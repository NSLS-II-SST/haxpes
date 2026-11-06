"""
PeakAnalyzerIOC against a running peak-ioc simulation IOC, over Channel
Access. Skipped unless peak-ioc is installed (it provides ``peak-sim-ioc``).

The IOC runs in a subprocess on its own port, so these tests do not see or
disturb other IOCs on the network.
"""

import os
import socket
import subprocess
import time

import pytest

pytest.importorskip("peak_ioc")

PREFIX = "PEAKTEST:"


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def ioc():
    port = _free_port()
    # pyepics reads these when it first starts, so set them before any import.
    os.environ.update(
        EPICS_CA_SERVER_PORT=str(port),
        EPICS_CAS_INTF_ADDR_LIST="127.0.0.1",
        EPICS_CA_ADDR_LIST="127.0.0.1",
        EPICS_CA_AUTO_ADDR_LIST="NO",
        EPICS_CA_MAX_ARRAY_BYTES="100000000",
    )
    proc = subprocess.Popen(
        ["peak-sim-ioc", "--time-scale", "0", "--prefix", PREFIX],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    yield proc
    proc.terminate()
    proc.wait(10)


@pytest.fixture
def analyzer(ioc):
    from haxpes.devices.peak_analyzer_ioc import PeakAnalyzerIOC

    analyzer = PeakAnalyzerIOC(PREFIX, name="PeakAnalyzer", timeout=30)
    analyzer.wait_for_connection(timeout=30)
    deadline = time.monotonic() + 30
    while analyzer.measurement_state.get() == "Disconnected":
        assert time.monotonic() < deadline, "sim IOC never connected"
        time.sleep(0.1)
    analyzer.accumulate.put("Off")
    analyzer.stop_live_mode()
    return analyzer


@pytest.fixture
def run_count():
    from bluesky import RunEngine
    from bluesky.plans import count

    RE = RunEngine({})

    def run(detectors, num=2):
        docs = []
        RE(count(detectors, num=num), lambda name, doc: docs.append((name, doc)))
        return docs

    return run


XPS_REGION = {"energy_center": 1999.5, "energy_step": 0.05, "energy_width": 5,
              "region_name": "Au4f",
              "description": "longer than a forty-character DBR_STRING. " * 2
              + "End"}
SETTINGS = {"pass_energy": 100, "lens_mode": "Transmission",
            "dwell_time": 0.2}


def test_xps_count_matches_old_document_keys(analyzer, run_count):
    analyzer.setup_from_dictionary(XPS_REGION, SETTINGS, "XPS")
    docs = run_count([analyzer])

    descriptor = next(doc for name, doc in docs if name == "descriptor")
    for key in ["total_counts", "xaxis", "edc", "yaxis", "y_CoM", "opt_val",
                "opt_par"]:
        assert f"PeakAnalyzer_{key}" in descriptor["data_keys"]
    assert "PeakAnalyzer_image" not in descriptor["data_keys"]
    assert descriptor["hints"]["PeakAnalyzer"]["fields"] == [
        "PeakAnalyzer_total_counts"]

    # The keys xpswriter.py reads.
    config = descriptor["configuration"]["PeakAnalyzer"]["data"]
    assert config["PeakAnalyzer_pass_energy"] == 100
    assert config["PeakAnalyzer_lens_mode"] == "Transmission"
    assert config["PeakAnalyzer_acq_mode"] == "Image"
    assert config["PeakAnalyzer_region_name"] == "Au4f"
    assert config["PeakAnalyzer_description"] == XPS_REGION["description"]
    assert config["PeakAnalyzer_dwell_time"] == 0.2
    assert config["PeakAnalyzer_scan_mode"] == "swept"

    events = [doc for name, doc in docs if name == "event"]
    assert len(events) == 2
    for event in events:
        data = event["data"]
        assert len(data["PeakAnalyzer_xaxis"]) == 101
        assert len(data["PeakAnalyzer_edc"]) == 101
        assert data["PeakAnalyzer_xaxis"][0] == pytest.approx(1997.0)
        assert data["PeakAnalyzer_total_counts"] == pytest.approx(
            sum(data["PeakAnalyzer_edc"]))
        assert data["PeakAnalyzer_total_counts"] > 0

    # unstage finished the measurement and powered down.
    assert analyzer.measure.get() == "Stop"
    assert analyzer.active.get() == "Off"


def test_each_trigger_gets_new_data(analyzer):
    analyzer.setup_from_dictionary(XPS_REGION, SETTINGS)
    analyzer.stage()
    try:
        counter = analyzer.array_counter.get()
        analyzer.trigger().wait(30)
        assert analyzer.array_counter.get() == counter + 1
        first = analyzer.edc.get()
        analyzer.trigger().wait(30)
        assert analyzer.array_counter.get() == counter + 2
        assert list(analyzer.edc.get()) != list(first)
    finally:
        analyzer.unstage()


def test_xas_setup_uses_fixed_mode(analyzer, run_count):
    analyzer.setup_from_dictionary({"energy_center": 2000, "region_name": "XAS"},
                                   {"pass_energy": 50}, scan_type="XAS")
    docs = run_count([analyzer], num=1)
    event = next(doc for name, doc in docs if name == "event")
    assert len(event["data"]["PeakAnalyzer_edc"]) == 500
    assert analyzer.scan_mode.get() == "fixed"


def test_unknown_scan_type(analyzer):
    with pytest.raises(ValueError):
        analyzer.setup_from_dictionary(XPS_REGION, SETTINGS, "UPS")


def test_alignment_style_moves(analyzer):
    """The calls hax_ops.align_sample_xps makes before its scan."""
    analyzer._getparameters()
    analyzer.opt_par.set(10).wait(10)
    analyzer.setfixedmode()
    analyzer.set_exposure(1)
    analyzer.lens_mode.set("Angular").wait(10)
    analyzer.pass_energy.set(200).wait(10)
    analyzer.energy_center.set(1999.5).wait(10)
    analyzer.stage()
    try:
        analyzer.trigger().wait(30)
        assert analyzer.opt_val.get() == pytest.approx(
            analyzer.total_counts.get() - 10 * abs(analyzer.y_CoM.get()))
        assert analyzer.exposure_time.get() == 1
    finally:
        analyzer.unstage()


def test_live_mode(analyzer):
    analyzer.set_live_pass_energy(20)  # ignored: not live
    assert analyzer.pass_energy.get() != 20
    analyzer.start_live_mode()
    assert analyzer._livemode
    analyzer.set_live_pass_energy(20)
    analyzer.set_live_energy_center(1990)
    assert analyzer.pass_energy.get() == 20
    analyzer.stop_live_mode()
    assert not analyzer._livemode
