from haxpes.motors import dm1
from haxpes.energy_tender import mono, U42
from haxpes.detectors import Idm1
from bluesky.plan_stubs import mv
from bluesky.plans import rel_scan
import numpy as np
from haxpes.optimizers_test import find_max
from os.path import isdir, isfile, dirname
from haxpes.funcs import tune_x2pitch

Idm1.set_exposure(1)

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

   # yield from mv(dcm.mode,"full")

    #put photodiode in place
    yield from mv(dm1,32)

    if u42start:
        yield from mv(U42,u42start)

#    u42max = []

    #move U42 to initial position, scan will be about position +/- 100 um ??
#    yield from mv(u42gap,18078)

    for E in energy_range:
        yield from mv(mono.energy, E)
        yield from tune_x2pitch()
        yield from find_max(rel_scan,[Idm1],U42,-100,100,50,max_channel=Idm1.mean.name,hysteresis_correct=True)
        #u42max.append(u42gap.position)

        writeline = str(E)+"\t"+str(U42.position)+"\n"
        fobj = open(filepath,'a')  #open / close each step ... don't know if this is needed ...
        fobj.write(writeline)
        fobj.close()

    #outarray = np.column_stack((energy_range,u42max))
    #np.savetxt(filepath,outarray)

