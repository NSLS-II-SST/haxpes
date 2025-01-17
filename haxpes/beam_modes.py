"""
Functions for managing HAXPES beam modes using deferred device loading.
"""

from nbs_bl.hw import beamselection, softbeamenable
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
import IPython

tender_mode_devices = ["enpostender", "Idm1", "dm1", "nBPM", "I1"]
soft_mode_devices = ["enpossoft", "dm4", "SlitAB", "M4Adrain"]

def enable_tender_beam():
    """
    Enable tender beam mode by loading required devices.

    This includes:
    - Tender energy control devices
    - Tender beam diagnostic devices
    - Tender beam optics
    """
    # Load required devices
    if beamselection.get() != "none":
        print("Stopping.  " + beamselection.get() + " beam enabled.  Disable first.")
        return 0

    devices_to_load = tender_mode_devices
 
    ip = IPython.get_ipython()

    # Load each device
    for device in devices_to_load:
        if bl.is_device_deferred(device):
            print(f"Loading {device}...")
            bl.load_deferred_device(device, ns=ip.user_global_ns)
        else:
            print(f"{device} already loaded")

    from haxpes.tender.tender_ops import set_photon_energy_tender, run_XPS_tender

    ip.user_global_ns["set_photon_energy"] = set_photon_energy_tender
    ip.user_global_ns["run_XPS"] = run_XPS_tender
    beamselection.set("Tender")
    print("Tender beam mode enabled")


def disable_tender_beam():
    """
    Disable tender beam mode by unloading required devices.
    """
    ip = IPython.get_ipython()
    if beamselection.get() != "Tender":
        print(
            "Stopping. Tender beam not enabled. Currently "
            + beamselection.get()
            + " is enabled."
        )
        return 0
    beamselection.set("none")
    print("Tender beam mode disabled")
    devices_to_defer = tender_mode_devices
    for device in devices_to_defer:
        bl.defer_device(device)

    ip.user_global_ns.pop("set_photon_energy", None)
    ip.user_global_ns.pop("run_XPS", None)


def enable_soft_beam():
    """
    Enable soft beam mode by loading required devices.
    """
    ip = IPython.get_ipython()
    

    if beamselection.get() != "none":
        print("Stopping.  " + beamselection.get() + " beam enabled.  Disable first.")
        return 0
    if softbeamenable.get() != "HAXPES":
        print("HAXPES endstation not selected for soft beam.  Cannot enable.")
        return 0
    devices_to_load = soft_mode_devices
    for device in devices_to_load:
        if bl.is_device_deferred(device):
            print(f"Loading {device}...")
            bl.load_deferred_device(device, ns=ip.user_global_ns)
        else:
            print(f"{device} already loaded")

    from haxpes.soft.soft_ops import set_photon_energy_soft, run_XPS_soft

    ip.user_global_ns["set_photon_energy"] = set_photon_energy_soft
    ip.user_global_ns["run_XPS"] = run_XPS_soft

    from haxpes.soft.getbeam import transfer_setup

    ip.user_global_ns["transfer_setup"] = transfer_setup
    beamselection.set("Soft")
    print("Soft beam mode enabled")


def disable_soft_beam():
    """
    Disable soft beam mode by unloading required devices.
    """
    ip = IPython.get_ipython()
    if beamselection.get() != "Soft":
        print(
            "Stopping. Soft beam not enabled. Currently "
            + beamselection.get()
            + " is enabled."
        )
        return 0

    devices_to_defer = soft_mode_devices
    for device in devices_to_defer:
        bl.defer_device(device)

    ip.user_global_ns.pop("set_photon_energy", None)
    ip.user_global_ns.pop("run_XPS", None)
    ip.user_global_ns.pop("transfer_setup", None)

    beamselection.set("none")
    print("Soft beam mode disabled")
