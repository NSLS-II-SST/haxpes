
from sst_base.detectors.i400 import I400
from sst_base.detectors.f460 import F460

dm4_i400 = I400("XF:07ID-BI{DM4:I400-1}", name = "DM4 I400")
dm3_f460 = F460("XF:07ID-BI{DM3:F4}", name="DM3 F460")
dm4_f460 = F460("XF:07ID-BI{DM4:F4}", name="DM4 F460")
dm5_f460 = F460("XF:07ID-BI{DM5:F4}", name="DM5 F460")

