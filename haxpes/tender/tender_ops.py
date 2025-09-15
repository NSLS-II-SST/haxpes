# from haxpes.hax_ops import set_analyzer
from haxpes.tender.funcs import (
    xalign_fs4,
    yalign_fs4_xps,
    xcoursealign_i0,
    ycoursealign_i0,
    xfinealign_i0,
    yfinealign_i0,
    stop_feedback,
    set_feedback,
    reset_feedback,
)
from bluesky.plan_stubs import mv, sleep, abs_set
from haxpes.devices.dcm_settings import dcmranges, offsetdict, gonilatdict, x2rolldict
from bluesky.plans import count
from haxpes.optimizers_test import find_max, find_centerofmass
from bluesky.plans import scan, rel_scan
from nbs_bl.hw import beamselection, gonilateral, psh1
from nbs_bl.utils import merge_func
from nbs_bl.plans.plan_stubs import set_exposure

from nbs_bl.help import add_to_plan_list

# from haxpes.scans import XPS_scan
from haxpes.plans.scans import XPSScan, SES_XPSScan
from haxpes.devices.peak_settings import analyzer_sets

#from bluesky.preprocessors import suspend_decorator
#from haxpes.hax_suspenders import suspendUS_tender, suspendHAX_tender, suspendFOE
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
from haxpes.hax_monitors import run_mode


def check_tender_beam(func):
    @merge_func(func)
    def wrapper(*args, **kwargs):
        if beamselection.get() != "Tender":
            raise RuntimeError(
                "Tender beam not enabled. Please run enable_tender_beam() first."
            )
        return (yield from func(*args, **kwargs))

    return wrapper


def set_crystal(crystalSP, roll_correct=1):
    dcm = bl["mono"]
    yield from mv(dcm.crystal, crystalSP)
    inpos = dcm.crystalstatus.get()
    if inpos == 0:
        yield from psh1.close()
        yield from mv(dcm.x2roll, x2rolldict[crystalSP])
        yield from mv(dcm.bragg.user_offset, offsetdict[crystalSP])
        yield from mv(gonilateral, gonilatdict[crystalSP])
        yield from psh1.open()


####
@add_to_plan_list
#@suspend_decorator(suspendUS_tender)
@check_tender_beam
def tune_x2pitch():
    """
    Tunes second crystal rocking curve. Starts with broad scan, then narrows around max.
    """
    
    dm1 = bl["dm1"]

    #collect DM1 initial position; return to this position once scan is done
    dm1_initial_position = dm1.position
    if dm1_initial_position > 60.: #in case slightly above 60, which is the soft limit ... it happens ...
        dm1_initial_position = 60.
    print(f'Current DM1 position is {dm1_initial_position}.')

    if "Idm1" in bl.get_deferred_devices():
        Idm1 = bl.load_deferred_device("Idm1")
        defer_after = True
    else:
        Idm1 = bl['Idm1']
        defer_after = False
    x2pitch = bl["x2pitch"]

    yield from set_exposure(1.0)
    if run_mode.current_mode.get() != "Align":
        run_mode.current_mode.put("Align")
    yield from mv(dm1, 32)
    max_channel = Idm1.mean.name  # define channel for DM1 diode
    md = {"purpose": "alignment"}
    yield from find_max(
        scan, [Idm1], x2pitch, -2.25, -1, 30, max_channel=max_channel, md=md
    )
    yield from find_max(
        rel_scan,
        [Idm1],
        x2pitch,
        -0.075,
        0.075,
        30,
        max_channel=max_channel,
        md=md,
    )
    print(f'Returning DM1 to initial position {dm1_initial_position}')
    yield from mv(dm1,dm1_initial_position)
    if defer_after:
        bl.defer_device('Idm1')


@check_tender_beam
def run_XPS_tender(sample_list, close_shutter=False):

    psh2 = bl["psh2"]
    fs4 = bl["fs4"]
    en = bl["en"]
    #    if "ses" in bl.get_deferred_devices():
    #        ses = bl.load_deferred_device("ses")
    #    else:
    #        ses = bl["ses"]

    if run_mode.current_mode.get() != "XPS SES":
        run_mode.current_mode.put("XPS SES")
    yield from psh2.open()  # in case it is closed. It should be open.
    if close_shutter:
        yield from fs4.close()
    for i in range(sample_list.index):
        if sample_list.all_samples[i]["To Run"]:
            print("Moving to sample " + str(i))
            yield from sample_list.goto_sample(i)
            # set photon energy ...
            current_en = en.position
            if (
                current_en >= sample_list.all_samples[i]["Photon Energy"] + 0.05
                or current_en <= sample_list.all_samples[i]["Photon Energy"] - 0.05
            ):
                yield from set_photon_energy_tender(
                    sample_list.all_samples[i]["Photon Energy"]
                )
                yield from align_beam_xps()
            for region in sample_list.all_samples[i]["regions"]:
                sample_list.en_cal = sample_list.all_samples[i]["Photon Energy"]
                yield from fs4.open()  # in case it is closed ...
                yield from SES_XPSScan(
                    sample_list.all_samples[i]["File Prefix"],
                    region,
                    sample_list.en_cal,
                )
                if close_shutter:
                    yield from fs4.close()
        else:
            print("Skipping sample " + str(i))


@check_tender_beam
def run_peakXPS_tender(sample_list, close_shutter=False):

    psh2 = bl["psh2"]
    fs4 = bl["fs4"]
    en = bl["en"]

    if run_mode.current_mode.get() != "XPS Peak":
        run_mode.current_mode.put("XPS Peak")
    from haxpes.plans.scans import (
        XPS_scan,
    )  # import here for now, in case peak servers are not running

    yield from psh2.open()  # in case it is closed. It should be open.
    if close_shutter:
        yield from fs4.close()
    for i in range(sample_list.index):
        if sample_list.all_samples[i]["To Run"]:
            print("Moving to sample " + str(i))
            yield from sample_list.goto_sample(i)
            # set photon energy ...
            current_en = en.position
            if (
                current_en >= sample_list.all_samples[i]["Photon Energy"] + 0.05
                or current_en <= sample_list.all_samples[i]["Photon Energy"] - 0.05
            ):
                yield from set_photon_energy_tender(
                    sample_list.all_samples[i]["Photon Energy"]
                )
                yield from align_beam_xps()
            ansetname = sample_list.all_samples[i]["AnalyzerSettings"]
            for settingdict in analyzer_sets:
                if settingdict["name"] == ansetname:
                    anset = settingdict
            for region in sample_list.all_samples[i]["regions"]:
                # get filename ...
                fn = (
                    sample_list.all_samples[i]["File Prefix"]
                    + str(round(sample_list.all_samples[i]["Photon Energy"]))
                    + "eV_"
                    + region["Region Name"]
                )
                sample_list.en_cal = sample_list.all_samples[i]["Photon Energy"]
                yield from fs4.open()  # in case it is closed ...
                reg = sample_list.translate_peak_dictionary(region)
                if sample_list.all_samples[i]["File Comments"] != "":
                    reg["description"] = sample_list.all_samples[i]["File Comments"]
                iterations = region["Iterations"]
                #                yield from XPS_scan(reg, iterations, anset, export_filename=fn)
                yield from XPSScan(reg, anset, sweeps=iterations)
                if close_shutter:
                    yield from fs4.close()
        else:
            print("Skipping sample " + str(i))


@add_to_plan_list
@check_tender_beam
def set_photon_energy_tender(
    energySP, use_optimal_harmonic=True, use_optimal_crystal=True
):

    x2finepitch = bl["x2finepitch"]
    x2fineroll = bl["x2fineroll"]
    h = bl["h"]
    dcm = bl["mono"]
    en = bl["en"]
    dm1 = bl["dm1"]

    if run_mode.current_mode.get() != "Align":
        run_mode.current_mode.put("Align")
    yield from stop_feedback()
    yield from mv(x2finepitch, 0, x2fineroll, 0)
    if use_optimal_harmonic:
        for r in dcmranges:
            if r["energymin"] <= energySP < r["energymax"]:
                yield from mv(h, r["harmonic"])
    if use_optimal_crystal:
        for r in dcmranges:
            if r["energymin"] <= energySP < r["energymax"]:
                yield from set_crystal(r["crystal"])
    yield from mv(en, energySP)
    yield from tune_x2pitch()
    yield from mv(dm1, 60)


@add_to_plan_list
#@suspend_decorator(suspendUS_tender)
@check_tender_beam
def align_beam_xps(PlaneMirror=False):

    x2finepitch = bl["x2finepitch"]
    x2fineroll = bl["x2fineroll"]
    fs4 = bl["fs4"]
    dm1 = bl["dm1"]
    BPM4cent = bl["BPM4cent"]

    if run_mode.current_mode.get() != "Align":
        run_mode.current_mode.put("Align")
    yield from stop_feedback()
    yield from reset_feedback()  # resets permit latch in case shutter was closed
    yield from mv(x2finepitch, 0, x2fineroll, 0)
    if not PlaneMirror:
        yield from fs4.close()
        yield from mv(dm1, 60)
        yield from sleep(5.0)
        yield from BPM4cent.adjust_gain()
        yield from yalign_fs4_xps(spy=349)
        yield from xalign_fs4(spx=479)
    yield from fs4.open()
    yield from xcoursealign_i0()
    yield from ycoursealign_i0()
    yield from sleep(
        5.0
    )  # necessary to make sure pitch motor has disabled prior to using piezo
#    if not PlaneMirror:
#        yield from yfinealign_i0()
#        yield from xfinealign_i0()
#        yield from sleep(
#            5.0
#        )  # necessary to make sure roll motor has disabled prior to using piezo
#    yield from set_feedback("vertical", set_new_sp=True)
#    yield from set_feedback("horizontal", set_new_sp=True)

@add_to_plan_list
#@suspend_decorator(suspendUS_tender)
@check_tender_beam
def fine_align_beam():
    x2finepitch = bl["x2finepitch"]
    x2fineroll = bl["x2fineroll"]
    yield from yfinealign_i0()
    yield from xfinealign_i0()
    yield from set_feedback("vertical", set_new_sp=False)
    yield from set_feedback("horizontal", set_new_sp=False)



######## hexapod functions ########
# NOTE: individual functions do not get the suspend decorator ...


def optimizeL1():
    dm1 = bl["dm1"]
    if "Idm1" in bl.get_deferred_devices():
        Idm1 = bl.load_deferred_device("Idm1")
        defer_after = True
    else:
        Idm1 = bl['Idm1']
        defer_after = False
    L1 = bl["L1"]

    yield from set_exposure(1.0)
    yield from mv(dm1, 32)
    # TO DO: turn off feedback and zero
    max_channel = Idm1.mean.name  # define channel for DM1 diode
    md = {"purpose": "alignment"}
    yield from find_centerofmass(
        scan,
        [Idm1],
        L1.pitch,
        0.5,
        1.25,
        31,
        max_channel=max_channel,
        hexapod=True,
        md=md,
    )
    if defer_after:
        bl.defer_device('Idm1')


def optimizeL2():
    dm1 = bl["dm1"]
    if "Idm1" in bl.get_deferred_devices():
        Idm1 = bl.load_deferred_device("Idm1")
        defer_after = True
    else:
        Idm1 = bl['Idm1']
        defer_after = False
    L2AB = bl["L2AB"]

    yield from set_exposure(1.0)
    L2pitch = L2AB.pitch
    yield from mv(dm1, 32)
    # TO DO: turn off feedback and zero
    max_channel = Idm1.mean.name  # define channel for DM1 diode
    md = {"purpose": "alignment"}
    yield from find_centerofmass(
        scan,
        [Idm1],
        L2pitch,
        9,
        10.5,
        31,
        max_channel=max_channel,
        hexapod=True,
        md=md,
    )
    if defer_after:
        bl.defer_device('Idm1')


#@suspend_decorator(suspendUS_tender)
def setL1(stripe):

    x2finepitch = bl["x2finepitch"]
    x2fineroll = bl["x2fineroll"]
    L1 = bl["L1"]

    if run_mode.current_mode.get() != "Align":
        run_mode.current_mode.put("Align")
    yield from stop_feedback()
    yield from mv(x2finepitch, 0, x2fineroll, 0)
    if stripe == "gold" or stripe == "Au":
        y_sp = -16.25
    if stripe == "carbon" or stripe == "C":
        y_sp = 0
    if stripe == "nickel" or stripe == "Ni":
        y_sp = 16.25
    # TO DO:  error out if not proper stripe name
    yield from mv(L1.y, y_sp)  # only move y motor. Assume others are fine.
    yield from optimizeL1()


#@suspend_decorator(suspendUS_tender)
def setL2_plane(stripe):

    x2finepitch = bl["x2finepitch"]
    x2fineroll = bl["x2fineroll"]
    L2wedge = bl["L2wedge"]
    L2AB = bl["L2AB"]

    if run_mode.current_mode.get() != "Align":
        run_mode.current_mode.put("Align")
    # stop feedback and zero piezos:
    yield from stop_feedback()
    yield from mv(x2finepitch, 0, x2fineroll, 0)
    if stripe == "gold" or stripe == "Au":
        y_sp = 0
        roll_sp = 2
        x_sp = 1.9
    if stripe == "nickel" or stripe == "Ni":
        y_sp = -12.5
        roll_sp = 4.15
        x_sp = 1.9
    # TO DO:  error out if not proper stripe name
    yield from mv(L2wedge, -35)
    yield from mv(L2AB.y, y_sp)
    yield from mv(L2AB.x, x_sp)
    yield from mv(L2AB.roll, roll_sp)
    yield from optimizeL2()


#@suspend_decorator(suspendUS_tender)
def setL2_toroid(stripe):

    x2finepitch = bl["x2finepitch"]
    x2fineroll = bl["x2fineroll"]
    L2wedge = bl["L2wedge"]
    L2AB = bl["L2AB"]

    if run_mode.current_mode.get() != "Align":
        run_mode.current_mode.put("Align")
    # stop feedback and zero piezos:
    print("stopping feedback")
    yield from stop_feedback()
    yield from mv(x2finepitch, 0, x2fineroll, 0)
    print("collecting required information")
    if stripe == "gold" or stripe == "Au":
        y_sp = 0
        roll_sp = 22.25
        x_sp = 2.8
    if stripe == "nickel" or stripe == "Ni":
        y_sp = 12.5
        roll_sp = -16.5
        x_sp = 2.9
    # TO DO:  error out if not proper stripe name
    print("moving L2 wedge")
    yield from mv(L2wedge, 35)
    print("moving L2 hexapod")
    yield from mv(L2AB.y, y_sp)
    yield from mv(L2AB.x, x_sp)
    yield from mv(L2AB.roll, roll_sp)
    print("optimizing L2 pitch")
    yield from optimizeL2()
