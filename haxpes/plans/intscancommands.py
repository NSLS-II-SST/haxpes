from haxpes.hax_runner import RE
from haxpes.detectors import Idm1
from haxpes.energy_tender import en, h
from haxpes.funcs import tune_x2pitch
import numpy as np
from bluesky.plan_stubs import mv, sleep


def runintscan():
    harmonics = [5, 7, 9]

    datadir = "/home/xf07id1/Documents/UserFiles/U42Cal/"

    erange = np.arange(3250,8000,50)

    for harm in harmonics:
        h.set(harm)
        fpath = datadir+"int_h"+str(harm)+".txt"

        for E in erange:
            Idm1.set_exposure(0.5)
            RE(mv(en,E))
            RE(tune_x2pitch())
            Idm1.set_exposure(10)
            Idm1.trigger()
            print("waiting")
            RE(sleep(15))
            Idiode = Idm1.mean.get()
            f = open(fpath,'a')
            f.write(str(E)+'\t'+str(Idiode)+'\n')
            f.close()

