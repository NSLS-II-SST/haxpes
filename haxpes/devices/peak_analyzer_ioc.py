"""
The PEAK analyzer, through the peak-ioc caproto IOC.

A drop-in for ``haxpes.devices.peak_analyzer.PeakAnalyzer``, which talks to
the PEAK server directly: the same component names, kinds and methods, so the
data and configuration keys (``PeakAnalyzer_edc``, ``PeakAnalyzer_pass_energy``,
...) and the HAXPES plans keep working. The analyzer itself is driven by the
IOC (https://github.com/xraygui/peak-ioc); the settings components are the
IOC's setpoint PVs, so, as before, they hold the requested values and reach
the analyzer at ``stage()``. ``stage()`` follows ``PeakAnalyzer.stage()`` step
by step: live mode on, live pass energy, lens mode and energy, a settling
wait, then the spectrum setup, with the IOC's own prepositioning turned off.
"""

from time import sleep

from ophyd import Component as Cpt
from ophyd import Device, EpicsSignal, EpicsSignalRO, Signal
from ophyd.status import SubscriptionStatus

default_dwell_time = 0.1
default_lens_mode = "Angular"
default_acq_mode = "Image"


class PeakAnalyzerIOC(Device):
    # general parameters:
    scan_mode = Cpt(EpicsSignal, "ScanMode", string=True, kind="config")
    pass_energy = Cpt(EpicsSignal, "PassEnergy", kind="config")
    measurement_state = Cpt(EpicsSignalRO, "State_RBV", string=True,
                            kind="config")
    lens_mode = Cpt(EpicsSignal, "LensMode", string=True, kind="config")
    acq_mode = Cpt(EpicsSignal, "AcqMode", string=True, kind="config")
    dwell_time = Cpt(EpicsSignal, "DwellTime", kind="config")
    region_name = Cpt(EpicsSignal, "RegionName", string=True, kind="config")
    description = Cpt(EpicsSignal, "Description", string=True, kind="config")
    # Never used by the HAXPES device; kept for its configuration key.
    offset = Cpt(Signal, value=0, kind="config")

    # energy region:
    energy_center = Cpt(EpicsSignal, "EnergyCenter", kind="config")
    # for swept mode:
    energy_width = Cpt(EpicsSignal, "EnergyWidth", kind="config")
    energy_step = Cpt(EpicsSignal, "EnergyStep", kind="config")

    # for fixed mode:
    exposure_time = Cpt(EpicsSignal, "ExposureTime", kind="config")

    # y axis for image mode ...:
    yaxis = Cpt(EpicsSignalRO, "YAxis")

    # returned data:
    total_counts = Cpt(EpicsSignalRO, "TotalCounts", kind="hinted")
    xaxis = Cpt(EpicsSignalRO, "XAxis")
    edc = Cpt(EpicsSignalRO, "EDC")
    y_CoM = Cpt(EpicsSignalRO, "YCoM")

    # optimization function for alignment:
    opt_val = Cpt(EpicsSignalRO, "OptVal")
    opt_par = Cpt(EpicsSignal, "OptPar")

    # New with the IOC; omitted from documents unless their kind is changed.
    image = Cpt(EpicsSignalRO, "Image", kind="omitted")
    size_x = Cpt(EpicsSignalRO, "SizeX_RBV", kind="omitted")
    size_y = Cpt(EpicsSignalRO, "SizeY_RBV", kind="omitted")
    y_profile = Cpt(EpicsSignalRO, "YProfile", kind="omitted")
    array_counter = Cpt(EpicsSignalRO, "ArrayCounter_RBV", kind="omitted")
    status_message = Cpt(EpicsSignalRO, "StatusMessage_RBV", string=True,
                         kind="omitted")
    acquire = Cpt(EpicsSignal, "Acquire", put_complete=True, kind="omitted")
    measure = Cpt(EpicsSignal, "Measure", string=True, put_complete=True,
                  kind="omitted")
    active = Cpt(EpicsSignal, "Active", string=True, put_complete=True,
                 kind="omitted")
    accumulate = Cpt(EpicsSignal, "Accumulate", string=True, kind="omitted")
    preposition = Cpt(EpicsSignal, "Preposition", string=True, kind="omitted")
    read_settings = Cpt(EpicsSignal, "ReadSettings", put_complete=True,
                        kind="omitted")
    live_energy = Cpt(EpicsSignal, "LiveEnergy", put_complete=True,
                      kind="omitted")
    live_pass_energy = Cpt(EpicsSignal, "LivePassEnergy", put_complete=True,
                           kind="omitted")
    live_lens_mode = Cpt(EpicsSignal, "LiveLensMode", string=True,
                         put_complete=True, kind="omitted")
    live_dwell_time = Cpt(EpicsSignal, "LiveDwellTime", put_complete=True,
                          kind="omitted")

    def __init__(self, prefix="", *, name="PeakAnalyzer", timeout=600,
                 preposition_wait=8, **kwargs):
        """
        ``timeout`` bounds staging and each acquisition, in seconds.
        ``preposition_wait`` is the settling time in ``stage()``, as the
        ``sleep(8)`` in ``PeakAnalyzer.stage()``.
        """
        super().__init__(prefix, name=name, **kwargs)
        self.timeout = timeout
        self.preposition_wait = preposition_wait

    def _getparameters(self):
        """Copy the analyzer's current settings to the settings components."""
        self.read_settings.set(1).wait(self.timeout)

    def setfixedmode(self):
        self.scan_mode.put("fixed")

    def setsweptmode(self):
        self.scan_mode.put("swept")

    def set_exposure(self, exposure_time):
        self.exposure_time.put(exposure_time)

    def stage(self):
        staged = super().stage()
        self.start_live_mode()
        ELo = self.energy_center.get() - (self.energy_width.get() / 2)
        self.set_live_pass_energy(self.pass_energy.get())
        self.set_live_lens_mode(self.lens_mode.get())
        self.set_live_energy_center(ELo)
        sleep(self.preposition_wait)
        # Only sets up the spectrum: the steps above did the IOC's preposition.
        self.preposition.set("Off").wait(self.timeout)
        self.measure.set("Start").wait(self.timeout)
        return staged

    def trigger(self):
        start = self.array_counter.get()

        def counted(value, **kwargs):
            return value > start

        # The put completes when the IOC has written the data; waiting for
        # the counter too makes sure our monitors have the new values.
        written = self.acquire.set(1, timeout=self.timeout)
        counter = SubscriptionStatus(self.array_counter, counted,
                                     timeout=self.timeout)
        return written & counter

    def unstage(self):
        self.measure.set("Stop").wait(self.timeout)
        return super().unstage()

    def setup_from_dictionary(self, region_dictionary, analyzer_settings,
                              scan_type="XPS", **kwargs):
        """performs analyzer setup from dictionary settings"""

        if scan_type == "XPS":
            self.setsweptmode()
            self.energy_center.put(region_dictionary["energy_center"])
            self.energy_step.put(region_dictionary["energy_step"])
            self.energy_width.put(region_dictionary["energy_width"])

        elif scan_type == "XAS":
            self.setfixedmode()
            self.energy_center.put(region_dictionary["energy_center"])

        else:
            raise ValueError(f"Unknown scan_type {scan_type!r}; use XPS or XAS")

        self.region_name.put(region_dictionary["region_name"])
        if "description" in region_dictionary.keys():
            self.description.put(region_dictionary["description"])

        self.pass_energy.put(analyzer_settings["pass_energy"])
        self.dwell_time.put(analyzer_settings.get("dwell_time",
                                                  default_dwell_time))
        self.lens_mode.put(analyzer_settings.get("lens_mode", default_lens_mode))
        self.acq_mode.put(analyzer_settings.get("acquisition_mode",
                                                default_acq_mode))

    def start_live_mode(self):
        self.active.set("On").wait(self.timeout)

    def stop_live_mode(self):
        self.active.set("Off").wait(self.timeout)

    @property
    def _livemode(self):
        return self.active.get() == "On"

    # As before, the live setters do nothing unless live mode is on. The IOC
    # also copies pass energy, lens mode and dwell time to the settings.
    def set_live_pass_energy(self, pass_energy):
        if self._livemode:
            self.live_pass_energy.set(pass_energy).wait(self.timeout)

    def set_live_dwell_time(self, dwell_time):
        if self._livemode:
            self.live_dwell_time.set(dwell_time).wait(self.timeout)

    def set_live_lens_mode(self, lens_mode):
        if self._livemode:
            self.live_lens_mode.set(lens_mode).wait(self.timeout)

    def set_live_energy_center(self, kinetic_energy):
        if self._livemode:
            self.live_energy.set(kinetic_energy).wait(self.timeout)
