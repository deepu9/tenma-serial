import time
import serial


class TenmaSerialHandler:
    """
    A small class that handles serial communication for tenma power supplies.
    """
    def __init__(
        self,
        serialPort: str,
        serialEOL: str,
        debug: bool = False,
        baud_rate: int = 9600,
        parity: str = serial.PARITY_NONE,
        stopbits: int | float = serial.STOPBITS_ONE
    ):
        """
            :param serialPort: COM/tty device
            :type serialPort: string
            :param serialEOL: COM/tty device
            :type serialPort: string
        """
        self.ser: serial.Serial = serial.Serial(port=serialPort,
                                 baudrate=baud_rate,
                                 parity=parity,
                                 stopbits=stopbits)
        self.serial_eol = serialEOL

        self.debug = debug

    def _sendCommand(self, command):
        """
            Sends a command to the serial port of a power supply

            :param command: Command to send
            :type command: string
        """
        if self.debug:
            print(">> ", command.strip())
        
        command = f"{command}{self.serial_eol}"

        self.ser.write(command.encode("ascii"))
        # Give it time to process
        time.sleep(0.2)

    def _readBytes(self):
        """
            Read serial output as a stream of bytes

            :return: Bytes read as a list of integers
        """
        out = []

        while self.ser.in_waiting > 0:
            out.append(ord(self.ser.read(1)))

        if self.debug:
            print("<< ", [f"0x{v:02x}" for v in out])

        return out

    def _readOutput(self):
        """
            Read serial otput as a string

            :return: Data read as a string
        """
        out = ""

        while self.ser.in_waiting > 0:
            out += self.ser.read(1).decode("ascii")

        if self.debug:
            print("<< ", out.strip())

        return out

    def close(self):
        """
            Closes the serial port
        """
        self.ser.close()