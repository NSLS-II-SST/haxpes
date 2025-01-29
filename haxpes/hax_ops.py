from bluesky.plan_stubs import abs_set, mv, sleep
from bluesky.plans import count, rel_scan
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
from nbs_bl.help import add_to_plan_list
from nbs_bl.hw import beamselection
from .soft.soft_ops import set_photon_energy_soft
from .tender.tender_ops import set_photon_energy_tender


@add_to_plan_list
def set_photon_energy(energy, use_optimal_harmonic=True, use_optimal_crystal=True):
    """
    Optimize the photon energy for the current beam mode. Automatically determines
    whether to use the soft or tender beam settings.

    Parameters
    ----------
    energy : float
        The photon energy to set in eV.
    use_optimal_harmonic : bool, optional
        Whether to set the optimal harmonic for the current beam mode.
    use_optimal_crystal : bool, optional
        Whether to set the optimal crystal for the current beam mode.
    """
    if beamselection.get() == "Soft":
        yield from set_photon_energy_soft(energy, use_optimal_harmonic)
    elif beamselection.get() == "Tender":
        yield from set_photon_energy_tender(
            energy, use_optimal_harmonic, use_optimal_crystal
        )
    else:
        raise ValueError("Invalid beam mode for setting photon energy")


###


###
"""
Commented out below ...
def rough_align_beam_xps(full_align=1):
    from .devices.detectors import BPM4cent

    fs4 = bl["fs4"]
    dm1 = bl["dm1"]

    yield from stop_feedback()
    if full_align:
        print("Tuning second crystal rocking curve")
        yield from tune_x2pitch()
    print("Aligning beam on FS4")
    yield from mv(dm1, 60)
    yield from fs4.close()
    yield from sleep(5.0)
    yield from BPM4cent.adjust_gain()
    yield from yalign_fs4_xps(spy=153)
    yield from xalign_fs4(spx=368)
"""

###


def align_sample_xps(analyzer_KE, anset, optimization_parameter=10):
    """function for aligning sample x position with analyzer counts.
    optimization_paramter weights the centering of the detector image vs. intensity.
    it probably needs to be quite large to actually matter ... REQUIRES TESTING.
    Only works for PEAK analyzer, not for SES.
    """
    from haxpes.peak_analyzer import peak_analyzer
    from haxpes.optimizers_test import find_max

    sampx = bl["sampx"]
    peak_analyzer._getparameters()  # get current live values ...
    yield from mv(
        peak_analyzer.opt_par, optimization_parameter
    )  # set optimization parameter
    peak_analyzer.setfixedmode()
    peak_analyzer.set_exposure(1)  # set exposure time to 1s
    yield from mv(peak_analyzer.lens_mode, anset["lens mode"])
    yield from mv(peak_analyzer.pass_energy, anset["pass energy"])
    yield from mv(peak_analyzer.dwell_time, anset["dwell time"])
    yield from mv(peak_analyzer.acq_mode, anset["acquisition mode"])
    yield from mv(peak_analyzer.energy_center, analyzer_KE)
    md = {}
    md["purpose"] = "alignment"
    yield from find_max(
        rel_scan,
        [peak_analyzer],
        sampx,
        -1,
        1,
        41,
        max_channel="PeakAnalyzer_opt_val",
        md=md,
    )


###
