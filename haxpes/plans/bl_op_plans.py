from nbs_bl.help import add_to_plan_list
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
from nbs_bl.plans.plan_stubs import set_exposure

from bluesky.plan_stubs import mv, abs_set, sleep as bsleep
from bluesky_live.bluesky_run import BlueskyRun, DocumentCache
from bluesky.plans import count
from bluesky.preprocessors import subs_decorator

import numpy as np

@add_to_plan_list
def close_shutter(shutter: str = "psh2"):
    shutter = bl[shutter]
    yield from shutter.close()

@add_to_plan_list
def open_shutter(shutter: str = "psh2"):
    shutter = bl[shutter]
    yield from shutter.open()

@add_to_plan_list
def insert_filter():
    nBPM = bl['nBPM']
    yield from mv(nBPM,0)

@add_to_plan_list
def remove_filter():
    nBPM = bl['nBPM']
    yield from mv(nBPM,16)

@add_to_plan_list
def FG_on(energy: float = 11, Vgrid: float = 75, delay_seconds: float = 10):
    FG = bl['floodgun']
    FG.startup()
    FG.set_Vgrid(Vgrid)
    FG.set_energy(energy)
    yield from bsleep(delay_seconds)

@add_to_plan_list
def set_FG(energy: float = 11, Vgrid: float = 75, delay_seconds: float = 10):
    FG = bl['floodgun']
    FG.set_Vgrid(Vgrid)
    FG.set_energy(energy)
    yield from bsleep(delay_seconds)

@add_to_plan_list
def FG_off(delay_seconds: float = 10):
    FG = bl['floodgun']
    FG.shutdown()
    yield from bsleep(delay_seconds)

@add_to_plan_list
def withdraw_samplebar(y_out: float = 535):
    manip = bl['manipulator']
    yield from mv(manip.x,0,manip.z,0,manip.r,0)
    yield from mv(manip.y,y_out)
    low_lim = y_out - 0.1 #seems to be needed
    manip.y.set_lim(low_lim,manip.y.high_limit)

@add_to_plan_list
def measure_offsets(shutter: str = "psh2", n_counts: int = 10):
    """take dark counts and set detector offsets"""
    dc = DocumentCache()

    shutter = bl[shutter]

    @subs_decorator(dc)
    def inner():
        yield from set_exposure(1.)

        if shutter.status() == "open":
            openAfter = True
            yield from shutter.close()
        else:
            openAfter = False

        # Clear offsets first
        for det in bl.detectors.active:
            detname = det.name
            if hasattr(det, "offset"):
                det.offset.set(0).wait()
        
        yield from count(
            bl.detectors.active, n_counts, md={"scantype": "darkcounts"}
        )
        run = BlueskyRun(dc)
        table = run.primary.read()
        for det in bl.detectors.active:
            detname = det.name
            if hasattr(det, "offset"):
                dark_value = float(table[detname].mean().values)
                if np.isfinite(dark_value):
                    det.offset.set(dark_value).wait()

        if openAfter:
            yield from shutter.open()

    return (yield from inner())    

@add_to_plan_list
def setup_peakXAS(energy_center: float, pass_energy: int = 50, lens_mode: str = "Angular"):
    """setup peak analyzer in fixed mode for XAS"""
    
    peak_analyzer = bl.load_deferred_device("peak_analyzer")
    rdict = {"energy_center": energy_center}
    anset = {
        "pass_energy": pass_energy,
        "lens_mode": lens_mode
        }
    peak_analyzer.setup_from_dictionary(rdict,anset,"XAS")
    yield None


