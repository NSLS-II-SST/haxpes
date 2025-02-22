from pandas import read_excel
import sys
from os.path import splitext, basename

try:
    f_in = sys.argv[1]
except IndexError:
    print("No file given.  Exiting.  Please call function with valid file name.")
    sys.exit()

f_out = splitext(basename(f_in))[0]+".toml"

try:
    dfRegions = read_excel(f_in)
except FileNotFoundError:
    print("File "+f_in+" does not exist.  Exiting.  Please call function with valid file name.")
    sys.exit()
except ValueError:
    print("File "+f_in+" is not a valid xls file.  Exiting.")
    sys.exit()
except:
    print("Something else went wrong.  I don't know!")
    sys.exit()

print("converting "+f_in+" into "+f_out)

fobj = open(f_out,'a')

for index, row in dfRegions.iterrows():
    rdict = row.to_dict()
    ename = str(rdict["Edge"].lower()+"_xas")
    edge = str(rdict["Edge"])
    name = edge+" XAS"
    e0 = float(rdict["E0"])
    nreg = int(rdict["Number of Regions"])
    bounds = rdict["Region Bounds"].split(",")
    bounds = [e0+float(b) for b in bounds]
    bounds = [str(b) for b in bounds]

    start = str(bounds[0])
    oline = ename+" = { edge = \""+edge+"\", region = ["+start+", "

    if nreg > 1:
        stepsizelist = rdict["Step Sizes"].split(",")
        for n in range(nreg-1):
            oline = oline + bounds[n+1]+", "+stepsizelist[n]+", "
        oline = oline + bounds[-1]+", "+stepsizelist[-1]+"]"
    elif nreg == 1:
        oline = oline + bounds[-1]+", "+str(rdict["Step Sizes"])+"]"

    oline = oline+", name = \""+name+"\"}\n"

    fobj.write(oline)

fobj.close()
    

