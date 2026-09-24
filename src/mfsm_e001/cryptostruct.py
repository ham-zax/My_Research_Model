"""CryptoStruct receipt-time adapter for the separate E001 liquidity study.

The adapter preserves the frozen E001-LIQ-OBS liquidity definitions. It only
translates CryptoStruct's normalized full-depth snapshot/update/trade stream
into the existing top-level liquidity-state contract.
"""

from collections import deque
from decimal import Decimal
import io
import json
from pathlib import Path
import subprocess

from .liquidity_state import (
    NS, decision_liquidity_state, liquidity_model_features, top_level_book,
)


ZERO = Decimal(0)


class CryptoStructError(ValueError):
    pass


def open_cryptostruct_text(path):
    """Yield UTF-8 lines from a plain or zstd-compressed CryptoStruct day file."""
    path = Path(path)
    if path.suffix != '.zst':
        with path.open('r', encoding='utf-8') as stream:
            yield from stream
        return
    try:
        process = subprocess.Popen(
            ['zstd', '-dc', '--', str(path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError as exc:
        raise CryptoStructError('zstd executable is required for .zst input') from exc
    assert process.stdout is not None
    try:
        yield from io.TextIOWrapper(process.stdout, encoding='utf-8')
        code = process.wait()
        if code:
            error = (process.stderr.read().decode(errors='replace')[-500:]
                     if process.stderr else '')
            raise CryptoStructError(f'zstd decompression failed ({code}): {error}')
    finally:
        process.stdout.close()
        if process.stderr:
            process.stderr.close()
        if process.poll() is None:
            process.kill()
            process.wait()


def read_cryptostruct_header(path):
    for line in open_cryptostruct_text(path):
        header = json.loads(line)
        if not isinstance(header, dict) or 'instrument' not in header:
            raise CryptoStructError('invalid CryptoStruct header')
        return header
    raise CryptoStructError('empty CryptoStruct file')


def _parse_event(line):
    row = json.loads(line)
    if not isinstance(row, list) or not row:
        raise CryptoStructError('invalid CryptoStruct event')
    kind = row[0]
    if kind == 5:
        if len(row) < 5:
            raise CryptoStructError('invalid instrument-state event')
        return {
            'kind': kind, 'adapter_ns': int(row[2]), 'state': row[3],
            'message': row[4], 'previous_id': None, 'event_id': None,
            'exchange_ns': None, 'data': None,
        }
    if len(row) < 7:
        raise CryptoStructError('short CryptoStruct event')
    previous = row[2]
    return {
        'kind': kind, 'instrument_id': int(row[1]),
        'previous_id': None if previous in ('', '0', None) else str(previous),
        'event_id': str(row[3]), 'adapter_ns': int(row[4]),
        'exchange_ns': None if not row[5] else int(row[5]), 'data': row[6],
    }


def _validate_header(header):
    instrument = header['instrument']
    if instrument.get('code') != 'BTCUSDT':
        raise CryptoStructError('E001 CryptoStruct adapter requires BTCUSDT')
    if instrument.get('type') != 'perpetual':
        raise CryptoStructError('E001 liquidity adapter requires a perpetual contract')
    if instrument.get('exchange_code') != 'bybit':
        raise CryptoStructError('E001 liquidity adapter requires Bybit perpetual data')
    if instrument.get('is_inverse') or instrument.get('is_quanto'):
        raise CryptoStructError('only linear BTCUSDT contracts are supported')
    multiplier = Decimal(str(instrument.get('multiplier') or 0))
    if multiplier <= 0:
        raise CryptoStructError('invalid contract multiplier')
    return instrument, multiplier


def liquidity_feature_at(path, *, trigger_s, levels=50):
    """Replay one CryptoStruct perpetual day to one frozen t0+15s feature row.

    Receipt ordering uses adapterTs exactly as recorded. A regression in the
    model-relevant book/trade stream is rejected rather than sorted or
    backdated. Book or trade chain gaps invalidate dependent history.
    """
    if type(trigger_s) is not int:
        raise TypeError('trigger_s must be an integer UTC second')
    if type(levels) is not int or not 1 <= levels <= 50:
        raise ValueError('levels must be between 1 and 50')

    lines = open_cryptostruct_text(path)
    try:
        header = json.loads(next(lines))
    except StopIteration as exc:
        raise CryptoStructError('empty CryptoStruct file') from exc
    instrument, multiplier = _validate_header(header)
    instrument_id = int(instrument['id'])

    target_s = trigger_s + 15
    target_ns = target_s * NS
    first_state_s = trigger_s - 1800
    next_state_s = first_state_s

    bids = {}
    asks = {}
    states = {}
    observations = deque()
    trades = deque()
    book_epoch = 0
    book_ready = False
    book_suspect = True
    last_book_ns = None
    last_book_event_id = None
    last_trade_event_id = None
    last_trade_gap_ns = None
    last_relevant_adapter_ns = None
    book_chain_gaps = 0
    trade_chain_gaps = 0
    source_clock_leads = 0
    relevant_events = 0

    def view(boundary_us):
        if not book_ready or book_suspect:
            return {
                'top_level_valid': False,
                'reason': 'book_not_ready_or_suspect',
                'book_epoch': book_epoch,
            }
        return top_level_book(
            bids, asks, levels=levels, epoch=book_epoch,
            last_us=last_book_ns // 1000 if last_book_ns is not None else None,
            boundary_us=boundary_us)

    def sample(second):
        return view(second * 1_000_000)

    def emit_before(adapter_ns):
        nonlocal next_state_s
        while next_state_s <= target_s and next_state_s * NS < adapter_ns:
            states[next_state_s] = sample(next_state_s)
            next_state_s += 1

    for line in lines:
        event = _parse_event(line)
        kind = event['kind']
        if kind not in (0, 1, 2, 5):
            continue
        if kind != 5 and event.get('instrument_id') != instrument_id:
            raise CryptoStructError('instrument id changed inside day file')
        adapter_ns = event['adapter_ns']
        if kind in (0, 1, 2):
            relevant_events += 1
            if (last_relevant_adapter_ns is not None and
                    adapter_ns < last_relevant_adapter_ns):
                raise CryptoStructError(
                    'model-relevant adapterTs regressed; do not reorder historical events')
            last_relevant_adapter_ns = adapter_ns
            exchange_ns = event['exchange_ns']
            if exchange_ns is not None and exchange_ns > adapter_ns:
                source_clock_leads += 1
        emit_before(adapter_ns)
        if adapter_ns > target_ns and next_state_s > target_s:
            break

        if kind == 5:
            if event['state'] == 'ERROR':
                book_epoch += 1
                book_suspect = True
                book_ready = False
                observations.clear()
                trades.clear()
                last_trade_gap_ns = adapter_ns
                last_trade_event_id = None
            continue

        if kind == 0:
            book_epoch += 1
            bids.clear()
            asks.clear()
            for side, price_raw, qty_raw, *_ in event['data']:
                price, qty = Decimal(str(price_raw)), Decimal(str(qty_raw))
                if qty <= 0:
                    continue
                (bids if side == 0 else asks)[price] = qty * multiplier
            book_ready = bool(bids and asks)
            book_suspect = not book_ready
            last_book_ns = adapter_ns
            last_book_event_id = event['event_id']
            viewed = view(adapter_ns // 1000)
            observations.append({
                'event_ns': adapter_ns, 'available_ns': adapter_ns,
                'book_epoch': book_epoch, 'reset': True,
                'top_level_valid': viewed.get('top_level_valid', False),
                'top_bid_prices': viewed.get('top_bid_prices', ()),
                'top_ask_prices': viewed.get('top_ask_prices', ()),
                'bid_changes_known': True, 'changes': [],
            })
        elif kind == 1:
            if (last_book_event_id is not None and event['previous_id'] is not None
                    and event['previous_id'] != last_book_event_id):
                book_chain_gaps += 1
                book_epoch += 1
                book_suspect = True
                book_ready = False
                observations.clear()
            last_book_event_id = event['event_id']
            changes = []
            if not book_suspect:
                for side, price_raw, qty_raw, *_ in event['data']:
                    price = Decimal(str(price_raw))
                    target = bids if side == 0 else asks
                    old = target.get(price, ZERO)
                    new = Decimal(str(qty_raw)) * multiplier
                    if new <= 0:
                        target.pop(price, None)
                        new = ZERO
                    else:
                        target[price] = new
                    delta = new - old
                    if delta:
                        changes.append(('bid' if side == 0 else 'ask', price, delta))
                last_book_ns = adapter_ns
                book_ready = bool(bids and asks)
                viewed = view(adapter_ns // 1000)
                observations.append({
                    'event_ns': adapter_ns, 'available_ns': adapter_ns,
                    'book_epoch': book_epoch, 'reset': False,
                    'top_level_valid': viewed.get('top_level_valid', False),
                    'top_bid_prices': viewed.get('top_bid_prices', ()),
                    'top_ask_prices': viewed.get('top_ask_prices', ()),
                    'bid_changes_known': True, 'changes': changes,
                })
        elif kind == 2:
            if (last_trade_event_id is not None and event['previous_id'] is not None
                    and event['previous_id'] != last_trade_event_id):
                trade_chain_gaps += 1
                last_trade_gap_ns = adapter_ns
                trades.clear()
            last_trade_event_id = event['event_id']
            for row in event['data']:
                if len(row) < 3:
                    raise CryptoStructError('invalid trade row')
                side, price_raw, qty_raw = row[:3]
                price = Decimal(str(price_raw))
                base_qty = Decimal(str(qty_raw)) * multiplier
                trades.append({
                    'received_us': adapter_ns // 1000,
                    'side': 'buy' if side == 0 else 'sell',
                    'notional': price * base_qty,
                })

        while observations and observations[0]['event_ns'] < adapter_ns - 20 * NS:
            observations.popleft()
        while trades and trades[0]['received_us'] < adapter_ns // 1000 - 30_000_000:
            trades.popleft()

        if next_state_s <= target_s and next_state_s * NS == adapter_ns:
            states[next_state_s] = sample(next_state_s)
            next_state_s += 1

    while next_state_s <= target_s:
        states[next_state_s] = sample(next_state_s)
        next_state_s += 1

    measured = decision_liquidity_state(
        states, observations, trades, trigger_s=trigger_s, levels=levels)
    if (last_trade_gap_ns is not None and
            last_trade_gap_ns >= (target_s - 30) * NS):
        measured = {
            'valid': False, 'reason': 'trade_chain_gap_in_flow_window',
            'trigger_s': trigger_s, 'decision_s': target_s,
        }
    model = liquidity_model_features(measured)
    return {
        'schema': 'E001-CryptoStruct-feature-probe-1',
        'source': str(path),
        'instrument': {
            'id': instrument_id,
            'exchange_code': instrument.get('exchange_code'),
            'code': instrument.get('code'),
            'multiplier': str(multiplier),
        },
        'trigger_s': trigger_s,
        'decision_s': target_s,
        'relevant_events_processed': relevant_events,
        'book_chain_gaps': book_chain_gaps,
        'trade_chain_gaps': trade_chain_gaps,
        'source_clock_leads': source_clock_leads,
        'raw': measured,
        'shared': model['shared'],
        'mfsm': model['mfsm'],
        'feature_vector_ready': model['ready'],
        'primary_eligible': False,
        'model_ready': False,
    }
