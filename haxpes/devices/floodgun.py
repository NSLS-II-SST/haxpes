from ophyd import Device, EpicsSignal, Component as Cpt, EpicsSignalRO

class FloodGun(Device):
    energy = Cpt(EpicsSignal,'EnergyRBV',write_pv='EnergySP',kind='config')
    Vgrid = Cpt(EpicsSignal,'VgridRBV',write_pv='VgridSP',kind='config')
    Iemis = Cpt(EpicsSignalRO,'IemissionRBV',kind='config')
    startProc = Cpt(EpicsSignal,'Resume',kind='config')
    stopProc = Cpt(EpicsSignal,'Shutdown',kind='config')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    
    def startup(self,energy=None,Vgrid=None):
        self.startProc.put(1)
        if energy:
            self.energy.put(energy)
        if Vgrid:
            self.Vgrid.put(Vgrid)

    def shutdown(self):
        self.stopProc.put(1)
    
