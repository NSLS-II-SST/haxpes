import serial

class RBD():

    def __init__(self,
        port="/dev/ttyUSB0",
        filterpoints = 0,
        deviceID = "RBD9103"
        ):
        
        self.port = port
        self.com = serial.Serial(
            self.port,
            baudrate=57600,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=False,
            timeout=1
            )
        self.set_singleread()
        self.set_filter(filterpoints)
        self._set_deviceID(deviceID)
        self._get_config()
            
            
    def _sendcommand(self,message_string):
        """ formats command "message string" and sends to device """
        c = bytes('&'+message_string+'\n','utf-8')
        self.com.write(c)
        
    def _readstring(self):
        """ reads back string from buffer and formats """
        return self.com.readline().decode('utf-8').rstrip()
       
    def _closeport(self):
        """ closes serial port ... """
        self.com.close()

    def _open_device(self):
        """ open port ..."""
        self.com.open()
            
    def _reset_device(self):
        """ resets device to default settings """
        self._sendcommand("D")       
      
    def _set_deviceID(self,devID):
        """ sets device ID.  ID must be 10 characters. """
        if len(devID) > 10:
            devID = devID[:10]
        self.deviceID = devID.ljust(10)
        c = "P"+self.deviceID
        self._sendcommand(c)
        self._readstring()
        
    def _get_config(self):
        """ reads configuration.  Puts device in single-read mode. """
    
        if self.autoread:
            self.set_singleread # temporarily disable auto-read but do not set flag or sample_interval
            
        self._read_all()
        self._sendcommand("Q")
        self._readstring() # Instrument name ... ignore
        self.firmware = self._readstring() # firmware ... how to parse
        self._readstring() # build ... ignore
        self.devrange_str = self._readstring() # range ... thing about how to handle this -- range to index
        self.sample_interval = int(self._readstring()[-9:-5])
        self._readstring() # chart log ... N/A
        self._readstring() # Bias ... N/A
        self.filter = int(self._readstring()[-3:]) # filter ... number of points
        self._readstring() # format length ... ignore for now
        self._readstring() # cal ... ignore for now
        self._readstring() # grounding ... ignore for now ... don't ground 
        self._readstring() # dev state ... ignore for now 
        self.deviceID = self._readstring()[7:] # device name

    def _read_all(self,output=False):
        """ reads all messages currently in buffer.          
        Does not output unless "output" is set to True
        By default, output is False.
        CAUTION: if command is given while device is in auto-read, will hang.
        """
        msg = self.com.readlines()
        if output:
            return msg
        else:
            return

    def set_singleread(self):
        """ sets RBD to single-read mode"""
#        self.sample_interval=0
        self.autoread = False
        self._sendcommand("I0000")
        self._read_all()
           
    def set_autoread(self,interval=50):
        """ sets RBD to autoread.  Readback interval can be given in ms.  Default value is 50 ms """
        self.sample_interval=interval
        c = "I"+f"{interval:04d}"
        self._sendcommand(c)
        self._readstring()
        self.autoread = True

    def read_current(self):
        """ performs single current read and parses output.  Returns a list with elements:
        0: current in A
        1: readstatus; "=" is in range, "<" is under-range, ">" is over-range, "*" is unstable
        2: readback of ammeter range.
        """
        self._sendcommand("S")
        msg = self._readstring()
        l = msg.split(",")
        readstatus = l[0][-1]
        unit = l[-1]
        current = l[-2]
        rangeRBV = l[1][6:]
        if unit == "nA":
            current = float(current)*10**-9
        if unit == "uA":
            current = float(current)*10**-6
        if unit == "mA":
            current = float(current)*10**-3
        return [current, readstatus, rangeRBV]
        
    def set_filter(self,filterpoints):
    
        if self.autoread:
            self._sendcommand("I0000") # turn off auto-read temporarily but do not reset sample_interval or autoread flag
            
        self.filter = filterpoints
        c = "F"+f"{filterpoints:03d}"
        self._sendcommand(c)
        self._readstring()
        
        if self.autoread:
            self.set_autoread(interval=self.sample_interval)
        
    def set_range(self,rangeindex):
        """ sets measurement range.  Available ranges are:
        1: 2 nA
        2: 20 nA
        3: 200 nA
        4: 2 uA
        5: 20 uA
        6: 200 uA
        7: 2 mA
        0: AutoRange.  
        NOTE:  Do not use AutoRange for high voltage operations!
        """
        
        if self.autoread:
            self._sendcommand("I0000") # turn off auto-read temporarily, do not reset sample_interval or autoread flag  

        c = "R"+str(rangeindex)
        self._sendcommand(c)
        self._readstring()
        
        if self.autoread:  
            self.set_autoread(self.sample_interval)  # turn auto-read back on
        
        
