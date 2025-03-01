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

#    def set_analyzer(self, filename, core_line, en_cal):
#        """
#        sets SES paramaters in a controlled way
#        """
#        dstepsize = 50
#        dlensmode = "Angular"
#        dsteptime = 0.1
#        dacqmode = "swept"
#        yield from abs_set(self.filename, filename)
#        yield from abs_set(self.region_name, core_line["Region Name"])
#        if core_line["Energy Type"] == "Binding":
#            cent = en_cal - core_line["center_en"]
#            yield from abs_set(self.center_en_sp, cent)
#        else:
#            yield from abs_set(self.center_en_sp, core_line["center_en"])
#        yield from abs_set(self.width_en_sp, core_line["width"])
#        yield from abs_set(self.iterations, core_line["Iterations"])
#        yield from abs_set(self.pass_en, core_line["Pass Energy"])
#        yield from abs_set(self.excitation_en, en_cal)  
#        print(en_cal)
#        if "Step Size" in core_line.keys():
#            yield from abs_set(self.en_step, core_line["Step Size"])
#        else:
#            yield from abs_set(self.en_step, dstepsize)
#        if "Lens Mode" in core_line.keys():
#            yield from abs_set(self.lens_mode, core_line["Lens Mode"])
#        else:
#            yield from abs_set(self.lens_mode, dlensmode)
#        if "steptime" in core_line.keys():
#            yield from abs_set(self.steptime, core_line["steptime"])
#        else:
#            yield from abs_set(self.steptime, dsteptime)
#        if "acq_mode" in core_line.keys():
#            yield from abs_set(self.acq_mode, core_line["acq_mode"])
#        else:
#            yield from abs_set(self.acq_mode, dacqmode)

    def set_analyzer(self, filename, core_line, en_cal):
        """
        sets SES paramaters in a controlled way
        """
        dstepsize = 50
        dlensmode = "Angular"
        dsteptime = 0.1
        dacqmode = "swept"
        self.filename.put(filename)
        self.region_name.put(core_line["Region Name"])
        if core_line["Energy Type"] == "Binding":
            cent = en_cal - core_line["center_en"]
            self.center_en_sp.put(cent)
        else:
            self.center_en_sp.put(core_line["center_en"])
        self.width_en_sp.put(core_line["width"])
        self.iterations.put(core_line["Iterations"])
        self.pass_en.put(core_line["Pass Energy"])
        self.excitation_en.put(en_cal)
        if "Step Size" in core_line.keys():
            self.en_step.put(core_line["Step Size"])
        else:
            self.en_step.put(dstepsize)
        if "Lens Mode" in core_line.keys():
            self.lens_mode.put(core_line["Lens Mode"])
        else:
            self.lens_mode.put(dlensmode)
        if "steptime" in core_line.keys():
            self.steptime.put(core_line["steptime"])
        else:
            self.steptime.put(dsteptime)
        if "acq_mode" in core_line.keys():
            self.acq_mode.put(core_line["acq_mode"])
        else:
            self.acq_mode.put(dacqmode)


    def setup_from_dictionary(self,region_dictionary,analyzer_settings,mode,sweeps=1):
        """ temporary function to make SES work same as peak - just translates dictionary from peak format to SES format.  Call must include "XPS" mode. """
        print(region_dictionary)        
        if mode != "XPS":
            print("bad mode!  I'm not doing anything.")
            return
        core_line = {
            "Region Name": region_dictionary["region_name"],
            "Energy Type": region_dictionary["energy_type"].capitalize(),
            "center_en": region_dictionary["energy_center"],
            "width": region_dictionary["energy_width"],
            "Pass Energy": analyzer_settings["pass_energy"],
            #think about en_cal ... by default already switched into k.e.
            "Step Size": 1000*region_dictionary["energy_step"],
            "Lens Mode": analyzer_settings["lens_mode"],
            "steptime": analyzer_settings["dwell_time"],
            "Iterations": sweeps
        }
        print(core_line)
        self.set_analyzer('XPS_scan_',core_line,0)
    
    def reset(self):
        """
        resets the stop signal.  Probably not necessary
        """
        status = DeviceStatus(self)
        self.stop_signal.put(0)
        return status


# ses = SES('XF:07ID-ES-SES', name='ses')
