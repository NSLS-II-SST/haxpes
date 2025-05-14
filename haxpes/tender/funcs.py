from haxpes.optimizers_test import find_max, find_sp
from bluesky.plan_stubs import mv
from bluesky.plans import scan, rel_scan
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl


def xalign_fs4(spx=448):
    """
    Tunes second crystal roll to align beam centroid at spx
    """
    fs4 = bl["fs4"]
    BPM4cent = bl["BPM4cent"]
    x2roll = bl["x2roll"]

    yield from fs4.close()
    xchannel = BPM4cent.centX.name
    md = {"purpose": "alignment"}
    yield from find_sp(
        rel_scan,
        [BPM4cent.centX],
        x2roll,
        -0.5,
        0.5,
        25,
        sp=spx,
        max_channel=xchannel,
        hysteresis_correct=True,
        md=md,
    )
    yield from find_sp(
        rel_scan,
        [BPM4cent.centX],
        x2roll,
        -0.1,
        0.1,
        25,
        sp=spx,
        max_channel=xchannel,
        hysteresis_correct=True,
        md=md,
    )


def yalign_fs4_xps(spy=326):
    """
    Tunes second crystal perpendicular offset to align beam centroid at spy.
    ONLY USE FOR PHOTOEMISSION. Motor will move to pre-defined position when
    scanning energy
    """
    fs4 = bl["fs4"]
    BPM4cent = bl["BPM4cent"]
    x2perp = bl["x2perp"]

    md = {"purpose": "alignment"}
    yield from fs4.close()
    ychannel = BPM4cent.centY.name
    delta = 0.1 * x2perp.position
    yield from find_sp(
        rel_scan,
        [BPM4cent.centY],
        x2perp,
        -delta,
        delta,
        25,
        sp=spy,
        max_channel=ychannel,
        hysteresis_correct=True,
        md=md,
    )
    delta = 0.02 * x2perp.position
    yield from find_sp(
        rel_scan,
        [BPM4cent.centY],
        x2perp,
        -delta,
        delta,
        25,
        sp=spy,
        max_channel=ychannel,
        hysteresis_correct=True,
        md=md,
    )


def ycoursealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal pitch motor.
    Assumes slits are in place for photoemission.
    """
    fs4 = bl["fs4"]
    I0 = bl["I0"]
    x2pitch = bl["x2pitch"]

    md = {"purpose": "alignment"}
    yield from mv(I0.exposure_time, steptime)
    yield from fs4.open()
    ychannel = I0.mean.name
    yield from find_max(
        rel_scan,
        [I0],
        x2pitch,
        -0.025,
        0.025,
        25,
        max_channel=ychannel,
        hysteresis_correct=True,
        invert=False, 
        md=md,
    )


def yfinealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal fine pitch piezomotor.
    Assumes slits are in place for photoemission.
    """
    fs4 = bl["fs4"]
    I0 = bl["I0"]
    x2finepitch = bl["x2finepitch"]

    md = {"purpose": "alignment"}
    yield from mv(I0.exposure_time, steptime)
    yield from fs4.open()
    ychannel = I0.mean.name
    yield from find_max(
        scan,
        [I0],
        x2finepitch,
        -10,
        10,
        41,
        max_channel=ychannel,
        hysteresis_correct=True,
        invert=False,
        md=md,
    )


def xcoursealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal roll motor with a course
    step.
    """
    fs4 = bl["fs4"]
    I0 = bl["I0"]
    x2roll = bl["x2roll"]

    md = {"purpose": "alignment"}
    yield from mv(I0.exposure_time, steptime)
    yield from fs4.open()
    xchannel = I0.mean.name
    yield from find_max(
        rel_scan,
        [I0],
        x2roll,
        -0.1,
        0.1,
        41,
        max_channel=xchannel,
        hysteresis_correct=True,
        invert=False,
        md=md,
    )


def xfinealign_i0(steptime=1):
    """
    Aligns the beam on I0 using the second crystal roll motor with a fine step.
    Assumes slits are in place.
    """
    fs4 = bl["fs4"]
    I0 = bl["I0"]
    x2fineroll = bl["x2fineroll"]

    md = {"purpose": "alignment"}
    yield from mv(I0.exposure_time, steptime)
    yield from fs4.open()
    xchannel = I0.mean.name
    yield from find_max(
        scan,
        [I0],
        x2fineroll,
        -25,
        25,
        51,
        max_channel=xchannel,
        hysteresis_correct=True,
        invert=False,
        md=md,
    )


def set_feedback(axis, set_new_sp=True):
    """
    Turns feedback axis on. If find_new_sp is True, then it grabs the current
    value and sets setpoint.
    """
    fbvert = bl["fbvert"]
    fbhor = bl["fbhor"]

    if axis == "vertical":
        if set_new_sp:
            vval = fbvert.lastinput.get()
            if vval <= 0.8 and vval >= -0.8:
                yield from mv(fbvert.setpoint, vval)
        yield from mv(fbvert.pidcontrol, 1)
    elif axis == "horizontal":
        if set_new_sp:
            hval = fbhor.lastinput.get()
            if hval <= 0.8 and hval >= -0.8:
                yield from mv(fbhor.setpoint, hval)
        yield from mv(fbhor.pidcontrol, 1)
    else:
        print("what????")


def stop_feedback():
    """
    Turns both feedbacks off.
    """
    fbvert = bl["fbvert"]
    fbhor = bl["fbhor"]

    yield from mv(fbvert.pidcontrol, 0)
    yield from mv(fbhor.pidcontrol, 0)


def reset_feedback():
    """
    Resets the latching permit.
    """
    fbvert = bl["fbvert"]
    fbhor = bl["fbhor"]

    yield from mv(fbvert.permitlatch, 1)
    yield from mv(fbhor.permitlatch, 1)
