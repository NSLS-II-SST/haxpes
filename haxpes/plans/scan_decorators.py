from nbs_bl.utils import merge_func
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
import bluesky.plan_stubs as bps
from bluesky.preprocessors import finalize_wrapper


def haxpes_shutter_decorator(func):
    """
    A decorator that sets up scans for HAXPES. Adds the ability to use the Greateyes detector, and open or close the shutter.

    Parameters
    ----------
    func : callable
        The function to wrap
    """

    @merge_func(func)
    def _inner(*args, open_shutter=True, **kwargs):
        shutter = bl.devices.get("fs4", None)
        if open_shutter and shutter is not None:
            start_value = yield from bps.rd(shutter.state)
            start_state = "closed" if start_value == shutter.closeval else "open"
            if start_state == "closed":
                yield from shutter.open()

        def post_hardware_reset():
            if open_shutter and shutter is not None:
                if start_state == "closed":
                    yield from shutter.close()

        yield from finalize_wrapper(
            plan=func(*args, **kwargs), final_plan=post_hardware_reset()
        )

    return _inner
