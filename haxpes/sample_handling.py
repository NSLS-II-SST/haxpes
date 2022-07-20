from .motors import sampx, sampy, sampz, sampr
from bluesky.plan_stubs import mv
import numpy as np

class sample_list:
    
    def __init__(self):
        self.all_samples = []
        self.index = 0

    def clear_list(self):
        self.all_samples = []
        self.index = 0

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

    def goto_sample(self,index):
        sample = self.all_samples[index]
        print("Moving to sample "+sample["sample_name"])
        yield from mv(sampy,sample["y_position"])
        yield from mv(
            sampx,sample["x_position"],
            sampz,sample["z_position"],
            sampr,sample["r_position"]
        )

    def add_region(self,index,region):
        self.all_samples[index]["regions"].append(region)

    def read_from_file(self,region_file,sample_file):
        self.clear_list()
        self.append_from_file(region_file,sample_file)

    def append_from_file(self,region_file,sample_file):
        regnamelist = np.genfromtxt(
            region_file,skip_header=1,delimiter='\t',dtype=str,usecols=0)
        centerlist = np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=1)
        widthlist = np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=2)
        passlist = np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=3)
        itlist = np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=4)
        steplist = np.genfromtxt(region_file,skip_header=1,delimiter='\t',usecols=5)

        namelist = np.genfromtxt(sample_file,skip_header=1,delimiter='\t',dtype=str,usecols=0)
        xlist = np.genfromtxt(sample_file,skip_header=1,delimiter='\t',usecols=1)
        ylist = np.genfromtxt(sample_file,skip_header=1,delimiter='\t',usecols=2)
        zlist = np.genfromtxt(sample_file,skip_header=1,delimiter='\t',usecols=3)
        rlist = np.genfromtxt(sample_file,skip_header=1,delimiter='\t',usecols=4)
        flist = np.genfromtxt(sample_file,skip_header=1,delimiter='\t',dtype=str,usecols=5)
        reglist = np.genfromtxt(sample_file,skip_header=1,delimiter='\t',dtype=str,usecols=6)
        for i in range(0,namelist.shape[0]):
            region_list = reglist[i].split(", ")
            scanregions = []
            for region in region_list:
                reg_index = int(np.where(regnamelist == region)[0][0])
                reg_parameters = {
                    "reg_name": regnamelist[reg_index],
                    "center_en": centerlist[reg_index],
                    "width": widthlist[reg_index],
                    "iterations": itlist[reg_index],
                    "pass_energy": passlist[reg_index],
                    "step_size": steplist[reg_index]
                }
                scanregions.append(reg_parameters)
            self.add_sample(
                namelist[i],
                xpos=xlist[i],
                ypos=ylist[i],
                zpos=zlist[i],
                rpos=rlist[i],
                filename=flist[i],
                regions=scanregions
            )

        
        
