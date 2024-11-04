import numpy as np
from os.path import basename

class DataObject:
    def __init__(self):
        self.name = None
        self.label = None
        self.comment = None
        self.xraw = np.empty([])
        self.yraw = np.empty([])
        self.n_col = 0
        self.xcurrent = np.empty([])
        self.ycurrent = np.empty([])
        self.ysum = np.empty([])
        self.yavg = np.empty([])
        self.xaxis_type = "Kinetic"
        self.inputfile = None
        self.outputfile = None
        self.pass_energy = 0
        self.excitation_energy_raw = 0
        self.excitation_energy = 0
        self.n_sweeps = 0
        self.shift_ke = 0
        self.multiplier = 1.
        
    def _sum_ydata(self):
        self.ysum = self.multiplier*np.sum(self.ycurrent,axis=1)
        self.yavg = self.multiplier*np.mean(self.ycurrent,axis=1)
        
    def load_from_ascii(self,filepath,dataformat):
        self.inputfile = filepath
        self.name = basename(self.inputfile)
        self.label = basename(self.inputfile)
        if dataformat == "csv":
            delim = ","
        elif dataformat == "peak" or dataformat == "ses":
            delim = "\t"
        else:
            delim = "\t"
        self.xraw = np.genfromtxt(self.inputfile,delimiter=delim)[:,0]
        self.yraw = np.genfromtxt(self.inputfile,delimiter=delim)[:,1:]
        self._revert_data()
        self.n_col = self.ycurrent.shape[1]
        self._read_header()
    
    def _read_header(self):
        fobj = open(self.inputfile,'r')
        filelines = fobj.readlines()
        if "# [Metadata]\n" not in filelines:
            return
        else:
            for line in filelines:
                if "Pass Energy" in line:
                    self.pass_energy = int(float(line[line.index('=')+1:-1]))
                if "Energy Scale" in line:
                    self.xaxis_type = line[line.index('=')+1:-1]
                if "Comments" in line:
                    self.comment = line[line.index('=')+1:-1]
                if "Number of Sweeps" in line:
                    self.n_sweeps = int(float(line[line.index('=')+1:-1]))
                if line.startswith("# Excitation Energy"):
                    self.excitation_energy = float(line[line.index('=')+1:-1])
                    self.excitation_energy_raw = self.excitation_energy

    def _revert_data(self):
        self.ycurrent = np.array(self.yraw)
        self.xcurrent = np.array(self.xraw)
        self.shift_ke = 0
        self.excitation_energy = self.excitation_energy_raw
        self.label = self.name
        self.multiplier = 1.
        self._sum_ydata()

class DataDictionary:
    def __init__(self):
        self.clear_data()
        
    def append_data(self,dataname,dataobject):
        self.all_data[dataname] = dataobject
        
    def clear_data(self):
        self.all_data = {}
        
    def remove_data(self,dataname):
        del self.all_data[dataname]
