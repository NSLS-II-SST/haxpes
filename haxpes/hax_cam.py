from ophyd import Device, Component as Cpt, EpicsSignal, EpicsSignalRO
from bluesky.plan_stubs import mv, sleep
#from time import sleep

class simpleBPM(Device):
    centX = Cpt(EpicsSignalRO,"Stats1:CentroidX_RBV", kind="hinted")
    centY = Cpt(EpicsSignalRO,"Stats1:CentroidY_RBV", kind="hinted")
    threshold = Cpt(EpicsSignal,"Stats1:CentroidThreshold", kind="config")
    compCent = Cpt(EpicsSignal,"Stats1:ComputeCentroid", kind="config")
    compStats = Cpt(EpicsSignal,"Stats1:ComputeStatistics", kind="config")
    maxval = Cpt(EpicsSignalRO,"Stats1:MaxValue_RBV", kind="hinted")
    minval = Cpt(EpicsSignalRO,"Stats1:MinValue_RBV", kind="hinted")
    acqtime = Cpt(EpicsSignal,"cam1:AcquireTime", kind="config")
    datatype = Cpt(EpicsSignalRO,"cam1:DataType_RBV", kind="config")

    def adjust_gain(self):
        yield from mv(self.acqtime,1)
        yield from sleep(5.0)
        scale = self.datatype.get()
        print(scale)
        if scale == 0: #UInt8
            datamax = 255
        elif scale == 1: #UInt16
            datamax = 65535
        m = self.maxval.get()
        while  m >= datamax:
            current_acqtime = self.acqtime.get()
            yield from mv(self.acqtime,current_acqtime / 2)
            yield from sleep(1)
            m = self.maxval.get()
