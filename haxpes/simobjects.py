from ophyd import Device, Signal

ensoft = Signal(name="Soft Energy Sim", kind="hinted", value=None)
polsoft = Signal(name="Soft Polarization Sim", kind="hinted", value=0)
hsoft = Signal(name="Soft Harmonic Sim", kind="hinted", value=1)
monosoft = Signal(name="Soft PGM Sim", kind="hinted", value=None)
