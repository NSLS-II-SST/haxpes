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
from .dcm import DCM
from sst_base.energy import UndulatorMotor

import numpy as np


class energypos(PseudoPositioner):

    energy = Cpt(PseudoSingle, kind="hinted", limits=(1985, 9000))

    harmonic = Cpt(Signal, value=3, kind="config", name="U42 Harmonic")

    mono = Cpt(DCM, "XF:07ID6-OP{Mono:DCM1-Ax:", name="dcm", kind="config")
    u42 = Cpt(
        UndulatorMotor,
        "SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr",
        kind="config",
        name="U42 Gap",
    )
    u42val = Cpt(Signal, kind="config", name="U42 Gap Calculation")

    offset_gap = Cpt(Signal, value=0, name="U42 Gap Offset", kind="config")

    def set_mono_mode(self, mono_mode):
        self.mono.mode.set(mono_mode)

    def set_mono_crystal(self, crystal):
        self.mono.set_crystal(crystal)

    def calc_gap(self, energy, harmonic, lims=(13446, 32902)):
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
        polyfit = np.poly1d(fit_coefficients)
        gap = polyfit(energy / harmonic)
        ### limit gap ... need to think of a better way to handle this ...
        if gap < min(lims):
            print("Warning, undulator value is below calibrated region.")
            gap = min(lims)
        if gap > max(lims):
            gap = max(lims)
            print("Warning, undulator value is above calibrated region.")
        self.u42val.set(gap)
        return gap + self.offset_gap.get()

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        return self.RealPosition(
            mono=[pseudo_pos.energy],
            u42=self.calc_gap(pseudo_pos.energy, self.harmonic.get()),
        )

    @real_position_argument
    def inverse(self, real_pos):
        return self.PseudoPosition(energy=real_pos.mono.energy)


enpos = energypos("", name="SST2 Energy")
en = enpos.energy
mono = enpos.mono
h = enpos.harmonic
U42 = enpos.u42
gapoffset = enpos.offset_gap
