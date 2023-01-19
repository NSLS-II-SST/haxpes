from .motors import sampx, sampy, sampz, sampr
from bluesky.plan_stubs import mv
import numpy as np

class sample_list:
    
    def __init__(self):
        self.all_samples = []
        self.region_list = []
        self.index = 0

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
            "sample_name": name,
            "x_position": xpos,
            "y_position": ypos,
            "z_position": zpos,
            "r_position": rpos,
            "sample_index": self.index,
            "filename": filename,
            "regions": regions
        }
        self.all_samples.append(sample)
        self.index = self.index+1

    def list_samples(self):
        if self.all_samples == []:
            print("Empty sample list")
        else:
            for s in self.all_samples:
                print(str(s["sample_index"])+": "+s["sample_name"])

    def list_regions(self):
        if self.region_list == []:
            print("Empty region list")
        else:
            for r in self.region_list:
                print(r["reg_name"])
                print(r)

    def goto_sample(self,index):
        sample = self.all_samples[index]
        print("Moving to sample "+sample["sample_name"])
        yield from mv(sampy,sample["y_position"])
        yield from mv(
            sampx,sample["x_position"],
            sampz,sample["z_position"],
            sampr,sample["r_position"]
        )

    def make_region(self,region_name=None,center_energy=None,width=None,iterations=None,pass_energy=None,step_size=50):
        region = {
            "reg_name": region_name,
            "center_en": center_energy,
            "width": width,
            "iterations": iterations,
            "pass_energy": pass_energy,
            "step_size": step_size
        }
        return region

    def append_region_to_list(self,region_dict):
        if len(self.region_list) == 0:
            self.region_list.append(region_dict)
        else:
            for i in range(len(self.region_list)):
                if self.region_list[i]["reg_name"] == region_dict["reg_name"]:
                    self.region_list[i] = region_dict
                else:
                    self.region_list.append(region_dict)

    def read_regions_from_file(self,region_file):
        self.clear_region_list()
        self.append_regions_from_file(region_file)

    def append_regions_from_file(self,region_file):
        regnamelist = np.atleast_1d(
            np.genfromtxt(region_file,skip_header=1,delimiter='\t',dtype=str,usecols=0))
        centerlist = np.atleast_1d(
            np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=1))
        widthlist = np.atleast_1d(
            np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=2))
        passlist = np.atleast_1d(
            np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=3))
        itlist = np.atleast_1d(
            np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=4))
        steplist = np.atleast_1d(
            np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=5))

        for i in range(regnamelist.size):
            region = self.make_region(region_name=regnamelist[i],
                center_energy=centerlist[i],
                width=widthlist[i],
                pass_energy=passlist[i],
                iterations=itlist[i],
                step_size=steplist[i]
            )
            self.append_region_to_list(region)

    def read_from_file(self,region_file,sample_file):
        self.clear_sample_list()
        self.clear_region_list()
        self.read_regions_from_file(region_file)
        self.append_from_file(sample_file)

    def append_from_file(self,sample_file):
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
                    if sreg == reg["reg_name"]:
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

            
