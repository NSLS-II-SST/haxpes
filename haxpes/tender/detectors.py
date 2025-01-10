from sst_base.detectors.scalar import ophScalar

# In devices.toml
Idm1 = ophScalar("XF:07ID-BI{DM3:F4}Cur:I2-I", name="DM1 Photodiode")

I1 = ophScalar("XF:07ID-BI[ADC:1-Ch:2]Volt", name="I1 ADC")
