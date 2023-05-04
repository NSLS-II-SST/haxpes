from haxpes.tender.motors import x2pitch, x2roll, x2perp, dm1, x2finepitch, x2fineroll
from haxpes.optimizers_test import find_max, find_sp, find_centerofmass
from haxpes.detectors import I0, BPM4cent
from haxpes.tender.detectors import Idm1
from bluesky.plan_stubs import mv, sleep
from bluesky.plans import scan, rel_scan
from haxpes.detectors import BPM4cent
from haxpes.hax_hw import fs4, psh2, fbvert, fbhor

####
def tune_x2pitch():
    """
    Tunes second crystal rocking curve.  Starts with broad scan, then narrows around max.
    """
    yield from mv(dm1,32)
    max_channel = Idm1.mean.name #define channel for DM1 diode
    yield from find_max(scan, [Idm1], x2pitch, -2.25, -1, 30, max_channel=max_channel)
    yield from find_max(rel_scan, [Idm1], x2pitch, -0.075, 0.075, 30, max_channel = max_channel)

###
def xalign_fs4(spx=448):
    """ 
    Tunes second crystal roll to align beam centroid at spx
    """
    yield from fs4.close()
    xchannel = BPM4cent.centX.name
    yield from find_sp(rel_scan,[BPM4cent], x2roll, -0.5,0.5,25, sp=spx, max_channel=xchannel,hysteresis_correct=True)
    yield from find_sp(rel_scan,[BPM4cent], x2roll, -0.1,0.1,25, sp=spx, max_channel=xchannel,hysteresis_correct=True)

###
def yalign_fs4_xps(spy=326):
    """
    Tunes second crystal perpendicular offset to align beam centroid at spy.  
    ONLY USE FOR PHOTOEMISSION.  Motor will move to pre-defined position when scanning energy
    """
    yield from fs4.close()
    ychannel = BPM4cent.centY.name
    delta = 0.1 * x2perp.position
    yield from find_sp(rel_scan,[BPM4cent],x2perp,-delta, delta, 25, sp=spy, max_channel=ychannel,hysteresis_correct=True)
    delta = 0.02 * x2perp.position
    yield from find_sp(rel_scan,[BPM4cent],x2perp,-delta, delta, 25, sp=spy, max_channel=ychannel,hysteresis_correct=True)

###
def ycoursealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal pitch motor.  
    Assumes slits are in place for photoemission.
    """
    yield from mv(I0.exposure_time,steptime)
    yield from fs4.open()
    ychannel = I0.mean.name
    yield from find_max(rel_scan,[I0],x2pitch,-0.025,0.025, 25, max_channel=ychannel,hysteresis_correct=True,invert=True)

def yfinealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal fine pitch piezomotor.  
    Assumes slits are in place for photoemission.
    """
    yield from mv(I0.exposure_time,steptime)
    yield from fs4.open()
    ychannel = I0.mean.name
    yield from find_max(scan,[I0],x2finepitch,-10,10,41, max_channel=ychannel,hysteresis_correct=True,invert=True)

###
def xcoursealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal roll motor with a course step.  
    """
    yield from mv(I0.exposure_time,steptime)
    yield from fs4.open()
    xchannel = I0.mean.name
    yield from find_max(rel_scan,[I0], x2roll, -0.1,0.1,41,  max_channel=xchannel,hysteresis_correct=True,invert=True)    

def xfinealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal roll motor with a fine step.  
    Assumes slits are in place.
    """
    yield from mv(I0.exposure_time,steptime)
    yield from fs4.open()
    xchannel = I0.mean.name
    yield from find_max(scan,[I0], x2fineroll, -25,25,51, max_channel=xchannel,hysteresis_correct=True,invert=True)

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
