from sst_base.detectors.scalar import ophScalar
from sst_base.detectors.scalar import ophScalar

M4Adrain = ophScalar("XF:07ID-BI[ADC:1-Ch:2]Volt",name="M4A Drain Current")
Idm3 = ophScalar("XF:07ID-BI{DM3:F4}Cur:I0-I",name="DM3 Photodiode")
Idm4 = ophScalar("XF:07ID-BI{DM5:F4}Cur:I1-I",name="DM4 Photodiode") #check ...
