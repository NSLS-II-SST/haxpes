from nbs_bl.help import add_to_plan_list
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl

from bluesky.plan_stubs import mv 

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
