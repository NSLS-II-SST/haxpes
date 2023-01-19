from haxpes.sample_handling import sample_list
from haxpes.hax_ops import run_XPS
from haxpes.energy_tender import en,h
from bluesky.plan_stubs import mv
from haxpes.hax_ops import align_beam_xps
from haxpes.energy_tender import dcm
####### look at imports ...


def runthemacro():  

    f3000 = "/home/xf07id1/Documents/UserFiles/live/SampleList_3000.xls"
    f4000 = "/home/xf07id1/Documents/UserFiles/live/SampleList_4000.xls"
    f5000 = "/home/xf07id1/Documents/UserFiles/live/SampleList_5000.xls"
    f6000 = "/home/xf07id1/Documents/UserFiles/live/SampleList_6000.xls"

    ##
    yield from mv(h,3)
    yield from mv(en,3000)
    yield from align_beam_xps(hslitsize=-0.06,vslitsize=-0.03)

    S = sample_list()

    S.en_cal = 3000.5
    S.read_from_file(f3000)

    yield from run_XPS(S)

    yield from dcm.set_crystal("Si(220)")

    ##
    yield from mv(en,4000)
    yield from align_beam_xps(hslitsize=-0.06,vslitsize=-0.03)

    S = sample_list()

    S.en_cal = 4000.9
    S.read_from_file(f4000)

    yield from run_XPS(S)

    ##
    yield from mv(h,5)
    yield from mv(en,5000)
    yield from align_beam_xps(hslitsize=-0.06,vslitsize=-0.03)

    S.en_cal = 5000.3
    S.read_from_file(f5000)

    yield from run_XPS(S)

    ##
    yield from mv(en,6000)
    yield from align_beam_xps(hslitsize=-0.06,vslitsize=-0.03)

    S.en_cal = 5999.9
    S.read_from_file(f6000)

    yield from run_XPS(S)

    ##
