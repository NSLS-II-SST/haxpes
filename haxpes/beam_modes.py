"""
Functions for managing HAXPES beam modes using deferred device loading.
"""

from nbs_bl.hw import beamselection, softbeamenable
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
from nbs_bl.help import add_to_func_list
import IPython

# tender_mode_devices = ["enpostender", "Idm1", "dm1", "nBPM", "I1"]
# soft_mode_devices = ["enpossoft", "dm4", "SlitAB", "M4Adrain"]


@add_to_func_list
def enable_tender_beam():
    """
    Enable tender beam mode by loading required devices.

    This includes:
    - Tender energy control devices
    - Tender beam diagnostic devices
    - Tender beam optics
    """
    # Load required devices
    print("Enabling tender beam mode")

    if beamselection.get() not in ["None", "Tender"]:
        print("Stopping.  " + beamselection.get() + " beam enabled.  Disable first.")
        return 0

    # devices_to_load = tender_mode_devices

    #ip = IPython.get_ipython()

    # Load each device

    bl.activate_mode("Tender")
    #from haxpes.tender.tender_ops import run_XPS_tender

    #ip.user_global_ns["run_XPS"] = run_XPS_tender
    print("Setting beamselection to Tender")
    beamselection.set("Tender")
    print("Tender beam mode enabled")
    bl.add_to_baseline("enpostender")
    print("Tender energy added to baseline")


@add_to_func_list
def disable_tender_beam():
    """
    Disable tender beam mode by unloading required devices.
    """
    #ip = IPython.get_ipython()
    print("Disabling tender beam mode")
    bl.deactivate_mode("Tender")
    # devices_to_defer = tender_mode_devices
    # for device in devices_to_defer:
    #     bl.defer_device(device)

    #ip.user_global_ns.pop("run_XPS", None)

    if beamselection.get() != "Tender":
        print(
            "Tender beam was not enabled. Currently "
            + beamselection.get()
            + " is enabled."
        )
    else:
        beamselection.set("None")
    print("Tender beam mode disabled")


@add_to_func_list
def enable_soft_beam():
    """
    Enable soft beam mode by loading required devices.
    """
    ip = IPython.get_ipython()
    print("Enabling soft beam mode")
    if beamselection.get() not in  ["None", "Soft"]:
        print("Stopping.  " + beamselection.get() + " beam enabled.  Disable first.")
        return 0
    if softbeamenable.get() != "HAXPES":
        print("HAXPES endstation not selected for soft beam.  Cannot enable.")
        return 0


    bl.activate_mode("Soft")
    #from haxpes.soft.soft_ops import run_XPS_soft
    #ip.user_global_ns["run_XPS"] = run_XPS_soft

    from haxpes.soft.getbeam import transfer_setup

    ip.user_global_ns["transfer_setup"] = transfer_setup
    beamselection.set("Soft")
    print("Soft beam mode enabled")
    bl.add_to_baseline("enpossoft")
    print("Soft energy added to baseline")


@add_to_func_list
def disable_soft_beam():
    """
    Disable soft beam mode by unloading required devices.
    """
    ip = IPython.get_ipython()
    print("Disabling soft beam mode")
    """
    devices_to_defer = soft_mode_devices
    for device in devices_to_defer:
        bl.defer_device(device)
    """
    bl.deactivate_mode("Soft")
    
    #ip.user_global_ns.pop("run_XPS", None)
    ip.user_global_ns.pop("transfer_setup", None)

    if beamselection.get() != "Soft":
        print(
            "Soft beam was not enabled. Currently "
            + beamselection.get()
            + " is enabled."
        )
    else:
        beamselection.set("None")
    print("Soft beam mode disabled")
