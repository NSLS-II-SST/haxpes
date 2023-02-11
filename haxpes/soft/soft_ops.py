from haxpes.energy_soft import ensoft, polsoft, hsoft, monosoft
from haxpes.soft.pgm_settings import pgmranges

#... check beam status ...


def set_photon_energy_soft(energySP,scanlock=1,use_optimal_harmonic=True):
    if use_optimal_harmonic:
        for r in pgmranges:
            if r["energymin"] <= enegySP < r["energymax"]:
                yield from mv(hsoft,r["harmonic"])
    yield from mv(ensoft,energySP)

