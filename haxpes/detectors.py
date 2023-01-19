
from sst_base.detectors.i400 import I400
from sst_base.detectors.f460 import F460
from .hax_cam import simpleBPM
from sst_base.detectors.scalar import ADCBuffer

dm4_i400 = I400("XF:07ID-BI{DM4:I400-1}", name = "DM4 I400")
dm3_f460 = F460("XF:07ID-BI{DM3:F4}", name="DM3 F460")
dm4_f460 = F460("XF:07ID-BI{DM4:F4}", name="DM4 F460")
dm5_f460 = F460("XF:07ID-BI{DM5:F4}", name="DM5 F460")

BPM4cent = simpleBPM("XF:07ID-BI{BPM:4}",name = "BPM4 Centroid")

I0 = ADCBuffer("XF:07ID-BI[ADC:1-Ch:1]",name="I0 ADC")
Idrain = ADCBuffer("XF:07ID-BI[ADC:1-Ch:0]",name="Sample Drain Current")
