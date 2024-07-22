from haxpes.peak_analyzer import peak_analyzer
from haxpes.detectors import I0, IK2600
from bluesky.plans import count, scan, list_scan
from bluesky.plan_stubs import mv
from haxpes.energy_tender import en
import numpy as np
from haxpes.motors import sampx, sampy, sampz, sampr

from bluesky.preprocessors import suspend_decorator
from haxpes.hax_suspenders import suspend_FEsh1, suspend_psh1, suspend_beamstat, suspend_psh2, suspend_fs4a

suspendList = [suspend_FEsh1]
suspendList.append(suspend_psh1)
suspendList.append(suspend_beamstat)
suspendList.append(suspend_psh2)
suspendList.append(suspend_fs4a)

default_dwell_time = 0.1
default_lens_mode = "Angular"
default_acq_mode = "Image"

detector_widths = {
    '500' : 40.,
    '200' : 16.,
    '100' : 8.,
    '50'  : 4.,
    '20'  : 1.6
}    

def setup_XPS(region_dictionary,analyzer_settings):
    peak_analyzer.setsweptmode()
    yield from mv(peak_analyzer.energy_center,region_dictionary["energy center"])
    yield from mv(peak_analyzer.energy_step,region_dictionary["energy step"])
    yield from mv(peak_analyzer.energy_width,region_dictionary["energy width"])
    yield from mv(peak_analyzer.region_name,region_dictionary["region name"])
    if "description" in region_dictionary.keys():
        yield from mv(peak_analyzer.description,region_dictionary["description"])

    yield from mv(peak_analyzer.pass_energy,analyzer_settings["pass energy"])
    if "dwell time" in analyzer_settings.keys():
        dwelltime = analyzer_settings["dwell time"]
    else:
        dwelltime = default_dwell_time
    yield from mv(peak_analyzer.dwell_time,dwelltime)
    if "lens mode" in analyzer_settings.keys():
        lensmode = analyzer_settings["lens mode"]
    else:
        lensmode = default_lens_mode 
    yield from mv(peak_analyzer.lens_mode,lensmode)
    if "acquisition mode" in analyzer_settings.keys():
        acqmode = analyzer_settings["acquisition mode"]
    else:
        acqmode = default_acq_mode
    yield from mv(peak_analyzer.acq_mode,acqmode)


def estimate_time(region_dictionary,analyzer_settings,number_of_sweeps):
    if "dwell time" in analyzer_settings.keys():
        dwelltime = analyzer_settings["dwell time"]
    else:
        dwelltime = default_dwell_time
    num_points = (region_dictionary["energy width"]+detector_widths[str(analyzer_settings["pass energy"])])/region_dictionary["energy step"]
    est_time = num_points*dwelltime 
    print("Estimated sweep time is "+str(est_time)+" s.  Setting I0 integration to "+str(est_time)+".")
    print("Estimated total time is "+str((est_time*number_of_sweeps)/60)+" min.")
    return est_time

@suspend_decorator(suspendList)
def XPS_scan(region_dictionary,number_of_sweeps,analyzer_settings,export_filename=None):
    yield from setup_XPS(region_dictionary,analyzer_settings)
    est_time = estimate_time(region_dictionary,analyzer_settings,number_of_sweeps)
    I0.set_exposure(est_time)

    #metadata for XPS scan:
    md = {}
    md["excitation energy"] = en.position
    md["purpose"] = "XPS Data"
    md["export filename"] = export_filename
    #input sample positions; note these should probably be put in generally.
    md["Sample X"] = sampx.position
    md["Sample Y"] = sampy.position
    md["Sample Z"] = sampz.position
    md["Sample Theta"] = sampr.position
   
    yield from count([I0,peak_analyzer],number_of_sweeps,md=md)


@suspend_decorator(suspendList)
def ResPES_scan(XPSregion,EnergyRegion,analyzer_settings,n_sweeps,export_filename=None):
    """performs resonance scan using PEAK analyzer.
    Currently records only peak analyzer and I0.  
    TO DO: add other detectors
    Currently only performs 1 XPS sweep per energy.  
    TODO: figure out multiple sweeps
    XPSregion is a dictionary which should contain keys "energy center", "energy width", "energy step", "region name".
    XPSregion has optional key "description" for sample comments but this can be left empty.
    analyzer_settings should be dictionary with keys "pass energy"
    analyzer_settings has optional keys "dwell time", "lens mode", and "acquisition mode.  These will default to default values if they are not set."
    EnergyRegion is a dictionary with keys:
    - n_regions (integer)
    - start_<n> where <n> is the region number starting from 0 for each region.
    - stop_<n> where <n> is the region number starting from 0 for each region.
    - step_<n> where <n> is the region number start from 0 for each region.
    """
    yield from setup_XPS(XPSregion,analyzer_settings)
    est_time = estimate_time(XPSregion,analyzer_settings,1)
    I0.set_exposure(est_time)
    fullrange = np.empty(0,)
    for reg in range(EnergyRegion["n_regions"]):
        start_energy = EnergyRegion["start_"+str(reg)]
        stop_energy = EnergyRegion["stop_"+str(reg)]
        step_size = EnergyRegion["step_"+str(reg)]
        reg_range = np.arange(start_energy,stop_energy,step_size)
        fullrange = np.concatenate((fullrange,reg_range),axis=0)
    en_list = fullrange.tolist()
    #medata
    md = {}
    md["purpose"] = "Resonant XPS Data"
    md["export_filename"] = export_filename
    md["Sample X"] = sampx.position
    md["Sample Y"] = sampy.position
    md["Sample Z"] = sampz.position
    md["Sample Theta"] = sampr.position

    for sweep in range(n_sweeps):
        yield from list_scan([I0,peak_analyzer],en,en_list,md=md)

    

#TO DO: XAS Scan ... think of how to include Scienta settings.
#NOTE: For alignment scans, this is also important ...
#def XAS_setup(detector_list,exposure_time):
#    for detector in detector_list:
#        detector.set_exposure(exposure_time)
#        print("setting exposure time of "+detector.name+" to "+str(exposure_time)+" s.")

#def XAS_linscan(edge_dictionary,detector_list,exposure_time,n_sweeps=1):
#    """ performs XAS scan with a linear trajectory using settings in edge_dictionary.
#   edge_dictionary should have keys: start_energy, stop_energy, n_steps.
#    convert step size to number of steps elsewhere.
#   detector_list is list of detector objects.  They should all have function "set_exposure"
#    exposure_time is a float.
#    """
#    XAS_setup(detector_list,exposure_time)
#    for sweep in range(n_sweeps):
#        yield from scan(detector_list,en,edge_dictionary["start_energy"],\
#edge_dictionary["stop_energy"],edge_dictionary["n_steps"])

#def XAS_scan(edge_dictionary,detector_list,exposure_time,n_sweeps=1):
#    """ peforms XAS scan with multiple regions
#    edge_dictionary should have have keys:
#    - n_regions (integer)
#    - start_<n> where <n> is the region number starting from 0 for each region.
#    - stop_<n> where <n> is the region number starting from 0 for each region.
#   - step_<n> where <n> is the region number start from 0 for each region.
#    """
#    fullrange = np.empty(0,)
#    for reg in range(edge_dictionary["n_regions"]):
#        start_energy = edge_dictionary["start_"+str(reg)]
#        stop_energy = edge_dictionary["stop_"+str(reg)]
#        step_size = edge_dictionary["step_"+str(reg)]
#        reg_range = np.arange(start_energy,stop_energy,step_size)
#        fullrange = np.concatenate((fullrange,reg_range),axis=0)
#    en_list = fullrange.tolist()
#    XAS_setup(detector_list,exposure_time)
#    for sweep in range(n_sweeps):
#        yield from list_scan(detector_list,en,en_list)

