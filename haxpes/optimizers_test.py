from bluesky_live.bluesky_run import BlueskyRun, DocumentCache
import bluesky.preprocessors as bpp
#from .preprocessors import run_return_decorator
from bluesky.plan_stubs import mv, mvr, trigger_and_read
from bluesky.plans import count
import numpy as np


def find_max(plan, dets, *args, max_channel=None, invert=False, hysteresis_correct=False):
    """
    invert turns find_max into find_min
    """
    dc = DocumentCache()

    @bpp.subs_decorator(dc)
    def inner_maximizer():
        yield from plan(dets, *args)
        run = BlueskyRun(dc)
        table = run.primary.read()
        motor_names = run.metadata['start']['motors']
        motors = [m for m in args if getattr(m, 'name', None) in motor_names]
        if max_channel is None:
            detname = dets[0].name
        else:
            detname = max_channel
        if invert:
            max_idx = int(table[detname].argmin())
            print(f"Minimum found at step {max_idx} for detector {detname}")
        else:
            max_idx = int(table[detname].argmax())
            print(f"Maximum found at step {max_idx} for detector {detname}")
        ret = []
        for m in motors:
            max_val = float(table[m.name][max_idx])
            print(f"setting {m.name} to {max_val}")
            ret.append([m, max_val])
            if hysteresis_correct:
                sval = float(table[m.name][0])
                yield from mv(m, sval)
            yield from mv(m, max_val)
        return ret
    return (yield from inner_maximizer())

######################
def find_centerofmass(plan, dets, *args, max_channel=None, hysteresis_correct=False):

    dc = DocumentCache()

    @bpp.subs_decorator(dc)
    def inner_maximizer():
        yield from plan(dets, *args)
        run = BlueskyRun(dc)
        table = run.primary.read()
        motor_names = run.metadata['start']['motors']
        motors = [m for m in args if getattr(m, 'name', None) in motor_names]
 #       print(motors)
        if max_channel is None:
            detname = dets[0].name
        else:
            detname = max_channel
#        cofm = np.average(table[motors[0].name],weights=table[detname])
#        print(f"Center of mass found at {cofm} for detector {detname}")
        ret = []
        for m in motors:
            cofm = np.average(table[m.name],weights=table[detname])
          ##  max_val = float(table[m.name][max_idx])
            print(f"setting {m.name} to {cofm}")
            ret.append([m, cofm])
            if hysteresis_correct:
                sval = float(table[m.name][0])
                yield from mv(m, sval)
            yield from mv(m, cofm)
        return ret
    return (yield from inner_maximizer())

######################
def find_sp(plan, dets, *args, sp=0, max_channel=None, hysteresis_correct=False):

    dc = DocumentCache()

    @bpp.subs_decorator(dc)
    def inner_maximizer():
        yield from plan(dets, *args)
        run = BlueskyRun(dc)
        table = run.primary.read()
        motor_names = run.metadata['start']['motors']
        motors = [m for m in args if getattr(m, 'name', None) in motor_names]
        if max_channel is None:
            detname = dets[0].name
        else:
            detname = max_channel
        delta = abs(sp - table[detname])
        sp_idx = int(delta.argmin())
        print(f"Set point closest at step {sp_idx} for detector {detname}")
        ret = []
        for m in motors:
            sp_val = float(table[m.name][sp_idx])
            print(f"setting {m.name} to {sp_val}")
            ret.append([m, sp_val])
            if hysteresis_correct:
                sval = float(table[m.name][0])
                yield from mv(m, sval)
            yield from mv(m, sp_val)
        return ret
    return (yield from inner_maximizer())
