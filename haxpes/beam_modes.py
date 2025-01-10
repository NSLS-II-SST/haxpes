"""
Functions for managing HAXPES beam modes using deferred device loading.
"""

from nbs_bl.beamline import GLOBAL_BEAMLINE as bl


def enable_tender_beam():
    """
    Enable tender beam mode by loading required devices.

    This includes:
    - Tender energy control devices
    - Tender beam diagnostic devices
    - Tender beam optics
    """
    # Load required devices
    devices_to_load = [
        "enpostender",
    ]

    # Load each device
    for device in devices_to_load:
        if bl.is_device_deferred(device):
            print(f"Loading {device}...")
            bl.load_deferred_device(device)
        else:
            print(f"{device} already loaded")

    print("Tender beam mode enabled")
