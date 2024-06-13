from haxpes.energy_tender import mono as dcm
from sst_base.motors import PrettyMotor
from sst_base.mirrors import FMBHexapodMirror
from ophyd import EpicsMotor

x2pitch = dcm.x2pitch
x2roll = dcm.x2roll
x2perp = dcm.x2perp
x2finepitch = dcm.x2finepitch
x2fineroll = dcm.x2fineroll
bragg = dcm.bragg

#DM1 ... photodiode = 32, FS = 0, mesh = -22, out = 60
dm1 = PrettyMotor("XF:07ID6-BI{Diag:01-Ax:Y}Mtr",name="DM1/FS03-Y")

# nanoBPM / filter:
nBPM = PrettyMotor("XF:07ID6-BI{BPM:1-Ax:Y}Mtr",name="nBPM/C Filter")

#L1 hexapod:
L1 = FMBHexapodMirror("XF:07IDA-OP{Mir:L1",name="L1")

#L2AB hexapod:
L2AB = FMBHexapodMirror("XF:07IDA6-OP{Mir:L2AB",name="L2AB")

#L2AB wedge:
L2wedge = EpicsMotor("XF:07IDA6-OP{Mir:L2AB-Ax:Y2}Mtr",name="L2 Wedge")

