"""Causal timing evidence must never certify an earlier or different epoch."""

from mfsm_e001.qualification import assess_timing_evidence


def evidence(epoch=2):
    utc = {'domain': 'independent_utc', 'reference': 'fixture_ntp',
           'upstream': 'fixture_stratum_1', 'sync_state': 'synchronized',
           'clock_epoch': epoch, 'request_wall_ns': 1_000, 'receipt_wall_ns': 1_100,
           'request_mono_ns': 5_000, 'receipt_mono_ns': 5_100,
           'offset_lower_ns': -10, 'offset_upper_ns': 10,
           'available_ns': 1_100, 'expires_ns': 2_000,
           'max_drift_ns': 1, 'provenance': 'synthetic_fixture'}
    delay = {'domain': 'websocket_role_bound', 'role': 'binance_spot_depth',
             'clock_epoch': epoch, 'contract_id': 'fixture_contract',
             'max_delivery_delay_ns': 100, 'max_clock_error_ns': 10,
             'available_ns': 1_100, 'expires_ns': 2_000,
             'provenance': 'synthetic_fixture'}
    return utc, delay


def test_synthetic_timing_evidence_qualifies_only_after_availability():
    utc, delay = evidence()
    kwargs = {'utc_records': [utc], 'delay_records': [delay],
              'roles': ('binance_spot_depth',), 'clock_epoch': 2,
              'supported_contracts': {'binance_spot_depth': 'fixture_contract'},
              'synthetic_fixture': True, 'max_utc_error_ns': 20,
              'max_total_delay_ns': 200}
    assert assess_timing_evidence(boundary_ns=1_099, **kwargs)['state'] == 'unknown'
    qualified = assess_timing_evidence(boundary_ns=1_500, **kwargs)
    assert qualified['state'] == 'qualified'
    assert qualified['source_delay_bound_ns'] == 110
    assert assess_timing_evidence(boundary_ns=2_001, **kwargs)['state'] == 'expired'


def test_wrong_domain_epoch_and_unapproved_contract_fail_closed():
    utc, delay = evidence()
    args = {'boundary_ns': 1_500, 'roles': ('binance_spot_depth',),
            'supported_contracts': {'binance_spot_depth': 'fixture_contract'},
            'synthetic_fixture': True, 'max_utc_error_ns': 20,
            'max_total_delay_ns': 200}
    assert assess_timing_evidence(utc_records=[{**utc, 'domain': 'http_exchange_clock'}],
                                  delay_records=[delay], clock_epoch=2, **args)['state'] == 'unknown'
    assert assess_timing_evidence(utc_records=[utc], delay_records=[delay],
                                  clock_epoch=3, **args)['state'] == 'unknown'
    assert assess_timing_evidence(utc_records=[utc], delay_records=[{**delay, 'contract_id': 'other'}],
                                  clock_epoch=2, **args)['state'] == 'unknown'
    assert assess_timing_evidence(utc_records=[utc], delay_records=[delay],
                                  clock_epoch=2, synthetic_fixture=False,
                                  **{k: v for k, v in args.items() if k != 'synthetic_fixture'})['state'] == 'unknown'


def test_malformed_or_contradictory_evidence_is_quarantined():
    utc, delay = evidence()
    result = assess_timing_evidence(
        boundary_ns=1_500, utc_records=[{**utc, 'offset_lower_ns': 20}],
        delay_records=[delay], roles=('binance_spot_depth',), clock_epoch=2,
        supported_contracts={'binance_spot_depth': 'fixture_contract'},
        synthetic_fixture=True, max_utc_error_ns=20, max_total_delay_ns=200)
    assert result['state'] == 'quarantined'
    assert 'contradictory_utc_interval' in result['reasons']
    result = assess_timing_evidence(
        boundary_ns=1_500, utc_records=[{**utc, 'available_ns': 'not-a-time'}],
        delay_records=[delay], roles=('binance_spot_depth',), clock_epoch=2,
        supported_contracts={'binance_spot_depth': 'fixture_contract'},
        synthetic_fixture=True, max_utc_error_ns=20, max_total_delay_ns=200)
    assert result['state'] == 'quarantined'
