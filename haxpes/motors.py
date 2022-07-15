from sst_base.motors import EpicsMotor, PrettyMotor
from sst_base.manipulator import Manipulator4AxBase
from ophyd import Component as Cpt

class Manipulator(Manipulator4AxBase):
    x = Cpt(EpicsMotor, "SampX}Mtr", name="x", kind='hinted')
    y = Cpt(EpicsMotor, "SampY}Mtr",  name="y", kind='hinted')
    z = Cpt(EpicsMotor, "SampZ}Mtr",  name="z", kind='hinted')
    r = Cpt(EpicsMotor, "SampTh}Mtr", name="r", kind='hinted')

manipulator = Manipulator(None, "XF:07ID1-BI{HAX-Ax:", name="haxpes_manipulator")
sampx = manipulator.x
sampy = manipulator.y
sampz = manipulator.z
sampr = manipulator.r

x2pitch = PrettyMotor("XF:07ID6-OP{Mono:DCM1-Ax:P2}Mtr",name="x2 pitch")
