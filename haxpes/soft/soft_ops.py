from haxpes.energy_soft import ensoft as en, polsoft, hsoft, monosoft
from haxpes.soft.pgm_settings import pgmranges
from bluesky.plan_stubs import mv
from haxpes.hax_hw import psh5
from bluesky.plans import count
from haxpes.ses import ses

from haxpes.hax_ops import set_analyzer

#... check beam status ...


def set_photon_energy_soft(energySP,use_optimal_harmonic=True):
    if use_optimal_harmonic:
        for r in pgmranges:
            if r["energymin"] <= energySP < r["energymax"]:
                yield from mv(hsoft,r["harmonic"])
    yield from mv(ensoft,energySP)


def run_XPS_soft(sample_list):
    yield from psh5.open() #in case it is closed.  It should be open.
    for i in range(sample_list.index):
        if sample_list.all_samples[i]["To Run"]:
            print("Moving to sample "+str(i))
            yield from sample_list.goto_sample(i)
            #set photon energy ...
            current_en = en.position
            if current_en >= sample_list.all_samples[i]["Photon Energy"]+0.05 or current_en <= sample_list.all_samples[i]["Photon Energy"]-0.05:
                yield from set_photon_energy_soft(sample_list.all_samples[i]["Photon Energy"])
            for region in sample_list.all_samples[i]["regions"]:
                sample_list.en_cal = sample_list.all_samples[i]["Photon Energy"]
#                if region["Energy Type"] == "Binding":
#                    sample_list.calc_KE(region)
                yield from set_analyzer(sample_list.all_samples[i]["File Prefix"],region,sample_list.en_cal)
               #yield from fs4.open() #in case it is closed ...
                yield from count([ses],1)
        else:
            print("Skipping sample "+str(i))
