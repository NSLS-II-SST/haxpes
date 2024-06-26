#XPS scan:
# Inputs:
# - energy region:
#   - energy center
#   - energy width
#   - energy step
# - analyzer settings:
#   - swept mode !
#   - pass energy
#   - dwell time (default = 0.1)
#   - lens mode (default = "Angular")
#   - acquisition mode (default = "Image")
# - number of sweeps
# Signals:
# - peak_analyzer
# - I0
# - drain current (**)
# - Keithley bias
# Other thoughts:
# - get analyzer and detector settings before scan??
# - bs scan is 'count'

# region name = acqClient.spectrum_definition.name
# comments = acqClient.spectrum_definition.description

from haxpes.peak_analyzer import peak_analyzer
from haxpes.detectors import I0, IK2600
from bluesky.plans import count, scan, list_scan
from bluesky.plan_stubs import mv
from haxpes.energy_tender import en
import numpy as np

default_dwell_time = 0.1
default_lens_mode = "Angular"
default_acq_mode = "Image"

def XPS_scan(region_dictionary,number_of_sweeps,analyzer_settings):
    """performs XPS sweep.  
    region_dictionary should contain keys "energy center", "energy width", "energy step", "region name".
    energies are in Kinetic energy!  conversion from binding energy should be done externally.
    region_dictionary has optional key "description" for sample comments but this can be left empty.
    analyzer_settings should be dictionary with keys "pass energy"
    analyzer_settings has optional keys "dwell time", "lens mode", and "acquisition mode.  These will default to default values if they are not set."
    number of sweeps must be an integer.
    """
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

    # TO DO:estimate scan time and set other exposures to estimated scan time.

    yield from count([peak_analyzer,I0,IK2600],number_of_sweeps)


def XAS_setup(detector_list,exposure_time):
    for detector in detector_list:
        detector.set_exposure(exposure_time)
        print("setting exposure time of "+detector.name+" to "+str(exposure_time)+" s.")

def XAS_linscan(edge_dictionary,detector_list,exposure_time,n_sweeps=1):
    """ performs XAS scan with a linear trajectory using settings in edge_dictionary.
    edge_dictionary should have keys: start_energy, stop_energy, n_steps.
    convert step size to number of steps elsewhere.
    detector_list is list of detector objects.  They should all have function "set_exposure"
    exposure_time is a float.
    """
    XAS_setup(detector_list,exposure_time)
    for sweep in range(n_sweeps):
        yield from scan(detector_list,en,edge_dictionary["start_energy"],\
edge_dictionary["stop_energy"],edge_dictionary["n_steps"])

def XAS_scan(edge_dictionary,detector_list,exposure_time,n_sweeps=1):
    """ peforms XAS scan with multiple regions
    edge_dictionary should have have keys:
    - n_regions (integer)
    - start_<n> where <n> is the region number starting from 0 for each region.
    - stop_<n> where <n> is the region number starting from 0 for each region.
    - step_<n> where <n> is the region number start from 0 for each region.
    """
    fullrange = np.empty(0,)
    for reg in range(edge_dictionary["n_regions"]):
        start_energy = edge_dictionary["start_"+str(reg)]
        stop_energy = edge_dictionary["stop_"+str(reg)]
        step_size = edge_dictionary["step_"+str(reg)]
        reg_range = np.arange(start_energy,stop_energy,step_size)
        fullrange = np.concatenate((fullrange,reg_range),axis=0)
    en_list = fullrange.tolist()
    XAS_setup(detector_list,exposure_time)
    for sweep in range(n_sweeps):
        yield from list_scan(detector_list,en,en_list)


#XAS scan:
# inputs:
# - energy points ...
# - detector settings
# - number of sweeps
# - detector settings:
#   - peak_analzyer:
#     - exposure time
#     - fixed mode !
#     - dwell time (default = exposure time)
#     - lens mode (default = "Angular")
#     - acq. mode (default = "Image")
#     - energy center
#     - pass energy
#   - Keithley:
#     - measure current range
#     - measure voltage range
#     - exposure time
#   - I0:
#     - range (*)
#     - exposure time 
# Signals:
# - peak_analzyer
# - I0
# - drain current (**)
# - Keithley bias 
# Other thoughts:
# - get analyzer and detector settings before scan ??
