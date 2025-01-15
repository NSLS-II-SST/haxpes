"""
This is just commands ... not written into proper function yet.  
"""


run = c[-1]

edc_all = run.primary.read()['PeakAnalyzer_edc'].data
xd_all = run.primary.read()['PeakAnalyzer_xaxis'].data

hv_all = run.primary.read()['SST2 Energy_energy'].data

dnum = 0:
if run.start['export_filename']:
    basename = "./"+run.start['export_filename']
else:
    basename = "./ResPES"

dirname = basename+"_{:03d}".format(dnum)+
while os.path.isdir(dirname):
    dnum = dnum+1
    dirname = basename+"_{:03d}".format(dnum)
    
os.makedir(dirname)

regname = run.primary.descriptors[0]['configuration']['PeakAnalyzer']['data']['PeakAnalyzer_region_name']

for n in range(len(hv_all)):
    hv_str = str(round(hv_all[n],2))
    fpath = dirname+"/"+basename+"_"+regname+"_"+hv_str+".csv"
    xd = xd_all[n,:]
    yd = yd_all[n,:]
    od = np.column_stack((xd,yd))
    np.savetxt(fpath,od,header="Kinetic Energy (eV),Count",delimiter=',')

#get and write metadata

