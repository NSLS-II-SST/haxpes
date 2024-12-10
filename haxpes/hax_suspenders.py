from bluesky.suspenders import SuspendBoolHigh, SuspendBoolLow
from .hax_hw import psh2, psh1, psh5, fs4
from sst_hw.shutters import FEsh1, psh4
from .ses import ses
from bluesky.plan_stubs import mv
from .hax_ops import stop_SES# start_SES
from .hax_monitors import beamon, run_mode

def pre_plan():
    """ checks current run mode, then makes decision based on said run mode """
    if run_mode.current_mode.get() == "Align":
        pass
    elif run_mode.current_mode.get() == "XPS Peak":
        pass
    elif run_mode.current_mode.get() == "XPS SES":
        yield from stop_SES()
    elif run_mode.current_mode.get() == "ResPES":
        pass
    elif run_mode.current_mode.get() == "Soft Beam":
        pass
    elif run_mode.current_mode.get() == "XAS":
        pass
    else:
        pass

def post_plan():
    """ checks current run mode, then makes decision based on said run mode """
    from haxpes.tender.tender_ops import reset_feedback
    reset_feedback()
    if run_mode.current_mode.get() == "Align":
        pass #nothing special
    elif run_mode.current_mode.get() == "XPS Peak":
        print('woopdeedoo!')
        pass #check I0 and re-align beam       
    elif run_mode.current_mode.get() == "XPS SES":
        yield from start_SES()
        #check I0 and re-align beam
    elif run_mode.current_mode.get() == "ResPES":
        pass
        #check i0 and re-align beam ?
    elif run_mode.current_mode.get() == "Soft Beam":
        pass
        #nothing special
    elif run_mode.current_mode.get() == "XAS":
        pass
        # ?
    else:
        pass

suspend_psh2 = SuspendBoolHigh(
    psh2.state,
    sleep=10,
    pre_plan = pre_plan(),
    post_plan = post_plan(),
    tripped_message = "Shutter 2 is closed.  Waiting for it to re-open."
    )

suspend_psh1 = SuspendBoolHigh(
    psh1.state,
    sleep=10,
    pre_plan = pre_plan(),
    post_plan = post_plan(),
    tripped_message = "Shutter 1 is closed.  Waiting for it to re-open."
    )

suspend_FEsh1 = SuspendBoolHigh(
    FEsh1.state,
    sleep=10,
    pre_plan = pre_plan(),
    post_plan = post_plan(),
    tripped_message = "FE shutter is closed.  Waiting for it to re-open."
    )

suspend_beamstat = SuspendBoolLow(
    beamon.state,
    sleep=10,
    pre_plan = pre_plan(),
    post_plan = post_plan(),
    tripped_message = "Beam is down.  Waiting for recovery."
    )

suspend_psh4 = SuspendBoolHigh(
    psh4.state,
    sleep=10,
    pre_plan = pre_plan(),
    post_plan = post_plan(),
    tripped_message = "Shutter 4 is closed.  Waiting for it to re-open."
    )

suspend_psh5 = SuspendBoolHigh(
    psh5.state,
    sleep=10,
    pre_plan = pre_plan(),
    post_plan = post_plan(),
    tripped_message = "Shutter 5 is closed.  Waiting for it to re-open."
    )

suspend_fs4a = SuspendBoolLow(
    fs4.state,
    sleep=10,
    pre_plan = pre_plan(),
    post_plan = post_plan(),    
    tripped_message = "FS4A is closed.  Waiting for it to re-open"
    )

suspendUS_tender = [suspend_beamstat, suspend_FEsh1, suspend_psh1]
suspendHAX_tender = [suspend_beamstat, suspend_FEsh1, suspend_psh1, suspend_psh2]
suspendHAX_soft = [suspend_beamstat, suspend_FEsh1, suspend_psh4, suspend_psh5]
#suspendUS_tender = [suspend_FEsh1, suspend_psh1]
#suspendHAX_tender = [suspend_FEsh1, suspend_psh1, suspend_psh2]

