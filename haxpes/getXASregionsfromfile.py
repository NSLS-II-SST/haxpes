from pandas import read_excel

def read_XAS_from_file(filename):
    dfRegions = read_excel(filename,dtype=str)
    XAS_regions = {}
    for index, row in dfRegions.iterrows():
        rdict = row.to_dict()
        regname = rdict['Edge']
        XAS_regions[regname] = {}
        n_regions = int(rdict["Number of Regions"])
        steps = rdict["Step Sizes"].split(",")
        steps = [float(i) for i in steps]
        bounds = rdict["Region Bounds"].split(",")
        bounds = [float(i) for i in bounds]
        #check regions:
        if len(bounds) != n_regions+1:
            print("Error in bounds; number of bounds must be number of regions plus one.")
            return
        if len(steps) != n_regions:
            print("Error in step sizes; number of step sizes must be equal to number of regions.")
            return
        bounds = [b + float(rdict['E0']) for b in bounds] 
        for n in range(n_regions):
            XAS_regions[regname]["start_"+str(n)] = bounds[n]
            XAS_regions[regname]["stop_"+str(n)] = bounds[n+1]
            XAS_regions[regname]["step_"+str(n)] = steps[n]
        XAS_regions[regname]['n_regions'] = n_regions
    return XAS_regions

DefaultRegions = read_XAS_from_file("/home/xf07id1/collection_packages/haxpes/haxpes/DefaultXASRegions.xls")
