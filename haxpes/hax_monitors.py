from ophyd import Device, Component as Cpt, EpicsSignalRO, Signal, EpicsSignal


class beamstatus(Device):
    state = Cpt(EpicsSignalRO, "Beam-Sts", kind="hinted")


class current_run_mode(Device):
    """possible run modes:
    XPS Peak
    XPS SES
    XAS
    ResPES
    Align
    Soft Beam
    """

    current_mode = Cpt(Signal, value="XPS Peak", kind="config")


beamon = beamstatus("XF:07ID6-OP{Mono:DCM1-Fb:PF2}", name="beam on")
run_mode = current_run_mode(name="RunMode")
beamselection = Signal(name="Beam Selection", kind="config", value="none")


