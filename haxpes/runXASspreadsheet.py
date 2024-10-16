from haxpes.motors import sampx, sampy, sampz, sampr
from bluesky.plan_stubs import mv
import numpy as np
from pandas import read_excel
from haxpes.getXASregionsfromfile import DefaultRegions
from haxpes.tender.tender_ops import set_photon_energy_tender as set_photon_energy
from haxpes.detectors import I0, IK2600
from haxpes.scans import XAS_scan

def runXASspreadsheet(filename,regions=None):
    ScanList = []

    if regions == None:
        regions = DefaultRegions

    dfSample = read_excel(filename)
    for index, row in dfSample.iterrows():
        sdict = row.dropna().to_dict()
        #check if we have the region:
        if sdict['Edge'] not in regions.keys():
            print("No region named "+sdict["Edge"])
            return
        ScanList.append(sdict)
        sdict["Filename"] = sdict["Sample Name"]+"_"+sdict["Edge"]

    current_edge = ScanList[0]["Edge"]
    for scanitem in ScanList:
        if scanitem["Edge"] != current_edge:
            current_edge == scanitem["Edge"]
            if "E0" in regions["Edge"].keys():
                print("Changing photon energy and aligning ...")
                yield from set_photon_energy(get_align_energy(current_region))
                #align beam XAS ....
        yield from mv(sampy,scanitem["Sample Y"])
        yield from mv(sampx,scanitem["Sample X"],sampz,scanitem["Sample Z"],sampr,scanitem["Sample Theta"])
        if "Comments" in scanitem.keys():
            comment = scanitem["Comments"]
        else:
            comment = None
        print(scanitem.keys())
        yield from XAS_scan(regions[current_edge],[I0, IK2600],scanitem["Integration"],n_sweeps=scanitem["Sweeps"],export_filename=scanitem["Filename"],comments=comment)

def get_align_energy(region_dictionary):
    stop_vals = []
    if "E0" in region_dictionary.keys():
        align_val = region_dictionary["E0"]
    else:
        for k in region_dictionary.keys():
            if "stop_" in k:
                stop_vals.append(region_dictionary[k])
    align_val = round((max(stop_vals) + region_dictionary["start_0"]) / 2)
    return align_val
