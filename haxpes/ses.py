from ophyd import EpicsSignal,PVPositioner, EpicsSignalRO, EpicsMotor
from ophyd import Device, Component
from ophyd import DeviceStatus

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

    
ses = SES('XF:07ID-ES-SES', name='ses')
