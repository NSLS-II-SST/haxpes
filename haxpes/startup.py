from .energy import dcm, u42gap
from .detectors import dm4_i400
from bluesky.plans import count, scan, rel_scan
from bluesky.plan_stubs import mv
from bluesky import RunEngine
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.callbacks import LiveTable
import databroker

RE = RunEngine(call_returns_result=True)
LiveTable._FMT_MAP['number'] = 'g'
# All of this will go away once Dan A. makes a proper databroker
db = databroker.temp()
bec = BestEffortCallback()
RE.subscribe(bec)
RE.subscribe(db.insert)
