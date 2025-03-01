from nbs_bl.hw import (
    I0,
    IK2600,
    sampx,
    sampy,
    sampz,
    sampr,
    floodgun,
    haxSMU,
    beamselection,
)
from bluesky.plans import count, scan, list_scan
from nbs_bl.plans.scans import nbs_count
from nbs_bl.utils import merge_func
from nbs_bl.help import add_to_scan_list
from nbs_bl.plans.plan_stubs import set_exposure
from nbs_bl.plans.scan_decorators import wrap_scantype
from bluesky.preprocessors import suspend_decorator
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
from haxpes.hax_monitors import run_mode
import numpy as np
from haxpes.hax_suspenders import suspendHAX_tender, suspendHAX_soft

#from haxpes.xpswriter import xpswrite_wrapper
#from haxpes.xaswriter import xaswrite_wrapper

# from haxpes.hax_suspenders import suspend_FEsh1, suspend_psh1, suspend_beamstat, suspend_psh2, suspend_fs4a
# suspendList = [suspend_FEsh1]
# suspendList.append(suspend_psh1)
# suspendList.append(suspend_beamstat)
# suspendList.append(suspend_psh2)
# suspendList.append(suspend_fs4a)

default_dwell_time = 0.1
default_lens_mode = "Angular"
default_acq_mode = "Image"

detector_widths = {"500": 40.0, "200": 16.0, "100": 8.0, "50": 4.0, "20": 1.6}


def estimate_time(region_dictionary, analyzer_settings, number_of_sweeps):
    if "dwell_time" in analyzer_settings.keys():
        dwelltime = analyzer_settings["dwell_time"]
    else:
        dwelltime = default_dwell_time
    num_points = (
        region_dictionary["energy_width"]
        + detector_widths[str(analyzer_settings["pass_energy"])]
    ) / region_dictionary["energy_step"]
    est_time = num_points * dwelltime
    print(
        "Estimated sweep time is "
        + str(est_time)
        + " s.  Setting I0 integration to "
        + str(est_time)
        + "."
    )
    print(
        "Estimated total time is " + str((est_time * number_of_sweeps) / 60) + " min."
    )
    return est_time

@suspend_decorator(suspendHAX_tender)
@add_to_scan_list
@wrap_scantype("xps")
@merge_func(nbs_count, use_func_name=False, omit_params=["extra_dets", "dwell"])
def XPSScan(region_dictionary, analyzer_settings, sweeps=1, **kwargs):
    print("loading peak")
    if "peak_analyzer" in bl.get_deferred_devices():
        peak_analyzer = bl.load_deferred_device('peak_analyzer')
    else:
        peak_analyzer = bl['peak_analyzer']
    print("setting up peak")
    peak_analyzer.setup_from_dictionary(region_dictionary, analyzer_settings, "XPS")
    print("setting up I0")
    est_time = estimate_time(region_dictionary, analyzer_settings, sweeps)
    I0initexp = I0.exposure_time.get()
    yield from set_exposure(est_time)
    print("run Peak")
    yield from nbs_count(sweeps, extra_dets=[peak_analyzer], **kwargs)
    print("resetting I0")
    yield from set_exposure(I0initexp)


#@suspend_decorator(suspendHAX_tender)
def SES_XPSScan(filename,core_line,en_cal):
    if "ses" in bl.get_deferred_devices():
        ses = bl.load_deferred_device("ses")
    else:
        ses = bl["ses"]
    ses.set_analyzer(filename,core_line,en_cal)
    yield from count([ses],1)


#@xpswrite_wrapper
@suspend_decorator(suspendHAX_tender)
def Peak_XPS_scan(
    region_dictionary,
    number_of_sweeps,
    analyzer_settings,
    export_filename=None,
    comments=None,
    calibrated_hv=None,
):

    if run_mode.current_mode.get() != "XPS Peak":
        run_mode.current_mode.put("XPS Peak")
   
    if "peak_analyzer" in bl.get_deferred_devices():
        peak_analyzer = bl.load_deferred_device('peak_analyzer')
    else:
        peak_analyzer = bl['peak_analyzer']

    en = bl['en']

    number_of_sweeps = int(number_of_sweeps)
    peak_analyzer.setup_from_dictionary(region_dictionary, analyzer_settings, "XPS")
    #    yield from setup_peak(region_dictionary,analyzer_settings,"XPS")
    est_time = estimate_time(region_dictionary, analyzer_settings, number_of_sweeps)
    I0initexp = I0.exposure_time.get()
    I0.set_exposure(est_time)

    # metadata for XPS scan:
    md = {}

    md["excitation energy"] = en.position
    md["purpose"] = "XPS Data"
    md["export filename"] = export_filename
    # input sample positions; note these should probably be put in generally.
    md["Sample X"] = sampx.position
    md["Sample Y"] = sampy.position
    md["Sample Z"] = sampz.position
    md["Sample Theta"] = sampr.position
    md["FG Energy"] = floodgun.energy.get()
    md["FG V_grid"] = floodgun.Vgrid.get()
    md["FG I_emit"] = floodgun.Iemis.get()
    if comments:
        md["Comments"] = comments
    if calibrated_hv:
        md["Calibrated Photon Energy"] = calibrated_hv

    yield from count([I0, peak_analyzer], number_of_sweeps, md=md)
    I0.set_exposure(I0initexp)  # reset I0 exposure time


def ResPES_scan(
    XPSregion,
    EnergyRegion,
    analyzer_settings,
    n_sweeps,
    export_filename=None,
    settle_time=0.5,
    comments=None,
):
    """performs resonance scan using PEAK analyzer.
    Currently records only peak analyzer and I0.
    TO DO: add other detectors
    Currently only performs 1 XPS sweep per energy.
    TODO: figure out multiple sweeps
    XPSregion is a dictionary which should contain keys "energy center", "energy width", "energy step", "region name".
    XPSregion has optional key "description" for sample comments but this can be left empty.
    analyzer_settings should be dictionary with keys "pass energy"
    analyzer_settings has optional keys "dwell time", "lens mode", and "acquisition mode.  These will default to default values if they are not set."
    EnergyRegion is a dictionary with keys:
    - n_regions (integer)
    - start_<n> where <n> is the region number starting from 0 for each region.
    - stop_<n> where <n> is the region number starting from 0 for each region.
    - step_<n> where <n> is the region number start from 0 for each region.
    """
    # first which beam and implement suspenders

    if beamselection.get() == "Tender":
        suspendList = suspendHAX_tender
    elif beamselection.get() == "Soft":
        suspendList = suspendHAX_soft
    elif beamselection.get() == "Soft & Tender":
        supendList = suspendHAX_soft + suspendHAX_tender
    else:
        suspendList = None
    # install suspenders

    @suspend_decorator(suspendList)
    def inner_function(*args, **kw_args):

        if run_mode.current_mode.get() != "ResPES":
            run_mode.current_mode.put("ResPES")
        from haxpes.peak_analyzer import peak_analyzer

        peak_analyzer.setup_from_dictionary(XPSregion, analyzer_settings, "XPS")
        est_time = estimate_time(XPSregion, analyzer_settings, 1)
        I0.set_exposure(est_time)
        fullrange = np.empty(
            0,
        )
        for reg in range(EnergyRegion["n_regions"]):
            start_energy = EnergyRegion["start_" + str(reg)]
            stop_energy = EnergyRegion["stop_" + str(reg)]
            step_size = EnergyRegion["step_" + str(reg)]
            reg_range = np.arange(start_energy, stop_energy, step_size)
            fullrange = np.concatenate((fullrange, reg_range), axis=0)
        en_list = fullrange.tolist()
        # medata
        md = {}
        md["purpose"] = "Resonant XPS Data"
        md["export_filename"] = export_filename
        md["Sample X"] = sampx.position
        md["Sample Y"] = sampy.position
        md["Sample Z"] = sampz.position
        md["Sample Theta"] = sampr.position
        md["FG Energy"] = floodgun.energy.get()
        md["FG V_grid"] = floodgun.Vgrid.get()
        md["FG I_emit"] = floodgun.Iemis.get()
        if comments:
            md["Comments"] = comments

        from bluesky.plan_stubs import (
            trigger_and_read,
            move_per_step,
            sleep as bs_sleep,
        )

        en = bl["en"]

        def per_step(detectors, step, pos_cache, take_readings=trigger_and_read):
            motors = step.keys()
            yield from move_per_step(step, pos_cache)
            yield from bs_sleep(settle_time)
            yield from take_readings(list(detectors) + list(motors))

        for sweep in range(n_sweeps):
            yield from list_scan(
                [I0, peak_analyzer], en, en_list, per_step=per_step, md=md
            )
        return

    yield from inner_function(
        XPSregion,
        EnergyRegion,
        analyzer_settings,
        n_sweeps,
        export_filename=export_filename,
        settle_time=settle_time,
        comments=comments,
    )


def XAS_setup(detector_list, exposure_time):
    for detector in detector_list:
        detector.set_exposure(exposure_time)
        print(
            "setting exposure time of "
            + detector.name
            + " to "
            + str(exposure_time)
            + " s."
        )


# def XAS_linscan(edge_dictionary,detector_list,exposure_time,n_sweeps=1):
#    """ performs XAS scan with a linear trajectory using settings in edge_dictionary.
#   edge_dictionary should have keys: start_energy, stop_energy, n_steps.
#    convert step size to number of steps elsewhere.
#   detector_list is list of detector objects.  They should all have function "set_exposure"
#    exposure_time is a float.
#    """
#    XAS_setup(detector_list,exposure_time)
#    for sweep in range(n_sweeps):
#        yield from scan(detector_list,en,edge_dictionary["start_energy"],\
# edge_dictionary["stop_energy"],edge_dictionary["n_steps"])


#@xaswrite_wrapper
def XAS_scan(
    edge_dictionary,
    detector_list,
    exposure_time,
    n_sweeps=1,
    settle_time=0.5,
    export_filename=None,
    comments=None,
):
    """peforms XAS scan with multiple regions
    edge_dictionary should have have keys:
    - n_regions (integer)
    - start_<n> where <n> is the region number starting from 0 for each region.
    - stop_<n> where <n> is the region number starting from 0 for each region.
    - step_<n> where <n> is the region number start from 0 for each region.
    """

    en = bl['en']

    if run_mode.current_mode.get() != "XAS":
        run_mode.current_mode.put("XAS")
    from bluesky.plan_stubs import trigger_and_read, move_per_step, sleep as bs_sleep

    def per_step(detectors, step, pos_cache, take_readings=trigger_and_read):
        motors = step.keys()
        yield from move_per_step(step, pos_cache)
        yield from bs_sleep(settle_time)
        yield from take_readings(list(detectors) + list(motors))

    # md to add: integration times
    md = {}
    md["purpose"] = "XAS Data"
    md["export_filename"] = export_filename
    if comments:
        md["Comments"] = comments
    md["FG Energy"] = floodgun.energy.get()
    md["FG V_grid"] = floodgun.Vgrid.get()
    md["FG I_emit"] = floodgun.Iemis.get()
    md["Sample X"] = sampx.position
    md["Sample Y"] = sampy.position
    md["Sample Z"] = sampz.position
    md["Sample Theta"] = sampr.position
    md["Applied Bias"] = haxSMU.VSource.get()

    fullrange = np.empty(
        0,
    )
    for reg in range(edge_dictionary["n_regions"]):
        start_energy = edge_dictionary["start_" + str(reg)]
        stop_energy = edge_dictionary["stop_" + str(reg)]
        step_size = edge_dictionary["step_" + str(reg)]
        reg_range = np.arange(start_energy, stop_energy, step_size)
        fullrange = np.concatenate((fullrange, reg_range), axis=0)
    en_list = fullrange.tolist()
    XAS_setup(detector_list, exposure_time)
    for sweep in range(n_sweeps):
        yield from list_scan(detector_list, en, en_list, per_step=per_step, md=md)
