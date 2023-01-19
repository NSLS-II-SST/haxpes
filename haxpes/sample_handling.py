from .motors import sampx, sampy, sampz, sampr
from bluesky.plan_stubs import mv
import numpy as np
from pandas import read_excel

class sample_list:
    
    def __init__(self):
        self.all_samples = []
        self.region_list = []
        self.index = 0
        self.en_cal = None

    def clear_sample_list(self):
        self.all_samples = []
        self.index = 0

    def clear_region_list(self):
        self.region_list = []

    def add_sample(self,name,filename=None,xpos=None,ypos=None,zpos=None,rpos=None,regions=[]):
        """ adds sample to sample list.  If positions are not defined, they will be taken as the current motor positions """
        if not xpos:
            xpos = sampx.position
        if not ypos:
            ypos = sampy.position
        if not zpos:
            zpos = sampz.position
        if not rpos:
            rpos = sampr.position

        if not filename:
            filename = name.replace(" ","_")+"_"

        sample = {
            "Sample Name": name,
            "X Position": xpos,
            "Y Position": ypos,
            "Z Position": zpos,
            "Th Position": rpos,
            "sample_index": self.index,
            "File Prefix": filename,
            "regions": regions
        }
        self.all_samples.append(sample)
        self.index = self.index+1

    def list_samples(self):
        if self.all_samples == []:
            print("Empty sample list")
        else:
            for s in self.all_samples:
                print(str(s["sample_index"])+": "+s["Sample Name"])

    def list_regions(self):
        if self.region_list == []:
            print("Empty region list")
        else:
            for r in self.region_list:
                print(r["Region Name"])
                print(r)

    def goto_sample(self,index):
        sample = self.all_samples[index]
        print("Moving to sample "+str(sample["sample_index"])+": "+sample["Sample Name"])
        yield from mv(sampy,sample["Y Position"])
        yield from mv(
            sampx,sample["X Position"],
            sampz,sample["Z Position"],
            sampr,sample["Th Position"]
        )

    def make_region(self,region_name=None,center_energy=None,width=None,iterations=None,pass_energy=None,step_size=50):
        region = {
            "Region Name": region_name,
            "center_en": center_energy,
            "width": width,
            "iterations": iterations,
            "pass_energy": pass_energy,
            "Step Size": step_size,
            "Excitation Energy": self.en_cal
        }
        return region

    def append_region_to_list(self,region_dict):
        if len(self.region_list) == 0:
            self.region_list.append(region_dict)
        else:
            for i in range(len(self.region_list)):
                if self.region_list[i]["Region Name"] == region_dict["Region Name"]:
                    self.region_list[i] = region_dict
                else:
                    self.region_list.append(region_dict)

    def read_regions_from_text(self,region_file):
        self.clear_region_list()
        self.append_regions_from_file(region_file)

    def read_from_text(self,region_file,sample_file):
        self.clear_sample_list()
        self.clear_region_list()
        self.read_regions_from_file(region_file)
        self.append_from_file(sample_file)

    def read_from_file(self,excel_file):
        self.clear_sample_list()
        self.clear_region_list()
        self.append_from_file(excel_file)
        
    def append_from_file(self,excel_file):
        #read regions
        dfRegions = read_excel(excel_file,sheet_name="Regions")
        for index, row in dfRegions.iterrows():
            rdict = row.to_dict()
            rdict["Excitation Energy"] = self.en_cal
            self.region_list.append(rdict)
        #read samples ... 
        dfSamples = read_excel(excel_file,sheet_name="Samples")
        for index, row in dfSamples.iterrows():
            sdict = row.dropna().to_dict()
            sdict["regions"] = []
            for r in ["Region 1", "Region 2", "Region 3", "Region 4", "Region 5", "Region 6", "Region 7", "Region 8", "Region 9", "Region 10"]:
                if r in sdict:
                    for rdict in self.region_list:
                        if sdict[r] == rdict["Region Name"]:
                            rdict["center_en"] = (rdict["Low Energy"] + rdict["High Energy"])/2
                            rdict["width"] = np.abs(rdict["High Energy"] - rdict["Low Energy"])
                            if rdict["Energy Type"] == "Binding":
                                rdict["center_en"] = self.en_cal - rdict["center_en"]
                            sdict["regions"].append(rdict)
            sdict["sample_index"] = self.index
            self.all_samples.append(sdict)
            self.index = self.index+1

    def append_from_text(self,sample_file):
        namelist = np.atleast_1d(
            np.genfromtxt(sample_file,skip_header=1,delimiter='\t',dtype=str,usecols=0))
        xlist = np.atleast_1d(
            np.genfromtxt(sample_file,skip_header=1,delimiter='\t',usecols=1))
        ylist = np.atleast_1d(
            np.genfromtxt(sample_file,skip_header=1,delimiter='\t',usecols=2))
        zlist = np.atleast_1d(
            np.genfromtxt(sample_file,skip_header=1,delimiter='\t',usecols=3))
        rlist = np.atleast_1d(
            np.genfromtxt(sample_file,skip_header=1,delimiter='\t',usecols=4))
        flist = np.atleast_1d(
            np.genfromtxt(sample_file,skip_header=1,delimiter='\t',dtype=str,usecols=5))
        regliststr = np.atleast_1d(
            np.genfromtxt(sample_file,skip_header=1,delimiter='\t',dtype=str,usecols=6))
        for i in range(namelist.size):
            sample_regions = regliststr[i].split(", ")
            for sreg in sample_regions:
                region_dicts = []
                for reg in self.region_list:
                    if sreg == reg["Region Name"]:
                        region_dicts.append(reg)
            self.add_sample(
                namelist[i],
                xpos=xlist[i],
                ypos=ylist[i],
                zpos=zlist[i],
                rpos=rlist[i],
                filename=flist[i],
                regions=region_dicts
            )

            
