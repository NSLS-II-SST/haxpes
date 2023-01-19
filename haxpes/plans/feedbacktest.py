from haxpes.ses import ses
from bluesky.plan_stubs import sleep, abs_set, mv
from bluesky.plans import count
from haxpes.hax_hw import fbvert, fbhor

def set_analyzer(filename):
    """sets analyzer settings and enters filename"""
    yield from mv(
        ses.center_en_sp, 1629,
        ses.width_en_sp, 20,
        ses.iterations, 5,
        ses.excitation_en, 2001,
        ses.pass_en, 50,
        ses.lens_mode, "Angular",
        ses.en_step, 50, 
        ses.region_name, "Ag3d",
        ses.filename, filename
    )

def run_test(iterations,sleep_time):
    yield from set_analyzer("Ag3d_FeedbackON_")
    for i in range(iterations):
        yield from count([ses],1)
        yield from sleep(sleep_time)
    yield from mv(fbvert.pidcontrol,0,fbhor.pidcontrol,0)
    yield from set_analyzer("Ag3d_FeedbackOFF_")
    for i in range(iterations):
        yield from count([ses],1)
        yield from sleep(sleep_time)
