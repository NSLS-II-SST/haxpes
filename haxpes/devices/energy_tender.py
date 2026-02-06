from ophyd import (
    EpicsMotor,
    PseudoPositioner,
    PseudoSingle,
    EpicsSignalRO,
    EpicsSignal,
    Signal,
    Component as Cpt,
)
from ophyd.pseudopos import pseudo_position_argument, real_position_argument
from .dcm import DCM, DCM_energy
from sst_base.energy import UndulatorMotor
from time import sleep

import numpy as np

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

    

class energypos(PseudoPositioner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.u42.tolerance.put(1)
        fit_coefficients = np.array(
            (
                3.721976545762123387e-12,
                -1.882489732981389563e-08,
                4.211877279144933479e-05,
                -5.089901181955627796e-02,
                4.530182069819578317e01,
                1.215159200296257040e03,
            )
        )
        self.polyfit = np.poly1d(fit_coefficients)

    energy = Cpt(PseudoSingle, kind="hinted", limits=(1985, 9000))

    harmonic = Cpt(
        EpicsSignal,
        "XF:07ID2-HAXMonitor:U42harmonic",
        kind="config",
        name="U42 Harmonic",
    )

    mono = Cpt(DCM, "XF:07ID6-OP{Mono:DCM1-Ax:", name="dcm", kind="config")
    mono_en = Cpt(DCM_energy, "XF:07ID6-OP{Mono:DCM1-Ax:", name = "dcm_energy", kind="config")

    u42 = Cpt(
        #UndulatorMotor,
        U42,
        "SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr",
        tolerance=0.001,
        kind="config",
        name="U42 Gap",
    )
    u42val = Cpt(Signal, value=0, kind="config", name="U42 Gap Calculation")

    offset_gap = Cpt(Signal, value=0, name="U42 Gap Offset", kind="config")

#    def set_mono_mode(self, mono_mode):
#        self.mono.mode.set(mono_mode)

    def set_mono_crystal(self, crystal):
        self.mono.set_crystal(crystal)

    def calc_gap(self, energy, harmonic, lims=(13446, 32902)):
        gap = self.polyfit(energy / harmonic)
        ### limit gap ... need to think of a better way to handle this ...
        if gap < min(lims):
            print("Warning, undulator value is below calibrated region.")
            gap = min(lims)
        if gap > max(lims):
            gap = max(lims)
            print("Warning, undulator value is above calibrated region.")
        self.u42val.put(gap)
        return gap + self.offset_gap.get()

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        return self.RealPosition(
            mono_en=pseudo_pos.energy,
            u42=self.calc_gap(pseudo_pos.energy, self.harmonic.get()),
        )

    @real_position_argument
    def inverse(self, real_pos):
        return self.PseudoPosition(energy=real_pos.mono_en)


enpos = energypos("", name="SST2 Energy")
en = enpos.energy
#mono = enpos.mono
h = enpos.harmonic
U42 = enpos.u42
gapoffset = enpos.offset_gap
