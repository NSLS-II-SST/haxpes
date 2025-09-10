from ophyd import (
    EpicsMotor,
    PseudoPositioner,
    PseudoSingle,
    EpicsSignalRO,
    EpicsSignal,
    Signal,
    PVPositioner,   
    Component as Cpt,
    Device
)
from ophyd.pseudopos import pseudo_position_argument, real_position_argument
from math import asin, cos, sin, pi
from bluesky.plan_stubs import mv
from nbs_bl.devices.motors import DeadbandEpicsMotor


class DCM_energy(PVPositioner):
    setpoint = Cpt(EpicsSignal,":ENERGY_SP",kind='config')
    readback = Cpt(EpicsSignal,":ENERGY_MON",kind='normal')
    done = Cpt(EpicsSignalRO,":ERDY_STS",kind="config")
    done_value = 1

class DCM(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #energy = Cpt(DCM_energy, kind="config")

    # configuration:
    d = Cpt(EpicsSignalRO, ":XTAL_CONST_MON", kind="config")
    hc = Cpt(EpicsSignalRO, ":HC_SP", kind="config")
    beam_offset = Cpt(EpicsSignalRO, ":BEAM_OFF_SP", kind="config")
    mode = Cpt(Signal, name="DCM mode", value='motor', kind="config")
    crystal = Cpt(EpicsSignal, ":XTAL_SEL", string=True, kind="config")
    stop_signal = Cpt(EpicsSignal, ":ENERGY_ST_CMD")
    crystal_move = Cpt(EpicsSignal, ":XTAL_CMD.PROC")
    para_default = Cpt(Signal, value=7.5, kind="config")
    crystalstatus = Cpt(EpicsSignalRO, ":XTAL_STS", kind="config")

    # motors:
    bragg = Cpt(DeadbandEpicsMotor, "Bragg}Mtr", kind="normal")
    x2perp = Cpt(DeadbandEpicsMotor, "Per2}Mtr", tolerance=0.001, kind="normal")
    x2para = Cpt(DeadbandEpicsMotor, "Par2}Mtr", tolerance=0.001, kind="normal")
    x2roll = Cpt(DeadbandEpicsMotor, "R2}Mtr", tolerance=0.001, kind="normal")
    x2pitch = Cpt(DeadbandEpicsMotor, "P2}Mtr", tolerance=0.001, kind="normal")
    x2perp = Cpt(DeadbandEpicsMotor, "Per2}Mtr", tolerance=0.001, kind="normal")
    x2finepitch = Cpt(DeadbandEpicsMotor, "PF2}Mtr", tolerance=0.001, kind="normal")
    x2fineroll = Cpt(DeadbandEpicsMotor, "RF2}Mtr", tolerance=0.001, kind="normal")

#    def set_mode
"""
PVs for the DCM mode:
XF:07ID6-OP{MC:08}DCM_MODE
XF:07ID6-OP{MC:08}DCM_MODE_RBV
"""
