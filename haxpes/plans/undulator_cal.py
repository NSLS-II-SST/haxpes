from haxpes.motors import dm1
from haxpes.energy_tender import mono, U42
from haxpes.devices.detectors import Idm1
from bluesky.plan_stubs import mv
from bluesky.plans import rel_scan
import numpy as np
from haxpes.optimizers_test import find_max
from os.path import isdir, isfile, dirname
from haxpes.funcs import tune_x2pitch

Idm1.set_exposure(1)

filepath = "/home/xf07id1/Documents/UserFiles/U42Cal/h11run.txt"
U42range = np.arange(11500, 13500, 50)


def runcal(filepath, U42_range, u42start=None, overwrite=False):

    # check direcotry is valid ...
    testpath = dirname(filepath)
    if not isdir(testpath):
        print("invalid directory")
        return

    # if file exists, will stop unless overwrite is set to True.  NOTE: Not tested!
    if not overwrite:
        if isfile(filepath):
            print(
                "file exists.  either select another file name or pass overwrite=True"
            )
            return

    fobj = open(
        filepath, "w"
    )  # open first in write mode, overwrites any previous run.  Be careful!
    fobj.write("Energy\tU42\n")
    fobj.close()
    #    fobj = open(filepath,'a')

    # yield from mv(dcm.mode,"full")

    # put photodiode in place
    yield from mv(dm1, 32)

    if u42start:
        yield from mv(U42, u42start)

    #    u42max = []

    # move U42 to initial position, scan will be about position +/- 100 um ??
    #    yield from mv(u42gap,18078)

    for U in U42_range:
        yield from mv(U42, U)
        # yield from tune_x2pitch()
        yield from find_max(
            rel_scan, [Idm1], mono.energy, -50, 50, 101, max_channel=Idm1.mean.name
        )
        # u42max.append(u42gap.position)

        writeline = str(mono.energy.position) + "\t" + str(U42.position) + "\n"
        fobj = open(
            filepath, "a"
        )  # open / close each step ... don't know if this is needed ...
        fobj.write(writeline)
        fobj.close()

    # outarray = np.column_stack((energy_range,u42max))
    # np.savetxt(filepath,outarray)
