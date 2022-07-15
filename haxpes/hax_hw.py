from sst_base.shutters import EPS_Shutter


# photon shutters ...

psh1 = EPS_Shutter("XF:07IDA-PPS{PSh:1}", name="SST-2 Branch Shutter", kind="hinted")
psh1.shutter_type = "PH"
psh1.openval = 0
psh1.closeval = 1

psh2 = EPS_Shutter("XF:07IDA-PPS{PSh:2}", name="Shutter 2", kind="hinted")
psh2.shutter_type = "PH"
psh2.openval = 0
psh2.closeval = 1

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


