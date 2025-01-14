from ophyd import Device, Component, EpicsSignalRO,EpicsSignal

class pid(Device):
    lastinput = Component(EpicsSignalRO,"Inp-Sts.A",kind='hinted')
    setpoint = Component(EpicsSignal,"PID-SP",kind='config')
    K_P = Component(EpicsSignal,"PID.KP",kind='config')
    K_I = Component(EpicsSignal,"PID.KI",kind='config')
    K_D = Component(EpicsSignal,"PID.KD",kind='config')
    dband = Component(EpicsSignal,"Val:DBnd-SP",kind='config')
    pidcontrol = Component(EpicsSignal,"Sts:FB-Sel",kind='config')
    updaterate = Component(EpicsSignal,"Inp-Sts.SCAN",kind='config')
    in_low = Component(EpicsSignal,"Inp-LowLim",kind='config')
    in_high = Component(EpicsSignal,"Inp-HighLim",kind='config')
    out_low = Component(EpicsSignal,"Out-LowLim",kind='config')
    out_high = Component(EpicsSignal,"Out-HighLim",kind='config')
    pid_out = Component(EpicsSignalRO,"PID.OVAL",kind='hinted')
    mtr_out = Component(EpicsSignalRO,"Val:OBuf3.OVAL",kind='hinted')
    permitlatch = Component(EpicsSignal,"Perm-Ltch",kind='config')

