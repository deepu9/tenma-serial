# Copyright (C) 2017 Jordi Castells
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
# @author Jordi Castells

"""
    Command line tenma control program for Tenma72_XXXX bank power supply
"""
import click

# TODO this is just a trick so tenmaControl runs cleanly from both the source tree
# and the pip installation
try:
    from tenma.tenmaDcLib import instantiate_tenma_class_from_device_response
    from tenma.exceptions.base_exception import TenmaException
except Exception:
    from tenmaDcLib import instantiate_tenma_class_from_device_response
    from exceptions.base_exception import TenmaException


@click.command()
@click.argument('device', default='/dev/ttyUSB0', type=str)
@click.option('-v', '--voltage', help='set mV', type=int)
@click.option('-c', '--current', help='set mA', type=int)
@click.option('-C', '--channel', help='channel to set (if not provided, 1 will be used)', type=int, default=1)
@click.option('-s', '--save', help='Save current configuration to Memory', type=int)
@click.option('-r', '--recall', help='Load configuration from Memory', type=int)
@click.option('-S', '--status', help='Retrieve and print system status', action="store_true", default=False)
@click.option('--ocp-enable', dest="ocp", help='Enable overcurrent protection', action="store_true", default=None)
@click.option('--ocp-disable', dest="ocp", help='Disable overcurrent pritection', action="store_false", default=None)
@click.option('--ovp-enable', dest="ovp", help='Enable overvoltage protection', action="store_true", default=None)
@click.option('--ovp-disable', dest="ovp",  help='Disable overvoltage pritection', action="store_false", default=None)
@click.option('--beep-enable', dest="beep", help='Enable beeps from unit', action="store_true", default=None)
@click.option('--beep-disable', dest="beep", help='Disable beeps from unit', action="store_false", default=None)
@click.option('--on', help='Set output to ON', action="store_true", default=False)
@click.option('--off', help='Set output to OFF', action="store_true", default=False)
@click.option('--verbose', help='Chatty program', action="store_true", default=False)
@click.option('--debug', help='print serial commands', action="store_true", default=False)
@click.option('--script', help='runs from script. Only print result of query, no version', action="store_true", default=False)
@click.option('--runningCurrent', help='returns the running output current', action="store_true", default=False)
@click.option('--runningVoltage', help='returns the running output voltage',action="store_true", default=False)
def main(
    device: str,
    voltage: int,
    current: int,
    channel: int,
    save: int,
    recall: int,
    status: bool,
    ocp_enable: bool,
    ocp_disable: bool,
    ovp_enable: bool,
    ovp_disable: bool,
    beep_enable: bool,
    beep_disable: bool,
    on: bool,
    off: bool,
    verbose: bool,
    debug: bool,
    script: bool,
    running_current: bool,
    running_voltage: bool
):

    T = None
    try:
        VERB = verbose
        T = instantiate_tenma_class_from_device_response(device, debug)
        if not script:
            print(f"VERSION: {T.getVersion()}")

        # On saving, we want to move to the proper memory 1st, then
        # perform the current/voltage/options setting
        # and after that, perform the save
        if save:
            if VERB:
                print("Recalling Memory", save)

            T.OFF()  # Turn off for safety
            T.recallConf(save)

        # Now, with memory, or no memory handling, perform the changes
        if ocp is not None:
            if VERB:
                if args["ocp"]:
                    print("Enable overcurrent protection")
                else:
                    print("Disable overcurrent protection")

            T.setOCP(args["ocp"])

        if args["ovp"] is not None:
            if VERB:
                if args["ovp"]:
                    print("Enable overvoltage protection")
                else:
                    print("Disable overvoltage protection")

            T.setOVP(args["ovp"])

        if args["beep"] is not None:
            if VERB:
                if args["beep"]:
                    print("Enable unit beep")
                else:
                    print("Disable unit beep")

            T.setBEEP(args["beep"])

        if voltage:
            if VERB:
                print(f"Setting voltage to {voltage}")
            T.setVoltage(channel, voltage)

        if current:
            if VERB:
                print("Setting current to ", current)
            T.setCurrent(channel, current)

        if save:
            if VERB:
                print("Saving to Memory", save)

            T.saveConfFlow(save, channel)

        if recall:
            if VERB:
                print("Loading from Memory: ", recall)

            T.recallConf(recall)
            volt = T.readVoltage(channel)
            curr = T.readCurrent(channel)

            print("Loaded from Memory: ", recall)
            print("Voltage:", volt)
            print("Current:", curr)

        if off:
            if VERB:
                print("Turning OUTPUT OFF")
            T.OFF()

        if on:
            if VERB:
                print("Turning OUTPUT ON")
            T.ON()

        if status:
            if VERB:
                print("Retrieving status")
            print(T.getStatus())

        if running_current:
            if VERB:
                print("Retrieving running Current")
            print(T.runningCurrent(channel))

        if running_voltage:
            if VERB:
                print("Retrieving running Voltage")
            print(T.runningVoltage(channel))

    except TenmaException as e:
        print("Lib ERROR: ", repr(e))
    finally:
        if VERB:
            print("Closing connection")
        if T:
            T.close()


if __name__ == "__main__":
    main()
