from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt
from sst_hw import UndulatorMotor

u42gap = UndulatorMotor("SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr", kind="normal",
                        name="U42 Gap")


class DCM(PVPositioner):
    setpoint = Cpt(EpicsSignal, ":ENERGY_SP", kind="normal")
    readback = Cpt(EpicsSignalRO, ":ENERGY_MON", kind="hinted")


dcm = DCM("XF:07id6-OP{Mono:DCM1-Ax:", kind="normal",
          name="DCM Energy")
