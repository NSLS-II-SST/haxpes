"""
#from .energy import dcm, u42gap
from .detectors import I0, Idrain, IK2600
from .tender.detectors import I1
from .ses import ses
#from .hax_ops import run_XPS, align_beam_xps #####
from .sample_handling import sample_list
from .hax_suspenders import suspend_FEsh1, suspend_beamstat
#from .energy_tender import mono,en,h,U42
#from .funcs import tune_x2pitch
from .enabler import enable_soft_beam, enable_tender_beam, disable_soft_beam, disable_tender_beam, enable_both_beams, disable_both_beams, beamselection, enable_test_mode, disable_test_mode

LiveTable._FMT_MAP['number'] = 'g'
"""

from bluesky.plan_stubs import abs_set
import nbs_bl
from nbs_bl.hw import *
from nbs_bl.detectors import (
    list_detectors,
    activate_detector,
    deactivate_detector,
    activate_detector_set,
)
from nbs_bl.motors import list_motors
import nbs_bl.plans.scans
from nbs_bl.run_engine import setup_run_engine, create_run_engine
from nbs_bl.help import GLOBAL_IMPORT_DICTIONARY
from nbs_bl.plans.groups import group
from nbs_bl.queueserver import request_update, get_status
from nbs_bl.samples import list_samples
from nbs_bl.beamline import GLOBAL_BEAMLINE
from haxpes.beam_modes import (
    enable_tender_beam,
    enable_soft_beam,
    disable_tender_beam,
    disable_soft_beam,
)
from haxpes.tender.tender_ops import *
from haxpes.soft.soft_ops import *
from haxpes.plans.xps import XPSScan, load_xps

from haxpes.sample_handling import sample_list

S = sample_list()

from os import chdir

chdir("/home/xf07id1/Documents/UserFiles/live/LiveData")

for key in GLOBAL_IMPORT_DICTIONARY:
    if key not in globals():
        globals()[key] = GLOBAL_IMPORT_DICTIONARY[key]


print("HAXPES Main Startup")

RE = create_run_engine(setup=True)
# RE = setup_run_engine(RE)

if "redis" in GLOBAL_BEAMLINE.settings:
    import redis
    from nbs_bl.status import RedisStatusDict
    from nbs_bl.queueserver import GLOBAL_USER_STATUS

    redis_settings = GLOBAL_BEAMLINE.settings.get("redis").get("md")
    uri = redis_settings.get("host", "localhost")  # "info.sst.nsls2.bnl.gov"
    prefix = redis_settings.get("prefix", "")
    md = RedisStatusDict(redis.Redis(uri), prefix=prefix)
    GLOBAL_USER_STATUS.add_status("USER_MD", md)
    RE.md = md

RE(set_exposure(1.0))


"""
I0.set_exposure(1)
Idrain.set_exposure(1)
IK2600.set_exposure(1)
I1.set_exposure(1)

#common suspenders:
#RE.install_suspender(suspend_FEsh1)
#RE.install_suspender(suspend_beamstat)

#by default, start in tender mode:
enable_tender_beam()

from haxpes.getXASregionsfromfile import DefaultRegions

from haxpes.motors import haxslt

from haxpes.hax_hw import floodgun, haxSMU
haxSMU.set_voltage(0)
"""
