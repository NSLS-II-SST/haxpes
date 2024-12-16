from nbs_bl.devices import Manipulator4AxBase
from ophyd import Component as Cpt, EpicsMotor

# from .slits import Slits


class Manipulator(Manipulator4AxBase):
    x = Cpt(EpicsMotor, "SampX}Mtr", name="x", kind="hinted")
    y = Cpt(EpicsMotor, "SampY}Mtr", name="y", kind="hinted")
    z = Cpt(EpicsMotor, "SampZ}Mtr", name="z", kind="hinted")
    r = Cpt(EpicsMotor, "SampTh}Mtr", name="r", kind="hinted")


# sample manipulator:
"""manipulator = Manipulator(None, "XF:07ID1-BI{HAX-Ax:", name="haxpes_manipulator")
sampx = manipulator.x
sampy = manipulator.y
sampz = manipulator.z
sampr = manipulator.r
"""
# DCM motors:  ###defined in DCM; call them from enpositioner here.
# x2pitch = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:P2}Mtr", name= "x2 pitch")
# x2roll = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:R2}Mtr", name = "x2 roll")
# x2perp = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:Per2}Mtr", name = "x2 perp offset")
# x2finepitch = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:PF2}Mtr", name = "x2 pitch piezo")
# x2fineroll = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:RF2}Mtr", name = "x2 roll piezo")
# braggmotor = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:Bragg}Mtr", name = "Bragg rotation")

# HAXPES slits (SLT12)
"""haxslt = Slits(
    "XF:07ID2-OP{Slt:12-Ax:", name="HAXPES slits", kind="hinted", concurrent=1
)

# DM1 slits (SLT1)
slt_dm1 = Slits("XF:07ID6-OP{Slt:03-Ax:", name="DM1_slits", kind="hinted", concurrent=1)
"""
