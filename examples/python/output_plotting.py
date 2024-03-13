import time

# Import plotting library
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Import tenma library
from tenma.tenmaDcLib import get_tenma_device
from tenma.exceptions.base_exception import TenmaException

# Set here the device node to connect to
device_node = '/dev/ttyACM0'

# Retrieve a proper tenma handler for your unit (mainly tries to keep values
# within ranges)
tenma = get_tenma_device(device_node)

print(tenma.getVersion())

data = []
tstamps = []
while True:
    current = tenma.runningCurrent(1)
    voltage = tenma.runningVoltage(1)
    timestamp = time.time()

    data.append(voltage)
    tstamps.append(timestamp)

    plt.clf()
    plt.plot(tstamps, data)
    plt.pause(0.5)
