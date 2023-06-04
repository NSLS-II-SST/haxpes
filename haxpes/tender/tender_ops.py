from haxpes.hax_ops import set_analyzer
from haxpes.tender.funcs import tune_x2pitch, xalign_fs4, yalign_fs4_xps, xcoursealign_i0, ycoursealign_i0, xfinealign_i0, yfinealign_i0, stop_feedback, set_feedback
from bluesky.plan_stubs import mv, sleep
from haxpes.tender.motors import x2finepitch, x2fineroll, dm1
from haxpes.dcm_settings import dcmranges
from haxpes.energy_tender import en, h, U42, mono as dcm
from bluesky.plans import count
from haxpes.hax_hw import fs4, psh2
from haxpes.detectors import BPM4cent
from haxpes.ses import ses

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
def align_beam_xps():
    yield from stop_feedback()
    yield from mv(x2finepitch,0,x2fineroll,0)
 #   yield from tune_x2pitch()
    yield from fs4.close()
    yield from mv(dm1,60)
    yield from sleep(5.0)
    yield from BPM4cent.adjust_gain()
    yield from yalign_fs4_xps(spy=326)
    yield from xalign_fs4(spx=427)
    yield from fs4.open()
#    yield from mv(haxslt.hsize,1)
#    yield from mv(haxslt.vsize,1)
#    yield from ycoursealign_i0()
    yield from xcoursealign_i0()
    yield from ycoursealign_i0()
#    yield from xcoursealign_i0()
#    yield from mv(haxslt.hsize,hslitsize,haxslt.vsize,vslitsize)
#    yield from ycoursealign_i0()
    yield from sleep(5.0) #necessary to make sure pitch motor has disabled prior to using piezo
    yield from yfinealign_i0()
    yield from xfinealign_i0()
#    yield from yfinealign_i0()
#    yield from xfinealign_i0()
    yield from sleep(5.0) #necessary to make sure roll motor has disabled prior to using piezo
    yield from set_feedback("vertical",set_new_sp=False)
    yield from set_feedback("horizontal",set_new_sp=False)
