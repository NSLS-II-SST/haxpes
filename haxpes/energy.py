from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt
from sst_hw.energy import UndulatorMotor
from sst_base.positioners import DeadbandMixin

u42gap = UndulatorMotor("SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr", kind="normal",
                        name="U42 Gap")


class DCM(DeadbandMixin, PVPositioner):
    setpoint = Cpt(EpicsSignal, ":ENERGY_SP", kind="normal")
    readback = Cpt(EpicsSignalRO, ":ENERGY_MON", kind="hinted")
    done = Cpt(EpicsSignalRO, ":ERDY_STS")
    done_value = 1
    stop_signal = Cpt(EpicsSignal, ":ENERGY_ST_CMD")

dcm = DCM("XF:07ID6-OP{Mono:DCM1-Ax:", kind="normal",
          name="DCM Energy")
dcm.tolerance.set(0.001)
