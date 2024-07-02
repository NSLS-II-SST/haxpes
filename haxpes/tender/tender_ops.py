from haxpes.hax_ops import set_analyzer
from haxpes.tender.funcs import xalign_fs4, yalign_fs4_xps, xcoursealign_i0, ycoursealign_i0, xfinealign_i0, yfinealign_i0, stop_feedback, set_feedback, reset_feedback
from bluesky.plan_stubs import mv, sleep
from haxpes.tender.motors import x2finepitch, x2fineroll, dm1, x2pitch, L1, L2AB, L2wedge
from haxpes.dcm_settings import dcmranges
from haxpes.energy_tender import en, h, U42, mono as dcm
from bluesky.plans import count
from haxpes.hax_hw import fs4, psh2
from haxpes.detectors import BPM4cent
from haxpes.tender.detectors import Idm1
from haxpes.ses import ses
from haxpes.optimizers_test import find_max, find_centerofmass
from bluesky.plans import scan, rel_scan

from bluesky.preprocessors import suspend_decorator
from haxpes.hax_suspenders import suspend_FEsh1, suspend_psh1, suspend_beamstat, suspend_psh2

suspendList = [suspend_FEsh1]
suspendList.append(suspend_psh1)
suspendList.append(suspend_beamstat)

####
@suspend_decorator(suspendList)
def tune_x2pitch():
    """
    Tunes second crystal rocking curve.  Starts with broad scan, then narrows around max.
    """
    yield from mv(dm1,32)
    max_channel = Idm1.mean.name #define channel for DM1 diode
    md = {}
    md["purpose"] = "alignment"
    yield from find_max(scan, [Idm1], x2pitch, -2.25, -1, 30, max_channel=max_channel,md=md)
    yield from find_max(rel_scan, [Idm1], x2pitch, -0.075, 0.075, 30, max_channel = max_channel,md=md)

###


@suspend_decorator(suspendList)
def run_XPS_tender(sample_list,close_shutter=False):
    yield from psh2.open() #in case it is closed.  It should be open.
    if close_shutter:
        yield from fs4.close()
    for i in range(sample_list.index):
        if sample_list.all_samples[i]["To Run"]:
            print("Moving to sample "+str(i))
            yield from sample_list.goto_sample(i)
            #set photon energy ...
            current_en = en.position
            if current_en >= sample_list.all_samples[i]["Photon Energy"]+0.05 or current_en <= sample_list.all_samples[i]["Photon Energy"]-0.05:
                yield from set_photon_energy_tender(sample_list.all_samples[i]["Photon Energy"])
                yield from align_beam_xps()
            for region in sample_list.all_samples[i]["regions"]:
                sample_list.en_cal = sample_list.all_samples[i]["Photon Energy"]
#                if region["Energy Type"] == "Binding":
#                    sample_list.calc_KE(region)
                yield from set_analyzer(sample_list.all_samples[i]["File Prefix"],region,sample_list.en_cal)
                yield from fs4.open() #in case it is closed ...
                yield from count([ses],1)
                if close_shutter:
                    yield from fs4.close()
        else:
            print("Skipping sample "+str(i))

@suspend_decorator(suspendList)
def set_photon_energy_tender(energySP,use_optimal_harmonic=True,use_optimal_crystal=True):
    ###for 
    yield from stop_feedback()
    yield from mv(x2finepitch,0,x2fineroll,0)
    if use_optimal_harmonic:
        for r in dcmranges:
            if r["energymin"] <= energySP < r["energymax"]:
                yield from mv(h,r["harmonic"])
    if use_optimal_crystal:
        for r in dcmranges:
            if r["energymin"] <= energySP < r["energymax"]:
                yield from dcm.set_crystal(r["crystal"])
    yield from mv(en,energySP)
    yield from tune_x2pitch()
    yield from mv(dm1,60)
    #yield from align_beam_xps
    
###
@suspend_decorator(suspendList)
def align_beam_xps(PlaneMirror=False):
    yield from stop_feedback()
    yield from reset_feedback() #resets permit latch in case shutter was closed
    yield from mv(x2finepitch,0,x2fineroll,0)
    if not PlaneMirror:
        yield from fs4.close()
        yield from mv(dm1,60)
        yield from sleep(5.0)
        yield from BPM4cent.adjust_gain()
        yield from yalign_fs4_xps(spy=349)
        yield from xalign_fs4(spx=468)
    yield from fs4.open()
    yield from xcoursealign_i0()
    yield from ycoursealign_i0()
    yield from sleep(5.0) #necessary to make sure pitch motor has disabled prior to using piezo
    if not PlaneMirror:
        yield from yfinealign_i0()
        yield from xfinealign_i0()
        yield from sleep(5.0) #necessary to make sure roll motor has disabled prior to using piezo
    yield from set_feedback("vertical",set_new_sp=False)
    yield from set_feedback("horizontal",set_new_sp=False)

######## hexapod functions ########
###NOTE: individual functions do not get the suspend decorator ...

###
def optimizeL1():
    yield from mv(dm1,32)
    #TO DO: turn off feedback and zero
    max_channel = Idm1.mean.name #define channel for DM1 diode
    md = {}
    md["purpose"] = "alignment"
    yield from find_centerofmass(scan, [Idm1], L1.pitch, 0.5,1.0,21,max_channel=max_channel,hexapod=True,md=md)

###
def optimizeL2():
    L2pitch = L2AB.pitch
    yield from mv(dm1,32)
    #TO DO: turn off feedback and zero
    max_channel = Idm1.mean.name #define channel for DM1 diode
    md = {}
    md["purpose"] = "alignment"
    yield from find_centerofmass(scan, [Idm1], L2pitch,9,10.5,31,max_channel=max_channel,hexapod=True,md=md)

###
@suspend_decorator(suspendList)
def setL1(stripe):
    #stop feedback and zero piezos:
    yield from stop_feedback()
    yield from mv(x2finepitch,0,x2fineroll,0)
    if stripe == "gold" or stripe == "Au":
        y_sp = -16.25
    if stripe == "carbon" or stripe == "C":
        y_sp = 0
    if stripe == "nickel" or stripe == "Ni":
        y_sp = 16.25
    #TO DO:  error out if not proper stripe name
    yield from mv(L1.y,y_sp) #only move y motor.  Assume others are fine.  
    yield from optimizeL1()

@suspend_decorator(suspendList)
def setL2_plane(stripe):
    #stop feedback and zero piezos:
    yield from stop_feedback()
    yield from mv(x2finepitch,0,x2fineroll,0)
    if stripe == "gold" or stripe == "Au":
        y_sp = 0
        roll_sp = 2
        x_sp = 1.9
    if stripe == "nickel" or stripe == "Ni":
        y_sp = -12.5
        roll_sp = 4.15
        x_sp = 1.9
    #TO DO:  error out if not proper stripe name
    yield from mv(L2wedge,-35)
    yield from mv(L2AB.y,y_sp)
    yield from mv(L2AB.x,x_sp)
    yield from mv(L2AB.roll,roll_sp)
    yield from optimizeL2()

@suspend_decorator(suspendList)
def setL2_toroid(stripe):
    #stop feedback and zero piezos:
    yield from stop_feedback()
    yield from mv(x2finepitch,0,x2fineroll,0)
    if stripe == "gold" or stripe == "Au":
        y_sp = 0
        roll_sp = 22.25
        x_sp = 2.8
    if stripe == "nickel" or stripe == "Ni":
        y_sp = 12.5
        roll_sp = -16.5
        x_sp = 4.8
    #TO DO:  error out if not proper stripe name
    yield from mv(L2wedge,35)
    yield from mv(L2AB.y,y_sp)
    yield from mv(L2AB.x,x_sp)
    yield from mv(L2AB.roll,roll_sp)
    yield from optimizeL2()
