from haxpes.tender.motors import x2pitch, x2roll, x2perp, dm1, x2finepitch, x2fineroll
from haxpes.optimizers_test import find_max, find_sp, find_centerofmass
from haxpes.detectors import I0, BPM4cent
from haxpes.tender.detectors import Idm1
from bluesky.plan_stubs import mv, sleep
from bluesky.plans import scan, rel_scan
from haxpes.detectors import BPM4cent
from haxpes.hax_hw import fs4, psh2, fbvert, fbhor


def xalign_fs4(spx=448):
    """ 
    Tunes second crystal roll to align beam centroid at spx
    """
    yield from fs4.close()
    xchannel = BPM4cent.centX.name
    md = {}
    md["purpose"] = "alignment"
    yield from find_sp(rel_scan,[BPM4cent], x2roll, -0.5,0.5,25, sp=spx, max_channel=xchannel,hysteresis_correct=True, md=md)
    yield from find_sp(rel_scan,[BPM4cent], x2roll, -0.1,0.1,25, sp=spx, max_channel=xchannel,hysteresis_correct=True, md=md)

###
def yalign_fs4_xps(spy=326):
    """
    Tunes second crystal perpendicular offset to align beam centroid at spy.  
    ONLY USE FOR PHOTOEMISSION.  Motor will move to pre-defined position when scanning energy
    """
    md = {}
    md["purpose"] = "alignment"
    yield from fs4.close()
    ychannel = BPM4cent.centY.name
    delta = 0.1 * x2perp.position
    yield from find_sp(rel_scan,[BPM4cent],x2perp,-delta, delta, 25, sp=spy, max_channel=ychannel,hysteresis_correct=True, md=md)
    delta = 0.02 * x2perp.position
    yield from find_sp(rel_scan,[BPM4cent],x2perp,-delta, delta, 25, sp=spy, max_channel=ychannel,hysteresis_correct=True, md=md)

###
def ycoursealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal pitch motor.  
    Assumes slits are in place for photoemission.
    """
    md = {}
    md["purpose"] = "alignment"
    yield from mv(I0.exposure_time,steptime)
    yield from fs4.open()
    ychannel = I0.mean.name
    yield from find_max(rel_scan,[I0],x2pitch,-0.025,0.025, 25, max_channel=ychannel,hysteresis_correct=True,invert=True, md=md)

def yfinealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal fine pitch piezomotor.  
    Assumes slits are in place for photoemission.
    """
    md = {}
    md["purpose"] = "alignment"
    yield from mv(I0.exposure_time,steptime)
    yield from fs4.open()
    ychannel = I0.mean.name
    yield from find_max(scan,[I0],x2finepitch,-10,10,41, max_channel=ychannel,hysteresis_correct=True,invert=True, md=md)

###
def xcoursealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal roll motor with a course step.  
    """
    md = {}
    md["purpose"] = "alignment"
    yield from mv(I0.exposure_time,steptime)
    yield from fs4.open()
    xchannel = I0.mean.name
    yield from find_max(rel_scan,[I0], x2roll, -0.1,0.1,41,  max_channel=xchannel,hysteresis_correct=True,invert=True, md=md)    

def xfinealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal roll motor with a fine step.  
    Assumes slits are in place.
    """
    md = {}
    md["purpose"] = "alignment"
    yield from mv(I0.exposure_time,steptime)
    yield from fs4.open()
    xchannel = I0.mean.name
    yield from find_max(scan,[I0], x2fineroll, -25,25,51, max_channel=xchannel,hysteresis_correct=True,invert=True, md=md)

###
def set_feedback(axis,set_new_sp=True):
    """
    Turns feedback axis on.  If find_new_sp is True, then it grabs the current value and sets  setpoint.
    """
    if axis == "vertical":
        if set_new_sp:
            vval = fbvert.lastinput.get()
            yield from mv(fbvert.setpoint,vval)
        yield from mv(fbvert.pidcontrol,1)
    elif axis == "horizontal":
        if set_new_sp:
            hval = fbhor.lastinput.get()
            yield from mv(fbhor.setpoint,hval)
        yield from mv(fbhor.pidcontrol,1)
    else:
        print("what????")
###
def stop_feedback():
    """
    Turns both feedbacks off.
    """
    yield from mv(fbvert.pidcontrol,0)
    yield from mv(fbhor.pidcontrol,0)

def reset_feedback():
    """
    Resets the latching permit.
    """
    yield from mv(fbvert.permitlatch,1)
    yield from mv(fbhor.permitlatch,1)

