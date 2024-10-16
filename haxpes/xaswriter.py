import numpy as np
from tiled.client import from_profile
from os.path import isfile

catalog = from_profile("haxpes")

def write_xas_file(uid,sum_sweeps=True):
    #grab the run by UID
    run = catalog[uid]

    uid_str = run.start['uid']
    
    #check if "XAS scan"
    if "purpose" not in run.start.keys():
        print("Data Type Unclear.  No data will be written.")
        return 0
    else:
        if run.start["purpose"] != "XAS Data":
            print("Not XPS data.  No data will be written.")
            return 0

    #record metadata:
    def get_md(md_key):
        if md_key in run.start.keys():
            return str(run.start[md_key])
        else:
            return "Unknown"

    xpos = get_md("Sample X")
    ypos = get_md("Sample Y")
    zpos = get_md("Sample Z")
    thpos = get_md("Sample Theta")
    E_fg = get_md("FG Energy")
    V_fg = get_md("FG V_grid")
    I_fg = get_md("FG I_emit")
    V_app = get_md("Applied Bias")

    file_comment = get_md("Comments")

    #get config data:
    configdat = run.primary.descriptors[0]['configuration']

    #for getting detector settings and data:
    def get_exposure_time(detector_key):
        if detector_key in run.metadata["start"]["detectors"]:
            keystr = detector_key+"_exposure_time"
            return str(configdat[detector_key]['data'][keystr])
        else:
            return "Unknown"

    def get_data(detector_key):
        if detector_key in run.metadata["start"]["detectors"]:
            return run.primary.read[detector_key].data

    I0_exposure = get_exposure_time('I0 ADC')
    Idrain_ADC_exposure = get_exposure_time('Idrain ADC')
    Idrain_K2600_exposure = get_exposure_time('K2600_current')
    I1_exposure = get_exposure_time('I1 ADC')

    data_array = run.primary.read()["SST2 Energy_energy"].data
    det_header = "\nEnergy"
    
    for detector_name in run.metadata["start"]["detectors"]:
        det_header = det_header+"\t"+detector_name.replace(" ","_")
        det_data = run.primary.read()[detector_name]
        data_array = np.column_stack((data_array,det_data))

    #check if export filename given, otherwise use UID ...:
    if "export filename" in run.start.keys() and run.start["export filename"] != None:
        fnum = 0
        filename = run.start["export filename"]+"_{:03d}.xy".format(fnum)
        while isfile(filename):
            fnum = fnum+1
            filename = run.start["export filename"]+"_{:03d}.xy".format(fnum)
    else:
        filename = "XAS_scan"+str(run.start["scan_id"])+".xy"
    
    header = "[Metadata]"+\
"\nScan UID="+uid_str+\
"\nComments="+file_comment+\
"\nFloodGun Emission="+I_fg+\
"\nFloodGun Energy="+E_fg+\
"\nFloodGun Grid Voltage="+V_fg+\
"\nSample X Position="+xpos+\
"\nSample Y Position="+ypos+\
"\nSample Z Position="+zpos+\
"\nSample Theta Position="+thpos+\
"\nApplied Bias="+V_app+\
"\nI0 Integration Time="+I0_exposure+\
"\nDrain Current Integration Time="+Idrain_ADC_exposure+\
"\nK2600B Integration Time="+Idrain_K2600_exposure+\
"\nI1 exposure Time="+I1_exposure+\
"\n\n------------------------------------------------------------------"+\
det_header

    np.savetxt(filename,data_array,delimiter='\t',header=header)

