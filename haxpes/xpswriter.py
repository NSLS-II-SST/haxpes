import numpy as np
from tiled.client import from_profile

catalog = from_profile("haxpes")

def write_xps_file(uid,filename=None,sum_sweeps=True):
    #grab the run by UID
    run = catalog[uid]
    
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

    I0_data = str(run.primary.read()["I0 ADC"].data)
    
    #write to file ...
    if not filename:
        filename = "HAXPES_"+str(uid)+".txt"
    
    header = "[Metadata]\n"+\
"Region Name="+reg_name+\
"\nPass Energy="+pass_energy+\
"\nLens Mode="+lens_mode+\
"\nAcquisition Mode="+acq_mode+\
"\nScan Mode=Swept"+\
"\nEnergy Scale=Kinetic"+\
"\nComments="+file_comment+\
"\nNumber of Sweeps="+nsweeps+\
"\nI0="+I0_data+\
"\n\n[Data]"

    np.savetxt(filename,output_array,delimiter='\t',header=header,comments='')

