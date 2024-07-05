import numpy as np
from tiled.client import from_profile

catalog = from_profile("haxpes")

def write_xps_file(uid,sum_sweeps=True):
    #grab the run by UID
    run = catalog[uid]

    uid_str = run.start['uid']
    
    #check if "XPS scan"
    if "purpose" not in run.start.keys():
        print("Data Type Unclear.  No data will be written.")
        return 0
    else:
        if run.start["purpose"] != "XPS Data":
            print("Not XPS data.  No data will be written.")
            return 0

    #get PEAK analyzer config data:
    configdat = run.primary.descriptors[0]['configuration']
    peak_config = configdat['PeakAnalyzer']['data']
    
    pass_energy = str(peak_config['PeakAnalyzer_pass_energy'])
    lens_mode = peak_config['PeakAnalyzer_lens_mode']
    acq_mode = peak_config['PeakAnalyzer_acq_mode']
    reg_name = peak_config['PeakAnalyzer_region_name']
    file_comment = peak_config['PeakAnalyzer_description']
    dwell_time = str(peak_config['PeakAnalyzer_dwell_time']) #think about formatting.

    #get I0 config data:
    I0_config = configdat['I0 ADC']['data'] #think about renaming ...
    I0_exposure_time = str(I0_config['I0 ADC_exposure_time'])

    #read data; sum all sweeps.
    energy_axis = run.primary.read()["PeakAnalyzer_xaxis"].data[0,:]  #use only the first xaxis, they all should be the same
    imdat = run.primary.read()["PeakAnalyzer_edc"].data 
    nsweeps = str(imdat.shape[0])
    if sum_sweeps:
        edc = imdat.sum(axis=0)
    else:
        edc = np.transpose(imdat)
    output_array = np.column_stack((energy_axis,edc))

    if "excitation energy" in run.start.keys():
        hv = str(run.start["excitation energy"])
    else:
        hv = "0"

    I0_data = str(run.primary.read()["I0 ADC"].data)

    #check if export filename given, otherwise use UID ...:
    if "export filename" in run.start.keys() and run.start["export filename"] != None:
        filename = run.start["export filename"]
    else:
        filename = "HAXPES_scan"+str(run.start["scan_id"])+"_"+reg_name+".xy"
    
    header = "[Metadata]"+\
"\nRegion Name="+reg_name+\
"\nScan UID="+uid_str+\
"\nPass Energy="+pass_energy+\
"\nLens Mode="+lens_mode+\
"\nAcquisition Mode="+acq_mode+\
"\nScan Mode=Swept"+\
"\nEnergy Scale=Kinetic"+\
"\nComments="+file_comment+\
"\nNumber of Sweeps="+nsweeps+\
"\nExcitation Energy = "+hv+\
"\nI0="+I0_data+\
"\n\n[Data]"

    np.savetxt(filename,output_array,delimiter='\t',header=header)

