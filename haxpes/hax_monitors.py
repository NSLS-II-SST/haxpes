from ophyd import Device, Component as Cpt, EpicsSignalRO

class beamstatus(Device):
    state = Cpt(EpicsSignalRO,"Beam-Sts",kind="hinted")


beamon = beamstatus("XF:07ID6-OP{Mono:DCM1-Fb:PF2}",name='beam on')
