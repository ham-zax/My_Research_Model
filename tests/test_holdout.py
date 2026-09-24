import pytest

from mfsm_e001.data import DataError, normalize_bybit_message


def test_eth_message_rejected_at_adapter_boundary():
    message = {"topic": "publicTrade.ETHUSDT", "type": "snapshot", "ts": 1000,
               "data": [{"T": 1000, "s": "ETHUSDT", "S": "Buy", "v": "1", "p": "100", "i": "x"}]}
    with pytest.raises(DataError, match="sealed"):
        normalize_bybit_message(message, received_ms=1001, market="spot")
