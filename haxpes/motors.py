from sst_base.motors import EpicsMotor, PrettyMotor
from sst_base.manipulator import Manipulator4AxBase
from ophyd import Component as Cpt
from sst_hw.energy import UndulatorMotor
from .slits import Slits
from .energy_tender import mono as dcm

class Manipulator(Manipulator4AxBase):
    x = Cpt(EpicsMotor, "SampX}Mtr", name="x", kind='hinted')
    y = Cpt(EpicsMotor, "SampY}Mtr",  name="y", kind='hinted')
    z = Cpt(EpicsMotor, "SampZ}Mtr",  name="z", kind='hinted')
    r = Cpt(EpicsMotor, "SampTh}Mtr", name="r", kind='hinted')

#sample manipulator:
manipulator = Manipulator(None, "XF:07ID1-BI{HAX-Ax:", name="haxpes_manipulator")
sampx = manipulator.x
sampy = manipulator.y
sampz = manipulator.z
sampr = manipulator.r

#DCM motors:  ###defined in DCM; call them from enpositioner here.
#x2pitch = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:P2}Mtr", name= "x2 pitch")
#x2roll = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:R2}Mtr", name = "x2 roll")
#x2perp = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:Per2}Mtr", name = "x2 perp offset")
#x2finepitch = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:PF2}Mtr", name = "x2 pitch piezo")
#x2fineroll = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:RF2}Mtr", name = "x2 roll piezo")
#braggmotor = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:Bragg}Mtr", name = "Bragg rotation")
x2pitch = dcm.x2pitch
x2roll = dcm.x2roll
x2perp = dcm.x2perp
x2finepitch = dcm.x2finepitch
x2fineroll = dcm.x2fineroll
bragg = dcm.bragg

#DM1 ... photodiode = 32, FS = 0, mesh = -22, out = 60
dm1 = PrettyMotor("XF:07ID6-BI{Diag:01-Ax:Y}Mtr",name="DM1/FS03-Y")

#DM4 ... photodiode = 32, FS = 0, mesh = -22, out = 60
dm4 = PrettyMotor("XF:07ID5-BI{Diag:04-Ax:Y}Mtr",name="DM4/FS09-Y")

# Undulator
u42gap = UndulatorMotor("SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr", kind="normal", name="U42 Gap")

# HAXPES slits (SLT12)
haxslt = Slits("XF:07ID2-OP{Slt:12-Ax:",name="HAXPES slits",kind="hinted",concurrent=1)

# nanoBPM / filter:
nBPM = PrettyMotor("XF:07ID6-BI{BPM:1-Ax:Y}Mtr",name="nBPM/C Filter")

