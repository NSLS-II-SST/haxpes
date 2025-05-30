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
from math import asin, cos, sin, pi
from bluesky.plan_stubs import mv
from nbs_bl.devices.motors import DeadbandEpicsMotor

# gonilateral = PrettyMotor(
#    "XF:07ID6-OP{Mono:DCM1-Ax:X}Mtr", name="DCM goniometer lateral"
# )


class DCM(PseudoPositioner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode.put("motor")

    # configuration:
    d = Cpt(EpicsSignalRO, ":XTAL_CONST_MON", kind="config")
    hc = Cpt(EpicsSignalRO, ":HC_SP", kind="config")
    beam_offset = Cpt(EpicsSignalRO, ":BEAM_OFF_SP", kind="config")
    mode = Cpt(Signal, name="DCM mode", kind="config")
    crystal = Cpt(EpicsSignal, ":XTAL_SEL", string=True, kind="config")
    done_value = 1
    stop_signal = Cpt(EpicsSignal, ":ENERGY_ST_CMD")
    crystal_move = Cpt(EpicsSignal, ":XTAL_CMD.PROC")
    para_default = Cpt(Signal, value=7.5, kind="config")
    crystalstatus = Cpt(EpicsSignalRO, ":XTAL_STS", kind="config")

    offsetdict = {
        "Si(111)": 10.829,
        "Si(220)": 10.782,
        "Si(333)": 10.829,
        "Si(444)": 10.829,
    }

    rolldict = {"Si(111)": -1.25, "Si(220)": 0.5, "Si(333)": -1.25, "Si(444)": -1.25}

    gonilatdict = {"Si(111)": 0, "Si(220)": 35, "Si(333)": 0, "Si(444)": 0}

    # pseudo motor
    energy = Cpt(PseudoSingle, kind="hinted")

    readback = Cpt(EpicsSignalRO, ":ENERGY_MON", kind="hinted")

    # motors:
    bragg = Cpt(DeadbandEpicsMotor, "Bragg}Mtr", kind="normal")
    x2perp = Cpt(DeadbandEpicsMotor, "Per2}Mtr", tolerance=0.001, kind="normal")
    x2para = Cpt(DeadbandEpicsMotor, "Par2}Mtr", tolerance=0.001, kind="normal")
    x2roll = Cpt(DeadbandEpicsMotor, "R2}Mtr", tolerance=0.001, kind="normal")
    x2pitch = Cpt(DeadbandEpicsMotor, "P2}Mtr", tolerance=0.001, kind="normal")
    x2perp = Cpt(DeadbandEpicsMotor, "Per2}Mtr", tolerance=0.001, kind="normal")
    x2finepitch = Cpt(DeadbandEpicsMotor, "PF2}Mtr", tolerance=0.001, kind="normal")
    x2fineroll = Cpt(DeadbandEpicsMotor, "RF2}Mtr", tolerance=0.001, kind="normal")

    # the following is deprecated for set_crystal in tender_ops ... probably doesn't work any more anyway
    # crystal set ... you shouldn't do this when shutter 1 is open ...
    #    def set_crystal(self, crystalSP, roll_correct=1):
    #        """sets the crystal pair and moves to that value.
    #        This automatically disables the PSH1 suspender and closes the shutter.
    #        Suspender is re-enabled after move is complete."""
    #        if roll_correct:
    #            yield from mv(self.x2roll, self.rolldict[crystalSP])
    #        #        self.bragg.user_offset.set(self.offsetdict[crystalSP])
    #        yield from mv(self.bragg.user_offset, self.offsetdict[crystalSP])
    #        yield from mv(self.crystal, crystalSP)
    #        # check crystal status; 0 = Not In Position; 1 = In Position:
    #       inpos = self.crystalstatus.get()
    #        if inpos == 0:
    #
    #            from haxpes.startup import RE
    #            from haxpes.hax_suspenders import suspend_psh1
    #            from nbs_bl.hw import psh1
    #
    #            RE.remove_suspender(suspend_psh1)
    #            yield from psh1.close()
    #            yield from mv(gonilateral, self.gonilatdict[crystalSP])
    #           yield from psh1.open()
    #           RE.install_suspender(suspend_psh1)

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        x2perpcurrent = self.x2perp.position
        x2paracurrent = self.x2para.position
        x2rollcurrent = self.x2roll.position
        x2pitchcurrent = self.x2pitch.position
        x2finepitchcurrent = self.x2finepitch.position
        x2finerollcurrent = self.x2fineroll.position

        if self.mode.get() == "channelcut":
            return self.RealPosition(
                bragg=asin(
                    1000 * self.hc.get() / (2 * self.d.get() * pseudo_pos.energy)
                )
                * 180
                / pi,
                x2perp=x2perpcurrent,
                x2para=7.5,  ### this maybe should be changed to a fixed value.
                x2pitch=x2pitchcurrent,
                x2roll=x2rollcurrent,
                x2finepitch=x2finepitchcurrent,
                x2fineroll=x2finerollcurrent,
            )
        elif self.mode.get() == "motor":
            return self.RealPosition(
                bragg=asin(
                    1000 * self.hc.get() / (2 * self.d.get() * pseudo_pos.energy)
                )
                * 180
                / pi,
                x2perp=self.beam_offset.get()
                / (
                    2
                    * cos(
                        asin(
                            1000
                            * self.hc.get()
                            / (2 * self.d.get() * pseudo_pos.energy)
                        )
                    )
                ),
                x2para=self.para_default.get(),  ### think about this...
                x2pitch=x2pitchcurrent,
                x2roll=x2rollcurrent,
                x2finepitch=x2finepitchcurrent,
                x2fineroll=x2finerollcurrent,
            )
        elif self.mode.get() == "full":
            return self.RealPosition(
                bragg=asin(
                    1000 * self.hc.get() / (2 * self.d.get() * pseudo_pos.energy)
                )
                * 180
                / pi,
                x2perp=self.beam_offset.get()
                / (
                    2
                    * cos(
                        asin(
                            1000
                            * self.hc.get()
                            / (2 * self.d.get() * pseudo_pos.energy)
                        )
                    )
                ),
                x2para=self.beam_offset.get()
                / (
                    2
                    * sin(
                        asin(
                            1000
                            * self.hc.get()
                            / (2 * self.d.get() * pseudo_pos.energy)
                        )
                    )
                ),
                x2pitch=x2pitchcurrent,
                x2roll=x2rollcurrent,
                x2finepitch=x2finepitchcurrent,
                x2fineroll=x2finerollcurrent,
            )
        else:
            return

    @real_position_argument
    def inverse(self, real_pos):
        return self.PseudoPosition(
            energy=1000
            * self.hc.get()
            / (2 * self.d.get() * sin(real_pos.bragg * pi / 180))
        )


# dcm = DCM("XF:07ID6-OP{Mono:DCM1-Ax:",name="dcm")
