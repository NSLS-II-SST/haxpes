from haxpes.dcm import dcm
from haxpes.motors import u42gap, dm1
from haxpes.detectors import dm3_f460
from bluesky.plan_stubs import mv
from bluesky.plans import rel_scan
import numpy as np
from sst_funcs.plans.maximizers import find_max
from os.path import isdir, isfile, dirname

def runcal(filepath,energy_range,u42start=None,overwrite=False):

    #check direcotry is valid ...
    testpath = dirname(filepath)
    if not isdir(testpath):
        print("invalid directory")
        return

    #if file exists, will stop unless overwrite is set to True.  NOTE: Not tested!
    if not overwrite:
        if isfile(filepath):
            print("file exists.  either select another file name or pass overwrite=True")
            return

    fobj = open(filepath,'w') #open first in write mode, overwrites any previous run.  Be careful!
    fobj.write("Energy\tU42\n")
    fobj.close()
#    fobj = open(filepath,'a')

    yield from mv(dcm.mode,"full")

    #put photodiode in place
    yield from mv(dm1,32)

    if u42start:
        yield from mv(u42gap,u42start)

#    u42max = []

    #move U42 to initial position, scan will be about position +/- 100 um ??
#    yield from mv(u42gap,18078)

    for en in energy_range:
        yield from mv(dcm.energy, en)
        yield from find_max(rel_scan,[dm3_f460],u42gap,-100,100,50,max_channel=dm3_f460.i3.name)
        #u42max.append(u42gap.position)

        writeline = str(en)+"\t"+str(u42gap.position)+"\n"
        fobj = open(filepath,'a')  #open / close each step ... don't know if this is needed ...
        fobj.write(writeline)
        fobj.close()

    #outarray = np.column_stack((energy_range,u42max))
    #np.savetxt(filepath,outarray)

