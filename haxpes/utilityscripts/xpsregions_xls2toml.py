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
    rname = str(rdict["Region Name"].lower()+"_xps")
    cl = rdict["Region Name"]
    etype = rdict["Energy Type"].lower()
    estart = rdict["Low Energy"]
    estop = rdict["High Energy"]
    estep = rdict["Step Size"]
    ostr = rname+" = { core_line = \""+cl+"\", energy_type = \""+etype+"\", energy_start = "+str(estart)+", energy_stop = "+str(estop)+", energy_step = "+str(estep)+", region_name = \""+cl+"\" }\n"
    fobj.write(ostr)

fobj.close()
    
