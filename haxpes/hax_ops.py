from .motors import sampx, sampy, sampz, sampr, haxslt
from .tender.motors import dm1, x2finepitch, x2fineroll
from .ses import ses
from bluesky.plan_stubs import abs_set, mv, sleep
from bluesky.plans import count
from .hax_hw import fs4, psh2, gv10
#from .funcs import tune_x2pitch, xalign_fs4, yalign_fs4_xps, xcoursealign_i0, ycoursealign_i0, xfinealign_i0, yfinealign_i0, stop_feedback, set_feedback
from .detectors import BPM4cent
from .dcm_settings import dcmranges
from .energy_tender import en, h, mono as dcm

def set_analyzer(filename,core_line,en_cal):
    """ 
    ...
    """
    dstepsize = 50
    dlensmode = "Angular"
    dsteptime = 0.1
    dacqmode = "swept"
    yield from abs_set(ses.filename,filename)
    yield from abs_set(ses.region_name,core_line["Region Name"])
    if core_line["Energy Type"] == "Binding":
       cent = en_cal - core_line["center_en"]
       yield from abs_set(ses.center_en_sp,cent)
    else:
       yield from abs_set(ses.center_en_sp,core_line["center_en"])
#    yield from abs_set(ses.center_en_sp,core_line["center_en"]) ### BE correction.  Above 5 lines for testing, this one commented out.
    yield from abs_set(ses.width_en_sp,core_line["width"])
    yield from abs_set(ses.iterations,core_line["Iterations"])
    yield from abs_set(ses.pass_en,core_line["Pass Energy"])
    yield from abs_set(ses.excitation_en,en_cal) # added 2023-08-02; NOT TESTED YET CW
    print(en_cal)
#    if "Photon Energy" in core_line.keys():  #commented out 2023-08-02 CW
#        yield from abs_set(ses.excitation_en,core_line["Photon Energy"])  #commented out 2023-08-02 CW
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

