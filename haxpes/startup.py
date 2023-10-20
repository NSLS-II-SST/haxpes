#from .energy import dcm, u42gap
from .detectors import I0, Idrain, HAXDetectors
from .motors import sampx, sampy, sampz, sampr
from .ses import ses
from bluesky.plans import count, scan, rel_scan
from bluesky.plan_stubs import mv, sleep
#from bluesky import RunEngine
from .hax_runner import RE
from bluesky.callbacks import LiveTable
#from .hax_ops import run_XPS, align_beam_xps #####
from .sample_handling import sample_list
from .hax_suspenders import suspend_FEsh1, suspend_beamstat
#from .energy_tender import mono,en,h,U42
#from .funcs import tune_x2pitch
from .enabler import enable_soft_beam, enable_tender_beam, disable_soft_beam, disable_tender_beam, enable_both_beams, disable_both_beams, beamselection, enable_test_mode, disable_test_mode

LiveTable._FMT_MAP['number'] = 'g'

I0.set_exposure(1)
Idrain.set_exposure(1)
#Idm1.set_exposure(1)

#common suspenders:
#RE.install_suspender(suspend_FEsh1)
#RE.install_suspender(suspend_beamstat)

#by default, start in tender mode:
enable_tender_beam()
