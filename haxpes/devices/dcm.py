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
from sst_base.motors import DeadbandFMBOEpicsMotor

class DCM_energy(PVPositioner):
    setpoint = Cpt(EpicsSignal,":ENERGY_SP",kind='config')
    readback = Cpt(EpicsSignal,":ENERGY_MON",kind='normal')
    done = Cpt(EpicsSignalRO,":ERDY_STS",kind="config")
    done_value = 1
    stop_signal = Cpt(EpicsSignal, ":ENERGY_ST_CMD.PROC")
    _enable_cmd = Cpt(EpicsSignal, ":ENA_CMD.PROC")


#    def _setup_move(self, position):
#        """Move and do not wait until motion is complete (asynchronous)
#        Required so that mono moves do not wait unintentionally, as setpoint
#        put will not return until motor has finished moving"""
#       self.log.debug("%s.setpoint = %s", self.name, position)
#       self._check_and_enable()
#        # copy from pv_positioner, with wait changed to false
#        # possible problem with IOC not returning from a set
#        self.setpoint.put(position, wait=False)
#        if self.actuate is not None:
#            self.log.debug("%s.actuate = %s", self.name, self.actuate_value)
#            self.actuate.put(self.actuate_value, wait=False)
#
#    def _check_and_enable(self):
#        if self.done.get() == 4:
#_en            self._enable_cmd.put(1,wait=True)       


"""
XF:07ID6-OP{Mono:DCM1-Ax::ERDY_STS

"""

class DCM(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #energy = Cpt(DCM_energy, kind="config")

    # configuration:
    d = Cpt(EpicsSignalRO, ":XTAL_CONST_MON", kind="config")
    hc = Cpt(EpicsSignalRO, ":HC_SP", kind="config")
    beam_offset = Cpt(EpicsSignalRO, ":BEAM_OFF_SP", kind="config")
    mode = Cpt(EpicsSignal, 
        read_pv="XF:07ID6-OP{MC:08}DCM_MODE_RBV", 
        write_pv="XF:07ID6-OP{MC:08}DCM_MODE", 
        kind="config",
        add_prefix=[False,False],
        string=True
    )
    crystal = Cpt(EpicsSignal, ":XTAL_SEL", string=True, kind="config")

    crystal_move = Cpt(EpicsSignal, ":XTAL_CMD.PROC")
    para_default = Cpt(Signal, value=7.5, kind="config")
    crystalstatus = Cpt(EpicsSignalRO, ":XTAL_STS", kind="config")

    # motors:
    bragg = Cpt(DeadbandEpicsMotor, "Bragg}Mtr", kind="normal")
    x2perp = Cpt(DeadbandEpicsMotor, "Per2}Mtr", tolerance=0.001, kind="normal")
    x2para = Cpt(DeadbandEpicsMotor, "Par2}Mtr", tolerance=0.001, kind="normal")
    x2roll = Cpt(DeadbandFMBOEpicsMotor, "R2}Mtr", tolerance=0.001, kind="normal")
    x2pitch = Cpt(DeadbandFMBOEpicsMotor, "P2}Mtr", tolerance=0.001, kind="normal")
    x2perp = Cpt(DeadbandEpicsMotor, "Per2}Mtr", tolerance=0.001, kind="normal")
    x2finepitch = Cpt(DeadbandEpicsMotor, "PF2}Mtr", tolerance=0.001, kind="normal")
    x2fineroll = Cpt(DeadbandEpicsMotor, "RF2}Mtr", tolerance=0.001, kind="normal")

