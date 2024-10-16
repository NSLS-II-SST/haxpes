from bluesky.suspenders import SuspendBoolHigh, SuspendBoolLow
from .hax_hw import psh2, psh1, psh5, fs4
from sst_hw.shutters import FEsh1, psh4
from .ses import ses
from bluesky.plan_stubs import mv
from .hax_ops import stop_SES# start_SES
from .hax_monitors import beamon

suspend_psh2 = SuspendBoolHigh(
    psh2.state,
    sleep=10,
   # pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "Shutter 2 is closed.  Waiting for it to re-open."
    )

suspend_psh1 = SuspendBoolHigh(
    psh1.state,
    sleep=10,
   # pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "Shutter 1 is closed.  Waiting for it to re-open."
    )

suspend_FEsh1 = SuspendBoolHigh(
    FEsh1.state,
    sleep=10,
   # pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "FE shutter is closed.  Waiting for it to re-open."
    )

suspend_beamstat = SuspendBoolLow(
    beamon.state,
    sleep=10,
   # pre_plan = stop_SES,
    tripped_message = "Beam is down.  Waiting for recovery."
    )
#XF:07ID6-OP{Mono:DCM1-Fb:PF2}Beam-Sts

suspend_psh4 = SuspendBoolHigh(
    psh4.state,
    sleep=10,
   # pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "Shutter 4 is closed.  Waiting for it to re-open."
    )

suspend_psh5 = SuspendBoolHigh(
    psh5.state,
    sleep=10,
   # pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "Shutter 5 is closed.  Waiting for it to re-open."
    )

suspend_fs4a = SuspendBoolLow(
    fs4.state,
    sleep=10,
   # pre_plan = stop_SES,
    tripped_message = "FS4A is closed.  Waiting for it to re-open"
    )

#### with SES
suspend_psh2_SES = SuspendBoolHigh(
    psh2.state,
    sleep=10,
    pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "Shutter 2 is closed.  Waiting for it to re-open."
    )

suspend_psh1_SES = SuspendBoolHigh(
    psh1.state,
    sleep=10,
    pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "Shutter 1 is closed.  Waiting for it to re-open."
    )

suspend_FEsh1_SES = SuspendBoolHigh(
    FEsh1.state,
    sleep=10,
    pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "FE shutter is closed.  Waiting for it to re-open."
    )

suspend_beamstat_SES = SuspendBoolLow(
    beamon.state,
    sleep=10,
   # pre_plan = stop_SES,
    tripped_message = "Beam is down.  Waiting for recovery."
    )
#XF:07ID6-OP{Mono:DCM1-Fb:PF2}Beam-Sts

suspend_psh4_SES = SuspendBoolHigh(
    psh4.state,
    sleep=10,
    pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "Shutter 4 is closed.  Waiting for it to re-open."
    )

suspend_psh5_SES = SuspendBoolHigh(
    psh5.state,
    sleep=10,
    pre_plan = stop_SES,
   # post_plan = start_SES,
    tripped_message = "Shutter 5 is closed.  Waiting for it to re-open."
    )

suspend_fs4a_SES = SuspendBoolLow(
    fs4.state,
    sleep=10,
    pre_plan = stop_SES,
    tripped_message = "FS4A is closed.  Waiting for it to re-open"
    )
#suspend_softstatus = ...(
