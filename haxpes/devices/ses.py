from ophyd import EpicsSignal,PVPositioner, EpicsSignalRO, EpicsMotor
from ophyd import Device, Component
from ophyd import DeviceStatus
from bluesky.plan_stubs import abs_set

class SES(Device):
    """
    Scienta SES control
    """

    center_en_sp = Component(EpicsSignal, ':center_en_SP', kind='config')
    width_en_sp = Component(EpicsSignal, ':width_en_SP', kind='config')
    set_start = Component(EpicsSignal, ':request', kind='config')
    done = Component(EpicsSignalRO, ':done', kind='config')
    iterations = Component(EpicsSignal, ':iterations_SP', kind='config')
    excitation_en = Component(EpicsSignal, ':excitation_en_SP', kind='config')
    steptime = Component(EpicsSignal, ':steptime_SP', kind='config')
    acq_mode = Component(EpicsSignal, ':acq_mode_SP', string=True, kind='config')
    pass_en = Component(EpicsSignal, ':pass_en_SP', kind='config')
    lens_mode  = Component(EpicsSignal, ':lens_mode_SP', string=True, kind='config')
    en_step = Component(EpicsSignal, ':en_step_SP', kind='config')
    write_mode = Component(EpicsSignal, ':write_mode', string=True, kind='config')
    filename = Component(EpicsSignal, ':filename_SP', string=True, kind='config')
    region_name = Component(EpicsSignal, ':region_name_SP', string=True, kind='config')
    stop_signal = Component(EpicsSignal, ':stop_request', kind='config')
   # write_directory = Component(EpicsSignal, ':savedir_SP')


    def trigger(self):
        """
        Trigger the detector and return a Status object.
        """
        status = DeviceStatus(self)
        # Wire up a callback that will mark the status object as finished
        # when we see the state flip from "acquiring" to "not acquiring"---
        # that is, a negative edge.
        def callback(old_value, value, **kwargs):
            if old_value == 0 and value == 1:
                status._finished()
                self.done.clear_sub(callback)

        self.done.subscribe(callback, run=False)
        self.set_start.put(1)        
        # And return the Status object, which the caller can use to
        # tell when the action is complete.
        return status

    def read_params(self):
        """
        Read the existing parameters in SES into PVs
        """
        status = DeviceStatus(self)
        # Wire up a callback that will mark the status object as finished
        # when we see the state flip from "acquiring" to "not acquiring"---
        # that is, a negative edge.
        def callback(old_value, value, **kwargs):
            if old_value == 0 and value == 1:
                status._finished()
                self.done.clear_sub(callback)

        self.done.subscribe(callback, run=False)
        self.set_start.put(2)
        # And return the Status object, which the caller can use to
        # tell when the action is complete.
        return status

    def stop(self):
        """
        Force stops the scan and reads back status ...
        """
        status = DeviceStatus(self)
        self.stop_signal.put(1)
        return status

    def set_analyzer(self, filename, core_line, en_cal):
        """
        sets SES paramaters in a controlled way
        """
        dstepsize = 50
        dlensmode = "Angular"
        dsteptime = 0.1
        dacqmode = "swept"

        yield from abs_set(self.filename, filename)
        yield from abs_set(self.region_name, core_line["Region Name"])
        if core_line["Energy Type"] == "Binding":
            cent = en_cal - core_line["center_en"]
            yield from abs_set(self.center_en_sp, cent)
        else:
            yield from abs_set(self.center_en_sp, core_line["center_en"])
        #    yield from abs_set(self.center_en_sp,core_line["center_en"]) ### BE correction.  Above 5 lines for testing, this one commented out.
        yield from abs_set(self.width_en_sp, core_line["width"])
        yield from abs_set(self.iterations, core_line["Iterations"])
        yield from abs_set(self.pass_en, core_line["Pass Energy"])
        yield from abs_set(self.excitation_en, en_cal)  # added 2023-08-02; NOT TESTED YET CW
        print(en_cal)
        #    if "Photon Energy" in core_line.keys():  #commented out 2023-08-02 CW
        #        yield from abs_set(ses.excitation_en,core_line["Photon Energy"])  #commented out 2023-08-02 CW
        if "Step Size" in core_line.keys():
            yield from abs_set(self.en_step, core_line["Step Size"])
        else:
            yield from abs_set(self.en_step, dstepsize)
        if "Lens Mode" in core_line.keys():
            yield from abs_set(self.lens_mode, core_line["Lens Mode"])
        else:
            yield from abs_set(self.lens_mode, dlensmode)
        if "steptime" in core_line.keys():
            yield from abs_set(self.steptime, core_line["steptime"])
        else:
            yield from abs_set(self.steptime, dsteptime)
        if "acq_mode" in core_line.keys():
            yield from abs_set(self.acq_mode, core_line["acq_mode"])
        else:
            yield from abs_set(self.acq_mode, dacqmode)

    def reset(self):
        """
        resets the stop signal.  Probably not necessary
        """
        status = DeviceStatus(self)
        self.stop_signal.put(0)
        return status


# ses = SES('XF:07ID-ES-SES', name='ses')
