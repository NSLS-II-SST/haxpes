from haxpes.energy_tender import mono as dcm
from sst_base.motors import PrettyMotor


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
