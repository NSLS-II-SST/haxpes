from sst_base.shutters import EPS_Shutter
from haxpes.pid_feedback import pid
from ophyd import EpicsSignalRO, Signal
from haxpes.floodgun import FloodGun

# photon shutters ...

psh1 = EPS_Shutter("XF:07IDA-PPS{PSh:1}", name="SST-2 Branch Shutter", kind="hinted")
psh1.shutter_type = "PH"
psh1.openval = 0
psh1.closeval = 1

psh2 = EPS_Shutter("XF:07IDA-PPS{PSh:2}", name="Shutter 2", kind="hinted")
psh2.shutter_type = "PH"
psh2.openval = 0
psh2.closeval = 1

psh5 = EPS_Shutter("XF:07IDA-PPS{PSh:5}", name="Shutter 5", kind="hinted")
psh5.shutter_type = "PH"
psh5.openval = 0
psh5.closeval = 1

# gate valves ...

gv10 = EPS_Shutter("XF:07IDB-VA:1{HAXPES-GV:1}", name="downstream GV", kind="hinted")
gv10.shutter_type = "GV"
gv10.openval = 1
gv10.closeval = 0

# FS4 ...

fs4 = EPS_Shutter("XF:07IDB-VA:1{FS:4A}", name="FS 4", kind="hinted")
fs4.shutter_type = "FS"
fs4.openval = 1
fs4.closeval = 0

# feedback PIDs:
fbvert = pid("XF:07ID6-OP{Mono:DCM1-Fb:PF2}", name="vertical feedback")
fbhor = pid("XF:07ID6-OP{Mono:DCM1-Fb:RF2}", name="horizontal feedback")

# soft beam enable and beamline mode:
softbeamenable = EpicsSignalRO("XF:07ID1-CT{Bl-Ctrl}Endstn-Sel",kind='config',string=True)
beamselection = Signal(name="Beam Selection",kind="config",value="none")

#flood gun
floodgun = FloodGun('XF:07ID-EGPS:1:',name="FloodGun")

#SMU
from haxpes.k2600b import SMU
haxSMU = SMU('XF:07ID1{K2601B:1}', name='K2601B')
