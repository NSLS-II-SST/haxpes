from ophyd import EpicsSignal, EpicsSignalRO, Signal, Device, Component as Cpt

class SMU(Device):

    VLim = Cpt(EpicsSignal,'SP-LimV',kind='config')
    ILim = Cpt(EpicsSignal,'SP-LimI',kind='config')
    SourceSelect = Cpt(EpicsSignal,'Sour:Sts',write_pv='Sour-Sel',kind='config')
    OutputEnable = Cpt(EpicsSignal,'Sts:Out-Ena',write_pv='Cmd:Out-Ena',kind='config')
    VSource = Cpt(EpicsSignal,'RB-VLvl',write_pv='SP-VLvl',kind='config')
    ISource = Cpt(EpicsSignal,'RB-ILvl',write_pv='SP-ILvl',kind='config')
    VMeas = Cpt(EpicsSignalRO,'RB-MeasV',kind='hinted')
    IMeas = Cpt(EpicsSignalRO,'RB-MeasI',kind='hinted')
    IMeasRange = Cpt(EpicsSignal,'Sts-MeasIRang',write_pv='SP-MeasIRang',kind='config')
    VSourceRange = Cpt(EpicsSignal,'Sts-SourVRang',write_pv='SP-SourVRang',kind='config')
    ISourceRange = Cpt(EpicsSignal,'Sts-SourIRang',write_pv='SP-SourIRang',kind='config')
    AutorangeISource = Cpt(EpicsSignal,'SP-SourAutoRangI',kind='config')
    AutorangeVSource = Cpt(EpicsSignal,'SP-SourAutoRangV',kind='config')
    AutorangeIMeas = Cpt(EpicsSignal,'SP-MeasAutoRangI',kind='config')
    AutorangeVMeas = Cpt(EpicsSignal,'SP-MeasAutoRangV',kind='config')

    def __init__(self,*args,**kwargs):
        """ puts it in DCVolts Source mode, sets source voltage to 0, sets voltage limit to 10 mA """
        super().__init__(*args, **kwargs)
        self.SourceSelect.set(1)
        self.VSource.set(0)
        self.ILim.set(0.01)
        self.OutputEnable.set(1)

    

haxSMU = SMU('XF:07ID1{K2601B:1}', name='K2601B')
