from tenma.devices.tenma_72_base import Tenma72Base
from tenma.exceptions.base_exception import TenmaException


class Tenma72_2540(Tenma72Base):
    MATCH_STR = ["72-2540"]
    #:
    NCHANNELS = 1
    #: Only 4 physical buttons. But 5 memories are available
    NCONFS = 5
    #:
    MAX_MA = 5100
    #:
    MAX_MV = 31000


class Tenma72_2535(Tenma72Base):
    #:
    MATCH_STR = ["72-2535"]
    #:
    NCHANNELS = 1
    #:
    NCONFS = 5
    #:
    MAX_MA = 3000
    #:
    MAX_MV = 30000


class Tenma72_2545(Tenma72Base):
    #:
    MATCH_STR = ["72-2545"]
    #:
    NCHANNELS = 1
    #:
    NCONFS = 5
    #:
    MAX_MA = 2000
    #:
    MAX_MV = 60000


class Tenma72_2550(Tenma72Base):
    #: Tenma 72-2550 is also manufactured as Korad KA 6003P
    MATCH_STR = ["72-2550", "KORADKA6003P"]
    #:
    NCHANNELS = 1
    #:
    NCONFS = 5
    #:
    MAX_MA = 3000
    #:
    MAX_MV = 60000


class Tenma72_2930(Tenma72Base):
    #:
    MATCH_STR = ["72-2930"]
    #:
    NCHANNELS = 1
    #:
    NCONFS = 5
    #:
    MAX_MA = 10000
    #:
    MAX_MV = 30000


class Tenma72_2705(Tenma72Base):
    #:
    MATCH_STR = ["72-2705"]
    #:
    NCHANNELS = 1
    #:
    NCONFS = 5
    #:
    MAX_MA = 3100
    #:
    MAX_MV = 31000


class Tenma72_2940(Tenma72Base):
    #:
    MATCH_STR = ["72-2940"]
    #:
    NCHANNELS = 1
    #:
    NCONFS = 5
    #:
    MAX_MA = 5000
    #:
    MAX_MV = 60000


class Tenma72_13320(Tenma72Base):
    #:
    MATCH_STR = ["72-13320"]
    #:
    NCHANNELS = 3
    #: This unit does actually support 10 slots (0-9) but it's not avialable from the front panel
    NCONFS = 0
    #:
    MAX_MA = 3000
    #:
    MAX_MV = 30000

    def __init__(self, serialPort, debug=False):
        serial_eol = "\n"
        self.serialHandler = TenmaSerialHandler(serialPort, serial_eol, debug=debug)
        self.debug = debug

    def getStatus(self):
        """
            Returns the power supply status as a dictionary of values

            * ch1Mode: "C.V | C.C"
            * ch2Mode: "C.V | C.C"
            * tracking:
                * 00=Independent
                * 01=Tracking series
                * 10=Tracking parallel
            * out1Enabled: True | False
            * out2Enabled: True | False

            :return: Dictionary of status values
        """
        self._sendCommand("STATUS?")
        statusBytes = self._readBytes()

        # 72-13330 sends two bytes back, the second being '\n'
        status = statusBytes[0]

        ch1mode = (status & 0x01)
        ch2mode = (status & 0x02)
        tracking = (status & 0x0C) >> 2
        out1 = (status & 0x40)
        out2 = (status & 0x80)

        if tracking == 0:
            tracking = "Independent"
        elif tracking == 1:
            tracking = "Tracking Series"
        elif tracking == 2:
            tracking = "Tracking Parallel"
        else:
            tracking = "Unknown"

        return {
            "ch1Mode": "C.V" if ch1mode else "C.C",
            "ch2Mode": "C.V" if ch2mode else "C.C",
            "Tracking": tracking,
            "out1Enabled": bool(out1),
            "out2Enabled": bool(out2)
        }

    def readCurrent(self, channel):
        """
            Reads the current setting for the given channel

            :param channel: Channel to read the current of
            :type channel: iint
            :return: Current for the channel in Amps as a float
            :raises TenmaException: If trying to read the current of Channel 3
        """
        if channel == 3:
            raise TenmaException("Channel CH3 does not support reading current")
        return super().readCurrent(channel)

    def runningCurrent(self, channel):
        """
            Returns the current read of a running channel

            :param channel: Channel to get the running current for
            :type channel: iint
            :return: The running current of the channel in Amps as a float

            :raises TenmaException: If trying to read the current of Channel 3
        """
        if channel == 3:
            raise TenmaException("Channel CH3 does not support reading current")
        return super().runningCurrent(channel)

    def setVoltage(self, channel, mV):
        """
            Sets the voltage of the specified channel

            :param channel: Channel to set the voltage of
            :type channel: int
            :param mV: voltage to set the channel to, in mV
            :type mV: int
            :return: The voltage the channel was set to in Volts as a float

            :raises TenmaException: If the voltage does not match what was set,
            or if trying to set an invalid voltage on Channel 3
        """
        if channel == 3 and mV not in [2500, 3300, 5000]:
            raise TenmaException("Channel CH3 can only be set to 2500mV, 3300mV or 5000mV")
        return super().setVoltage(channel, mV)

    def setOCP(self, enable=True):
        """
            Enable or disable OCP.

            There's no feedback from the serial connection to determine
            whether OCP was set or not.

            :param enable: Boolean to enable or disable
            :type enable: boolean
            :raises NotImplementedError: This model doesn't support OCP
        """
        raise NotImplementedError("This model does not support OCP")

    def setOVP(self, enable=True):
        """
            Enable or disable OVP

            There's no feedback from the serial connection to determine
            whether OVP was set or not.

            :param enable: Boolean to enable or disable
            :type enable: boolean
            :raises NotImplementedError: This model doesn't support OVP
        """
        raise NotImplementedError("This model does not support OVP")

    def ON(self, channel=None):
        """
            Turns on the output(s)

            :param channel: Channel to turn on, defaults to None (turn all channels on)
            :type channel: int
        """
        if channel is None:
            command = "OUT12:1"
        else:
            self.checkChannel(channel)
            command = "OUT{}:1".format(channel)

        self._sendCommand(command)

    def OFF(self, channel=None):
        """
            Turns off the output(s)

            :param channel: Channel to turn on, defaults to None (turn all channels off)
            :type channel: int
        """
        if channel is None:
            command = "OUT12:0"
        else:
            self.checkChannel(channel)
            command = "OUT{}:0".format(channel)
        self._sendCommand(command)

    def setLock(self, enable=True):
        """
            Set the front-panel lock on or off

            :param enable: Enable lock, defaults to True
            :type enable: boolean
        """
        enableFlag = 1 if enable else 0
        self._sendCommand("LOCK{}".format(enableFlag))

    def setTracking(self, trackingMode):
        """
            Sets the tracking mode of the power supply outputs
            0: Independent
            1: Series
            2: Parallel

            :param trackingMode: one of 0, 1 or 2
            :type trackingMode: int
            :raises TenmaException: If a tracking mode other than 0, 1 or 2 is specified
        """
        if trackingMode not in [0, 1, 2]:
            raise TenmaException(
                ("Tracking mode {} not valid. Use one of:"
                 " 0 (Independent), 1 (Series), 2 (Parallel)").format(trackingMode))
        self._sendCommand("TRACK{}".format(trackingMode))

    def startAutoVoltageStep(self, channel, startMillivolts,
                             stopMillivolts, stepMillivolts, stepTime):
        """
            Starts an automatic voltage step from Start mV to Stop mV,
            incrementing by Step mV every Time seconds

            :param channel: Channel to start voltage step on
            :type channel: int
            :param startMillivolts: Starting voltage in mV
            :type startMillivolts: int
            :param stopMillivolts: End voltage in mV
            :type stopMillivolts: int
            :param stepMillivolts: Amount to increase voltage by in mV
            :type stepMillivolts: int
            :param stepTime: Time to wait before each increase, in Seconds
            :type stepTime: float
            :raises TenmaException: If the channel or voltage is invalid
        """
        self.checkChannel(channel)
        self.checkVoltage(channel, stopMillivolts)
        # TODO: improve this check for when we're stepping down in voltage
        if stepMillivolts > stopMillivolts:
            raise TenmaException(
                ("Channel CH{channel} step voltage {stepMillivolts}V"
                 " higher than stop voltage {stopMillivolts}V").format(
                    channel=channel,
                    stepMillivolts=stepMillivolts,
                    stopMillivolts=stopMillivolts))

        startVolts = float(startMillivolts) / 1000.0
        stopVolts = float(stopMillivolts) / 1000.0
        stepVolts = float(stepMillivolts) / 1000.0

        command = "VASTEP{channel}:{startVolts},{stopVolts},{stepVolts},{stepTime}".format(
            channel=channel,
            startVolts=startVolts,
            stopVolts=stopVolts,
            stepVolts=stepVolts,
            stepTime=stepTime
        )
        self._sendCommand(command)

    def stopAutoVoltageStep(self, channel):
        """
            Stops the auto voltage step on the specified channel

            :param channel: Channel to stop the auto voltage step on
            :type channel: int
        """
        self.checkChannel(channel)
        self._sendCommand("VASTOP{}".format(channel))

    def startAutoCurrentStep(self, channel, startMilliamps,
                             stopMilliamps, stepMilliamps, stepTime):
        """
            Starts an automatic current step from Start mA to Stop mA,
            incrementing by Step mA every Time seconds

            :param channel: Channel to start current step on
            :type channel: int
            :param startMilliamps: Starting current in mA
            :type startMilliamps: int
            :param stopMilliamps: End current in mA
            :type stopMilliamps: int
            :param stepMilliamps: Amount to increase current by in mA
            :type stepMilliamps: int
            :param stepTime: Time to wait before each increase, in Seconds
            :type stepTime: float
            :raises TenmaException: If the channel or current is invalid
        """
        self.checkChannel(channel)
        self.checkCurrent(channel, stopMilliamps)
        if stepMilliamps > stopMilliamps:
            raise TenmaException(
                ("Channel CH{channel} step current {stepMilliamps}mA higher"
                 " than stop current {stopMilliamps}mA").format(
                    channel=channel,
                    stepMilliamps=stepMilliamps,
                    stopMilliamps=stopMilliamps))

        startAmps = float(startMilliamps) / 1000.0
        stopAmps = float(stopMilliamps) / 1000.0
        stepAmps = float(stepMilliamps) / 1000.0

        command = "IASTEP{channel}:{startAmps},{stopAmps},{stepAmps},{stepTime}".format(
            channel=channel,
            startAmps=startAmps,
            stopAmps=stopAmps,
            stepAmps=stepAmps,
            stepTime=stepTime
        )
        self._sendCommand(command)

    def stopAutoCurrentStep(self, channel):
        """
            Stops the auto current step on the specified channel

            :param channel: Channel to stop the auto current step on
            :type channel: int
        """
        self.checkChannel(channel)
        self._sendCommand("IASTOP{}".format(channel))

    def setManualVoltageStep(self, channel, stepMillivolts):
        """
            Sets the manual step voltage of the channel
            When a VUP or VDOWN command is sent to the power supply channel, that channel
            will step up or down by stepMillivolts mV

            :param channel: Channel to set the step voltage for
            :type channel: int
            :param stepMillivolts: Voltage to step up or down by when triggered
            :type stepMillivolts: int
        """
        self.checkChannel(channel)
        self.checkVoltage(channel, stepMillivolts)
        stepVolts = float(stepMillivolts) / 1000.0
        command = "VSTEP{}:{}".format(channel, stepVolts)
        self._sendCommand(command)

    def stepVoltageUp(self, channel):
        """
            Increse the voltage by the configured step voltage on the specified channel
            Call "setManualVoltageStep" to set the step voltage

            :param channel: Channel to increase the voltage for
            :type channel: int
        """
        self.checkChannel(channel)
        self._sendCommand("VUP{}".format(channel))

    def stepVoltageDown(self, channel):
        """
            Decrese the voltage by the configured step voltage on the specified channel
            Call "setManualVoltageStep" to set the step voltage

            :param channel: Channel to decrease the voltage for
            :type channel: int
        """
        self.checkChannel(channel)
        self._sendCommand("VDOWN{}".format(channel))

    def setManualCurrentStep(self, channel, stepMilliamps):
        """
            Sets the manual step current of the channel
            When a IUP or IDOWN command is sent to the power supply channel, that channel
            will step up or down by stepMilliamps mA

            :param channel: Channel to set the step current for
            :type channel: int
            :param stepMilliamps: Current to step up or down by when triggered
            :type stepMilliamps: int
        """
        self.checkChannel(channel)
        self.checkCurrent(channel, stepMilliamps)
        stepAmps = float(stepMilliamps) / 1000.0
        command = "ISTEP{}:{}".format(channel, stepAmps)
        self._sendCommand(command)

    def stepCurrentUp(self, channel):
        """
            Increse the current by the configured step current on the specified channel
            Call "setManualCurrentStep" to set the step current

            :param channel: Channel to increase the current for
            :type channel: int
        """
        self.checkChannel(channel)
        self._sendCommand("IUP{}".format(channel))

    def stepCurrentDown(self, channel):
        """
            Decrese the current by the configured step current on the specified channel
            Call "setManualCurrentStep" to set the step current

            :param channel: Channel to decrease the current for
            :type channel: int
        """
        self.checkChannel(channel)
        self._sendCommand("IDOWN{}".format(channel))


class Tenma72_13330(Tenma72_13320):
    #:
    MATCH_STR = ["72-13330"]
    #:
    NCHANNELS = 3
    #: This unit does actually support 10 slots (0-9) but it's not avialable from the front panel
    NCONFS = 0
    #:
    MAX_MA = 5000
    #:
    MAX_MV = 30000


class Tenma72_13360_base(object):
    """
        Tenma 72-13360 single channel programmable PSU
        This PSU uses the RS485 protocol and only supports a single channel.
        That means that the channel is never specified in the message to the PSU.
        Because of this, the channel parameter removed from all methods.

        It also has other slight variations in protocol such as a ":" separator and the
        STATUS? command returning more general settings.
    """

    NCONFS = 5
    MAX_MA = 15000
    MAX_MV = 60000
    SERIAL_SETTER_SEPARATOR = ":"

    def __init__(self, serialPort, debug=False):
        serial_eol = "\n"
        self.serialHandler = TenmaSerialHandler(serialPort, serial_eol, debug=debug)

        self.debug = debug

    def _sendCommand(self, command):
        """
            Sends a command to the serial port of a power supply

            :param command: Command to send
        """
        self.serialHandler._sendCommand(command)

    def _readBytes(self):
        """
            Read serial output as a stream of bytes

            :return: Bytes read as a list of integers
        """
        return self.serialHandler._readBytes()

    def __readOutput(self):
        """
            Read serial otput as a string

            :return: Data read as a string
        """
        return self.serialHandler._readOutput()

    def close(self):
        """
            Closes the serial port
        """
        self.serialHandler.close()

    def checkVoltage(self, mV):
        """
            Checks that the given voltage is valid for the power supply

            :param mV: Voltage to check
            :raises TenmaException: If the voltage is outside the range for the power supply
        """
        mV = int(mV)
        if mV > self.MAX_MV or mV < 0:
            raise TenmaException(
                "Trying to set voltage to {mv}mV, the maximum is {max}mV".format(
                    mv=mV,
                    max=self.MAX_MV))

    def checkCurrent(self, mA):
        """
            Checks that the given current is valid for the power supply

            :param mA: current to check
            :raises TenmaException: If the current is outside the range for the power supply
        """
        mA = int(mA)
        if mA > self.MAX_MA or mA < 0:
            raise TenmaException(
                "Trying to set current to {ma}mA, the maximum is {max}mA".format(
                    ma=mA,
                    max=self.MAX_MA))

    def getVersion(self, serialEol=""):
        """
            Returns a single string with the version of the Tenma Device and Protocol user

            :param serialEol: End of line terminator, defaults to ""
            :return: The version string from the power supply
        """
        self._sendCommand("*IDN?{}".format(serialEol))
        return self.__readOutput()

    def getStatus(self):
        """
            Returns the power supply status as a dictionary of values

            "channelMode ": "C.V" or "C.C",
            "output ": "ON" or "OFF",
            "V/C priority ": "Current priority" or "Voltage priority",
            "beep ": "ON" or "OFF",
            "lock ": "ON" or "OFF",

            :return: Dictionary of status values
        """
        self._sendCommand("STATUS?")
        statusBytes = self._readBytes()

        # 72-13360 sends two bytes back, the second being '\n'
        status = statusBytes[0]

        ch1mode = (status & 0b00000001)
        output = (status & 0b00000010)
        current_priority = (status & 0b00000100)
        beep = (status & 0b00010000)
        lock = (status & 0b00100000)

        return {
            "channelMode ": "C.V" if ch1mode else "C.C",
            "output ": "ON" if output else "OFF",
            "V/C priority ": "Current priority" if current_priority else "Voltage priority",
            "beep ": "ON" if beep else "OFF",
            "lock ": "ON" if lock else "OFF",
        }

    def readCurrent(self):
        """
            Reads the current setting

            :return: Current in Amps as a float
        """
        commandCheck = "ISET?".format()
        self._sendCommand(commandCheck)
        return float(self.__readOutput()[:5])

    def setCurrent(self, mA):
        """
            Sets the current

            :param mA: Current to set the PSU to, in mA
            :raises TenmaException: If the current does not match what was set
            :return: The current the PSU was set to in Amps as a float
        """
        self.checkCurrent(mA)

        A = float(mA) / 1000.0
        command = "ISET:{amperes:.3f}".format(amperes=A)

        self._sendCommand(command)
        readcurrent = self.readCurrent()
        readMilliamps = int(readcurrent * 1000)

        if readMilliamps != mA:
            raise TenmaException("Set {mA}mA, but read {readMilliamps}mA".format(
                mA=mA,
                readMilliamps=readMilliamps
            ))
        return float(readcurrent)

    def readVoltage(self):
        """
            Reads the voltage setting

            :return: Voltage in Volts as a float
        """
        commandCheck = "VSET?"
        self._sendCommand(commandCheck)
        return float(self.__readOutput())

    def setVoltage(self, mV):
        """
            Sets the voltage

            :param mV: voltage to set the PSU to, in mV
            :raises TenmaException: If the voltage does not match what was set
            :return: The voltage the PSU was set to in Volts as a float
        """
        self.checkVoltage(mV)

        volts = float(mV) / 1000.0
        command = "VSET:{volts:.2f}".format(volts=volts)

        self._sendCommand(command)
        readVolts = self.readVoltage()
        readMillivolts = int(readVolts * 1000)

        if readMillivolts != int(mV):
            raise TenmaException("Set {mV}mV, but read {readMillivolts}mV".format(
                mV=mV,
                readMillivolts=readMillivolts
            ))
        return float(readVolts)

    def runningCurrent(self):
        """
            Returns the current when the PSU is running

            :return: The running current of the PSU in Amps as a float
        """
        command = "IOUT?"
        self._sendCommand(command)
        return float(self.__readOutput())

    def runningVoltage(self):
        """
            Returns the voltage read when the PSU is running

            :return: The running voltage of the PSU in volts as a float
        """
        command = "VOUT?"
        self._sendCommand(command)
        return float(self.__readOutput())

    def saveConf(self, conf):
        """
            Save current configuration into Memory.

            :param conf: Memory index to store to
            :raises TenmaException: If the memory index is outside the range
        """
        conf = int(conf)
        if conf > self.NCONFS or conf < 1:
            raise TenmaException("Trying to set M{conf} with only {nconf} slots".format(
                conf=conf,
                nconf=self.NCONFS
            ))

        command = "SAV:{}".format(conf)
        self._sendCommand(command)

    def saveConfFlow(self, conf):
        """
            Alias for saveConf as saveConf works as expected on Tenma 13360
            unlike some other Tenma models
        """
        self.saveConf(conf)

    def recallConf(self, conf):
        """
            Load existing configuration in Memory. Same as pressing any Mx button on the unit
        """
        conf = int(conf)
        if conf > self.NCONFS or conf < 1:
            raise TenmaException("Trying to recall M{conf} with only {nconf} confs".format(
                conf=conf,
                nconf=self.NCONFS
            ))
        self._sendCommand("RCL:{}".format(conf))

    def setBEEP(self, enable=True):
        """
            Enable or disable BEEP

            There's no feedback from the serial connection to determine
            whether BEEP was set or not.

            :param enable: Boolean to enable or disable
        """
        enableFlag = 1 if enable else 0
        command = "BEEP:{}".format(enableFlag)
        self._sendCommand(command)

    def setLock(self, enable=True):
        """
            Set the front-panel lock on or off

            :param enable: Enable lock, defaults to True
        """
        enableFlag = 1 if enable else 0
        self._sendCommand("LOCK:{}".format(enableFlag))

    def ON(self):
        """
            Turns on the output
        """
        command = "OUT:1"
        self._sendCommand(command)

    def OFF(self):
        """
            Turns off the output
        """
        command = "OUT:0"
        self._sendCommand(command)

    def startAutoVoltageStep(self, startMillivolts,
                             stopMillivolts, stepMillivolts, stepTime):
        """
            Starts an automatic voltage step from Start mV to Stop mV,
            incrementing by Step mV every Time seconds

            :param startMillivolts: Starting voltage in mV
            :param stopMillivolts: End voltage in mV
            :param stepMillivolts: Amount to increase voltage by in mV
            :param stepTime: Time to wait before each increase, in Seconds
            :raises TenmaException: If the voltage is invalid
        """
        self.checkVoltage(stopMillivolts)
        if stepMillivolts > stopMillivolts:
            raise TenmaException(
                ("step voltage {stepMillivolts}V"
                 " higher than stop voltage {stopMillivolts}V").format(
                    stepMillivolts=stepMillivolts,
                    stopMillivolts=stopMillivolts))

        startVolts = float(startMillivolts) / 1000.0
        stopVolts = float(stopMillivolts) / 1000.0
        stepVolts = float(stepMillivolts) / 1000.0

        command = "VASTEP:{startVolts},{stopVolts},{stepVolts},{stepTime}".format(
            startVolts=startVolts,
            stopVolts=stopVolts,
            stepVolts=stepVolts,
            stepTime=stepTime
        )
        self._sendCommand(command)

    def stopAutoVoltageStep(self):
        """
            Stops the auto voltage step
        """
        self._sendCommand("VASTOP")

    def startAutoCurrentStep(self, startMilliamps,
                             stopMilliamps, stepMilliamps, stepTime):
        """
            Starts an automatic current step from Start mA to Stop mA,
            incrementing by Step mA every Time seconds

            :param startMilliamps: Starting current in mA
            :param stopMilliamps: End current in mA
            :param stepMilliamps: Amount to increase current by in mA
            :param stepTime: Time to wait before each increase, in Seconds
            :raises TenmaException: If the current is invalid
        """
        self.checkCurrent(stopMilliamps)
        if stepMilliamps > stopMilliamps:
            raise TenmaException(
                ("step current {stepMilliamps}mA higher"
                 " than stop current {stopMilliamps}mA").format(
                    stepMilliamps=stepMilliamps,
                    stopMilliamps=stopMilliamps))

        startAmps = float(startMilliamps) / 1000.0
        stopAmps = float(stopMilliamps) / 1000.0
        stepAmps = float(stepMilliamps) / 1000.0

        command = "IASTEP:{startAmps},{stopAmps},{stepAmps},{stepTime}".format(
            startAmps=startAmps,
            stopAmps=stopAmps,
            stepAmps=stepAmps,
            stepTime=stepTime
        )
        self._sendCommand(command)

    def stopAutoCurrentStep(self):
        """
            Stops the auto current step
        """
        self._sendCommand("IASTOP")

    def setManualVoltageStep(self, stepMillivolts):
        """
            Sets the manual step voltage
            When a VUP or VDOWN command is sent to the power supply, the PSU
            will step up or down by stepMillivolts mV

            :param stepMillivolts: Voltage to step up or down by when triggered
        """
        self.checkVoltage(stepMillivolts)
        stepVolts = float(stepMillivolts) / 1000.0
        command = "VSTEP:{}".format(stepVolts)
        self._sendCommand(command)

    def stepVoltageUp(self):
        """
            Increse the voltage by the configured step voltage
            Call "setManualVoltageStep" to set the step voltage
        """
        self._sendCommand("VUP")

    def stepVoltageDown(self):
        """
            Decrese the voltage by the configured step voltage
            Call "setManualVoltageStep" to set the step voltage
        """
        self._sendCommand("VDOWN")

    def setManualCurrentStep(self, stepMilliamps):
        """
            Sets the manual step current
            When a IUP or IDOWN command is sent to the power supply, the current
            will step up or down by stepMilliamps mA

            :param stepMilliamps: Current to step up or down by when triggered
        """
        self.checkCurrent(stepMilliamps)
        stepAmps = float(stepMilliamps) / 1000.0
        command = "ISTEP:{}".format(stepAmps)
        self._sendCommand(command)

    def stepCurrentUp(self):
        """
            Increse the current by the configured step current.
            Call "setManualCurrentStep" to set the step curchrent
        """
        self._sendCommand("IUP")

    def stepCurrentDown(self):
        """
            Decrese the current by the configured step current.
            Call "setManualCurrentStep" to set the step current
        """
        self._sendCommand("IDOWN")

    def setVoltagePriority(self):
        """
            Prioritize voltage
        """
        self._sendCommand("PRIORITY:0")

    def setCurrentPriority(self):
        """
            Prioritize current
        """
        self._sendCommand("PRIORITY:1")


class Tenma72_13360(Tenma72_13360_base):
    MATCH_STR = ["72-13360"]
