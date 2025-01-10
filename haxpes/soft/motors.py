from sst_base.motors import PrettyMotor
from sst_hw.mirrors import mir3 as M3AB
from sst_base.mirrors import FMBHexapodMirror
from ophyd import EpicsMotor

# In devices.toml

dm3 = PrettyMotor("XF:07ID3-BI{Diag:03-Ax:Y}Mtr", name="DM3/FS08-Y")
dm4 = PrettyMotor("XF:07ID5-BI{Diag:04-Ax:Y}Mtr", name="DM4/FS09-Y")

M4A = FMBHexapodMirror("XF:07ID3-OP{Mir:M4A", name="M4A", kind="hinted")

SlitAB = EpicsMotor(
    "XF:07ID3-OP{Slt:06-Ax:YGap}Mtr", name="Exit Slit AB", kind="hinted"
)
