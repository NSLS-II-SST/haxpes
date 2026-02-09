from ophyd import (
    EpicsMotor,
#    PseudoPositioner,
#    PseudoSingle,
    EpicsSignalRO,
    EpicsSignal,
    Signal,
    Component as Cpt,
    PVPositioner,
    Device
)
from ophyd.pseudopos import pseudo_position_argument, real_position_argument
from .dcm import DCM, DCM_energy
from sst_base.energy import UndulatorMotor
from nbs_bl.devices.motors import DeadbandPVPositioner
from time import sleep

import numpy as np


### don't think I need the U42 ###
class U42(UndulatorMotor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    _enabledTU = Cpt(EpicsSignalRO, "SR:C07-ID:G1A{SST2:1-Ax:TU}Sw:AmpEn-Sts", add_prefix=[False],kind='config')
    _enabledTD = Cpt(EpicsSignalRO, "SR:C07-ID:G1A{SST2:1-Ax:TD}Sw:AmpEn-Sts", add_prefix=[False],kind='config')

    def _check_and_enable(self):
        if not self._enabledTU.get() and not self._enabledTD.get():
            print('not enabled')
            current_position = self.position
            self.user_setpoint.put(current_position,wait=False)
            print('U42 not enabled.  Enabling')
            sleep(1.)

    def move(self, position,**kwargs):
        self._check_and_enable()
        super().move(position,**kwargs)

    
class flyenergy(DeadbandPVPositioner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    setpoint = Cpt(EpicsSignal, "FlyMove-Mtr-SP-Go")
    readback = Cpt(EpicsSignal, "FlyEnergyID-RB")
    # readback = Cpt(EpicsSignal, "FlyMove-Mtr.RBV")
    done = Cpt(EpicsSignalRO, "FlyMove-Mtr.MOVN")
    done_value = 0
    stop_signal = Cpt(EpicsSignal, "FlyMove-Mtr.STOP")
    speed = Cpt(EpicsSignal,"FlyMove-Speed-RB",write_pv="FlyMove-Speed-SP",kind="config")


class energypos(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy.tolerance.set(0.15).wait()
                    
    speed = Cpt(EpicsSignal,"FlyMove-Speed-RB",write_pv="FlyMove-Speed-SP",kind="config")
    
    harmonic = Cpt(
        EpicsSignal,
        "FlyHarmonic-RB",
        write_pv="FlyHarmonic-SP",
        kind="config",
        name="U42 Harmonic",
    )

    mono = Cpt(DCM, "XF:07ID6-OP{Mono:DCM1-Ax:", name="dcm", kind="config",add_prefix=[False,False])
    mono_en = Cpt(DCM_energy, "XF:07ID6-OP{Mono:DCM1-Ax:", name = "dcm_energy", kind="config", add_prefix=[False,False])

    u42 = Cpt(
        U42,
        "SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr",
        tolerance=0.001,
        kind="config",
        name="U42 Gap",
        add_prefix=[False,False]
    )
    
    energy = Cpt(flyenergy,"SR:C07-ID:G1A{SST2:1}",add_prefix=[False,False])

    offset_gap = Cpt(EpicsSignal,"EScanIDEnergyOffset-RB",write_pv="EScanIDEnergyOffset-SP",kind='config')

    def set_mono_crystal(self, crystal):
        self.mono.set_crystal(crystal)

#enpos = energypos("SR:C07-ID:G1A{SST2:1}", name="SST2 Energy")


