from haxpes.energy_soft import ensoft as en, polsoft, hsoft, monosoft
from haxpes.soft.pgm_settings import pgmranges
from bluesky.plan_stubs import mv
from haxpes.hax_hw import psh5
from bluesky.plans import count
from haxpes.ses import ses

from haxpes.hax_ops import set_analyzer

from bluesky.preprocessors import suspend_decorator
from haxpes.hax_suspenders import *

suspendList = [suspend_FEsh1]
suspendList.append(suspend_psh4)
suspendList.append(suspend_psh5)
suspendList.append(suspend_beamstat)

suspendListSES = [suspend_FEsh1_SES]
suspendListSES.append(suspend_psh4_SES)
suspendListSES.append(suspend_psh5_SES)
suspendListSES.append(suspend_beamstat_SES)

@suspend_decorator(suspendList)
def set_photon_energy_soft(energySP,use_optimal_harmonic=True):
    if use_optimal_harmonic:
        for r in pgmranges:
            if r["energymin"] <= energySP < r["energymax"]:
                yield from mv(hsoft,r["harmonic"])
    yield from mv(en,energySP)

@suspend_decorator(suspendListSES)
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


@suspend_decorator(suspendList)
def run_peakXPS_soft(sample_list):
    from haxpes.scans import XPS_scan #import here for now, in case peak servers are not running
    for i in range(sample_list.index):
        if sample_list.all_samples[i]["To Run"]:
            print("Moving to sample "+str(i))
            yield from sample_list.goto_sample(i)
            #set photon energy ...
            current_en = en.position
            if current_en >= sample_list.all_samples[i]["Photon Energy"]+0.05 or current_en <= sample_list.all_samples[i]["Photon Energy"]-0.05:
                yield from set_photon_energy_soft(sample_list.all_samples[i]["Photon Energy"])
            ansetname = sample_list.all_samples[i]["AnalyzerSettings"]
            for settingdict in analyzer_sets:
                if settingdict["name"] == ansetname:
                    anset = settingdict
            for region in sample_list.all_samples[i]["regions"]:
                #get filename ... 
                fn = sample_list.all_samples[i]["File Prefix"]+\
str(round(sample_list.all_samples[i]["Photon Energy"]))+"eV_"+region["Region Name"]
                sample_list.en_cal = sample_list.all_samples[i]["Photon Energy"]
                reg = {}
                if region["Energy Type"] == "Binding":
                    reg["energy center"] = sample_list.en_cal - region["center_en"]
                else:
                    reg["energy center"] = region["center_en"]           
                reg["energy step"] = region["Step Size"]
                reg["region name"] = region["Region Name"]
                reg["energy width"] = float(region["width"])
                if sample_list.all_samples[i]["File Comments"] != "":
                    reg["description"] = sample_list.all_samples[i]["File Comments"]
                iterations = region["Iterations"]
                yield from XPS_scan(reg,iterations,anset,export_filename=fn) 
                if close_shutter:
                    yield from fs4.close()
        else:
            print("Skipping sample "+str(i))

