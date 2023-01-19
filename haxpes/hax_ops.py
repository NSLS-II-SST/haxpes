from .motors import sampx, sampy, sampz, sampr, dm1, x2finepitch, x2fineroll, haxslt
from .ses import ses
from bluesky.plan_stubs import abs_set, mv, sleep
from bluesky.plans import count
from .hax_hw import fs4, psh2, gv10
from .funcs import tune_x2pitch, xalign_fs4, yalign_fs4_xps, xcoursealign_i0, ycoursealign_i0, xfinealign_i0, yfinealign_i0, stop_feedback, set_feedback
from .detectors import BPM4cent
from .dcm_settings import dcmranges
from .energy_tender import en, h, mono as dcm

def set_analyzer(filename,core_line):
    """ 
    ...
    """
    dstepsize = 50
    dlensmode = "Angular"
    dsteptime = 0.1
    dacqmode = "swept"
    yield from abs_set(ses.filename,filename)
    yield from abs_set(ses.region_name,core_line["Region Name"])
    yield from abs_set(ses.center_en_sp,core_line["center_en"])
    yield from abs_set(ses.width_en_sp,core_line["width"])
    yield from abs_set(ses.iterations,core_line["Iterations"])
    yield from abs_set(ses.pass_en,core_line["Pass Energy"])
    if "Excitation Energy" in core_line.keys():
        yield from abs_set(ses.excitation_en,core_line["Excitation Energy"])
    if "Step Size" in core_line.keys():
        yield from abs_set(ses.en_step,core_line["Step Size"])
    else:
        yield from abs_set(ses.en_step,dstepsize)
    if "Lens Mode" in core_line.keys():
        yield from abs_set(ses.lens_mode,core_line["Lens Mode"])
    else:
        yield from abs_set(ses.lens_mode,dlensmode)
    if "steptime" in core_line.keys():
        yield from abs_set(ses.steptime,core_line["steptime"])
    else:
        yield from abs_set(ses.steptime,dsteptime)
    if "acq_mode" in core_line.keys():
        yield from abs_set(ses.acq_mode,core_line["acq_mode"])
    else:
        yield from abs_set(ses.acq_mode,dacqmode)
        
def run_XPS_old(all_samples):
    """ 
    Runs samples from list "all_samples".  "all_samples" is a list of sample dictionaries.  Dictionaries MUST contain the following keys:
    x_position:  sampx position
    y_position:  sampy position
    z_position:  sampz position
    r_position:  sampr (theta) position
    cores:  list of core_line dictionaries.  See set_analyzer function for definition of core_line dictionaries.
Sample dictionary typicall contains a sample name as well, but as yet this is not used.
    """
    for sample in all_samples:
        yield from mv(
            sampx,sample["x_position"],
            sampy,sample["y_position"],
            sampz,sample["z_position"],
            sampr,sample["r_position"])
        for coreline in sample["cores"]:
            yield from set_analyzer(sample["file_name"],coreline)
            yield from fs4.open()
            yield from count([ses],1)
            yield from fs4.close()


def run_XPS(sample_list,close_shutter=False):
    yield from psh2.open() #in case it is closed.  It should be open.
    if close_shutter:
        yield from fs4.close()
    for i in range(sample_list.index):
        if sample_list.all_samples[i]["To Run"]:
            print("Moving to sample "+str(i))
            yield from sample_list.goto_sample(i)
            for region in sample_list.all_samples[i]["regions"]:
                yield from set_analyzer(sample_list.all_samples[i]["File Prefix"],region)
                yield from fs4.open() #in case it is closed ...
                yield from count([ses],1)
                if close_shutter:
                    yield from fs4.close()
        else:
            print("Skipping sample "+str(i))
    
###

def withdraw_bar(heating_stage=0,close_valves=1):
    if heating_stage:
        y_out = 435
    else:
        y_out = 535
    yield from mv(
        sampx,0,
        sampz,0,
        sampr,0
    )
    yield from mv(sampy,y_out)
    if close_valves:
        yield from psh2.close()
        yield from gv10.close()
        print("Please close manual valve GV9A")
        

###
def stop_SES():
    yield from mv(ses.stop_signal, 1)

###
def rough_align_beam_xps(full_align=1):
    yield from stop_feedback()
    if full_align:
        print("Tuning second crystal rocking curve")
        yield from tune_x2pitch()
    print("Aligning beam on FS4")
    yield from mv(dm1,60)
    yield from fs4.close()
    yield from sleep(5.0)
    yield from BPM4cent.adjust_gain()
    yield from yalign_fs4_xps(spy=153)
    yield from xalign_fs4(spx=368)

###
def set_photon_energy(energySP,use_optimal_harmonic=True,use_optimal_crystal=True):
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
    
###
def align_beam_xps(hslitsize=0.5,vslitsize=0.1):
    yield from stop_feedback()
    yield from mv(x2finepitch,0,x2fineroll,0)
    yield from tune_x2pitch()
    yield from fs4.close()
    yield from mv(dm1,60)
    yield from sleep(5.0)
    yield from BPM4cent.adjust_gain()
    yield from yalign_fs4_xps(spy=326)
    yield from xalign_fs4(spx=448)
    yield from mv(haxslt.hsize,1)
    yield from mv(haxslt.vsize,0.5)
    yield from ycoursealign_i0()
    yield from xcoursealign_i0()
    yield from ycoursealign_i0()
    yield from xcoursealign_i0()
    yield from mv(haxslt.hsize,hslitsize,haxslt.vsize,vslitsize)
#    yield from ycoursealign_i0()
    yield from sleep(5.0) #necessary to make sure pitch motor has disabled prior to using piezo
    yield from yfinealign_i0()
    yield from xfinealign_i0()
    yield from yfinealign_i0()
    yield from xfinealign_i0()
    yield from sleep(5.0) #necessary to make sure roll motor has disabled prior to using piezo
    yield from set_feedback("vertical",set_new_sp=False)
    yield from set_feedback("horizontal")
