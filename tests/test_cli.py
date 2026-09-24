import json
import gzip
import os
from pathlib import Path
import subprocess
import sys
import zipfile


ENV = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}


def test_fixture_command_outputs_one_labeled_episode_without_real_data(tmp_path):
    output = tmp_path / "btc_fixture_result.json"
    completed = subprocess.run([sys.executable, "-m", "mfsm_e001.cli", "fixture",
                                "--output", str(output)], env=ENV, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    result = json.loads(output.read_text())
    assert result["provenance"] == "synthetic_fixture"
    assert result["events"] == [
        {"trigger_s": 301, "decision_s": 316, "accepted": True, "reason": "accepted"},
        {"trigger_s": 320, "decision_s": 335, "accepted": False, "reason": "episode_lockout"},
    ]
    assert result["primary_label"]["state"] == "downside-first"
    assert result["primary_label"]["value"] == 1
    assert result["mfsm_features"]["liquidation_pressure_ratio"] is None


def test_real_command_refuses_to_claim_confirmatory_data(tmp_path):
    completed = subprocess.run([sys.executable, "-m", "mfsm_e001.cli", "build-real",
                                "--output", str(tmp_path / "result.json")],
                               env=ENV, capture_output=True, text=True)
    assert completed.returncode != 0
    assert "audited" in completed.stderr.lower()


def test_public_archive_audit_reports_event_time_only(tmp_path):
    binance = tmp_path / "btc_binance.zip"
    bybit = tmp_path / "btc_bybit.csv.gz"
    output = tmp_path / "audit.json"
    with zipfile.ZipFile(binance, "w") as archive:
        archive.writestr("BTCUSDT-trades-2023-10-01.csv",
                             "1,100,0.2,20,1696118400000,False,True\n")
    with gzip.open(bybit, "wt") as stream:
        stream.write("id,timestamp,price,volume,side\n")
        stream.write("1,1696118400001,101,0.2,buy\n")
    result = subprocess.run([sys.executable, "-m", "mfsm_e001.cli", "audit-public",
                             "--binance", str(binance), "--bybit", str(bybit),
                             "--output", str(output)], env=ENV, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text())
    assert report["provenance"] == "archive_event_time_only"
    assert report["binance"]["records"] == 1
    assert report["bybit"]["records"] == 1
    assert report["binance"]["has_receipt_times"] is False


def test_tardis_audit_command_reports_receipt_time_sample(tmp_path):
    sample = tmp_path / "btc_tardis_bybit_trades.csv.gz"
    output = tmp_path / "tardis_audit.json"
    with gzip.open(sample, "wt") as stream:
        stream.write("exchange,symbol,timestamp,local_timestamp,id,side,price,amount\n")
        stream.write("bybit,BTCUSDT,1682899200000000,1682899200005100,1,buy,29233.5,0.01\n")
    result = subprocess.run([
        sys.executable, "-m", "mfsm_e001.cli", "audit-tardis",
        "--file", str(sample), "--data-type", "trades", "--exchange", "bybit",
        "--symbol", "BTCUSDT", "--output", str(output),
    ], env=ENV, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text())
    assert report["provenance"] == "tardis_normalized_csv_audit"
    assert report["sample"]["has_receipt_times"] is True
    assert report["sample"]["first_local_us"] == 1682899200005100
