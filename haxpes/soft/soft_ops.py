from haxpes.energy_soft import ensoft, polsoft, hsoft, monosoft
from haxpes.soft.pgm_settings import pgmranges
from bluesky.plan_stubs import mv

#... check beam status ...


def set_photon_energy_soft(energySP,use_optimal_harmonic=True):
    if use_optimal_harmonic:
        for r in pgmranges:
            if r["energymin"] <= energySP < r["energymax"]:
                yield from mv(hsoft,r["harmonic"])
    yield from mv(ensoft,energySP)

