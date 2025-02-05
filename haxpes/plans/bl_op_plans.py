from nbs_bl.help import add_to_plan_list
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl

from bluesky.plan_stubs import mv, abs_set, sleep as bsleep

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
    
