from sst_hw.energy import EnPos
from haxpes.motors import sampr

enpos = EnPos("", rotation_motor=sampr, name="en")
enpos.scanlock.set(1)

ensoft = enpos.energy
polsoft = enpos.polarization
hsoft = enpos.harmonic
monosoft = enpos.monoen
undulatorgapsoft = enpos.epugap
