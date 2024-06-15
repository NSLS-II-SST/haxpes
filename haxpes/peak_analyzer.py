from ophyd import Device, Component as Cpt, Signal
import peak
from peak.types.peak_axis_mode import PeakAxisMode
from peak.types.peak_axis import PeakAxis
from peak.types.peak_acquisition_mode import PeakAcquisitionMode
from ophyd.status import SubscriptionStatus
from time import sleep
import threading
import numpy as np

class _updatemonitor(threading.Thread):
    def __init__(self, statussignal, client, updatetime=0.1):
        super().__init__()
        self._stop_event = threading.Event()
        self.statussignal = statussignal
        self.client = client

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            self.statussignal.put(self.client.get_state())


class PeakAnalyzer(Device):
    #general parameters:
    scan_mode = Cpt(Signal,name="energy_mode",kind="config")
    pass_energy = Cpt(Signal,name="pass_energy",kind="config",value=50)
    measurement_state = Cpt(Signal,name="measurement_state",kind="config",value="Ready")
    lens_mode = Cpt(Signal,name="lens_mode",kind="config")
    acq_mode = Cpt(Signal,name="acquisition_mode",kind="config")
    dwell_time = Cpt(Signal,name="dwell_time",kind="config")
    region_name = Cpt(Signal,name="region_name",kind="config",value="Region")
    description = Cpt(Signal,name="description",kind="config",value="Description")

    #energy region:
    energy_center = Cpt(Signal,name="energy_center",kind="config",value=2000)
    #for swept mode:
    energy_width = Cpt(Signal,name="energy_width",kind="config",value=15)
    energy_step = Cpt(Signal,name="energy_step",kind="config")

    #for fixed mode:
    exposure_time = Cpt(Signal,name="exposure_time", kind="config")    

    #returned data:
    total_counts = Cpt(Signal,name="total_counts",kind="hinted")
    xaxis = Cpt(Signal,name="x_axis")        
    edc = Cpt(Signal,name="spetrum_data")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self._peakclient = peak.PeakClient("http://xf07id-ws11.nsls2.bnl.local:8087")
        self._peakclient.connect()
        self._acqclient = peak.AcquireSpectrumClient(self._peakclient)
        self._acqclient.connect()
        self._getparameters()
        self._multisweep = False
        
    def _activate_analyzer(self):
        if self._acqclient.get_state() == "Ready":
            self._peakclient.activate_servers()
            sleep(10)
        else:
            #NOTE: figure out states and how to deal
            print("Analyzer Already Active")

    def _deactivate_analyzer(self):
        self._peakclient.deactivate_servers()

    def _getparameters(self):
        specdef = self._acqclient.spectrum_definition
        self.pass_energy.put(specdef.pass_energy)
        self.acq_mode.put(specdef.acquisition_mode.value)
        self.lens_mode.put(specdef.lens_mode_name)
        self.exposure_time.put(specdef.acquisition_time)
        self.dwell_time.put(specdef.dwell_time)
        self.region_name.put(specdef.name)
     #   self.description.put(specdef.description)
        if PeakAxis.X in specdef.fixed_axes:
            self.scan_mode.put("fixed")
        if PeakAxis.X in specdef.sweep_axes:
            self.scan_mode.put("swept")
        self.energy_center.put(self._acqclient.current_x_axis.center)
        self.energy_width.put(self._acqclient.current_x_axis.width)
        self.energy_step.put(self._acqclient.current_x_axis.delta)

    def setfixedmode(self):
        self._acqclient.set_x_axis_mode(PeakAxisMode("Fixed"))
        self._getparameters()

    def setsweptmode(self):
        self._acqclient.set_x_axis_mode(PeakAxisMode("Sweep"))
        self._getparameters()

    def _setanalyzer(self):
        self._acqclient.start_measurement()
        self._acqclient.set_pass_energy(self.pass_energy.get())
        self._acqclient.set_lens_mode(self.lens_mode.get())
        self._acqclient.set_acquisition_mode(PeakAcquisitionMode(self.acq_mode.get()))
        self._acqclient.set_dwell_time(self.dwell_time.get())
        self._acqclient.set_name(self.region_name.get())
        self._acqclient.set_description(self.description.get())
        if self.scan_mode.get() == "swept":
            print("setting energy step size to "+str(self.energy_step.get())+" eV.")
            self._acqclient.set_x_axis_delta(self.energy_step.get())
            print("setting energy center to "+str(self.energy_center.get())+" eV.")
            self._acqclient.set_x_axis_center(self.energy_center.get())
            print("setting energy width to "+str(self.energy_width.get())+" eV.")
            self._acqclient.set_x_axis_width(self.energy_width.get())
        elif self.scan_mode.get() == "fixed":
            print("setting up for fixed energy mode.")
            self._acqclient.set_x_axis_center(self.energy_center.get())
            self._acqclient.set_acquisition_time(self.exposure_time.get())
        self._acqclient.setup_spectrum()
        self._getparameters()

    def set_exposure(self,exposure_time):
        self.exposure_time.set(exposure_time)

    def stage(self):
        self._activate_analyzer()
        self._setanalyzer()

    def trigger(self):
        _updater = _updatemonitor(self.measurement_state,self._acqclient)
        _updater.start()
        def check_value(*, old_value, value, **kwargs):
            return (old_value == "Acquiring" and value == "Measuring")

        status = SubscriptionStatus(self.measurement_state,check_value)
        self._acqclient.acquire_spectrum()
        specdat = self._acqclient.get_spectrum()
        self.total_counts.put(specdat.data.sum())
        self.xaxis.put(np.arange(specdat.x_axis.minimum,specdat.x_axis.maximum,specdat.x_axis.delta))
        self.edc.put(specdat.data.sum(axis=0))
#        self.imagedata.put(specdat.data)
        _updater.stop()
        if not self._multisweep:
            self._acqclient.clear_spectrum()
        return status
        
    def unstage(self):
        self._acqclient.finish_measurement()
        self._deactivate_analyzer()

peak_analyzer = PeakAnalyzer(name="PeakAnalyzer")
