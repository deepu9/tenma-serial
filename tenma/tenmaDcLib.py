#    Copyright (C) 2017-2023 Jordi Castells
#
#
#   this file is part of tenma-serial
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>

"""
    tenmaDcLib is small python library to control a Tenma 72-XXXX programmable
    DC power supply, either from USB or Serial.

    Supported models:

     * 72_2545 -> Tested on HW
     * 72_2535 -> Set as manufacturer manual (not tested)
     * 72_2540 -> Tested on HW
     * 72_2550 -> Tested on HW
     * 72-2705 -> Tested on HW
     * 72_2930 -> Set as manufacturer manual (not tested)
     * 72_2940 -> Set as manufacturer manual (not tested)
     * 72_13320 -> Set as manufacturer manual (not tested)
     * 72_13330 -> Tested on HW
     * 72_13360 -> Tested on HW

    Other units from Korad or Vellman might work as well since
    they use the same serial protocol.
"""


def instantiate_tenma_class_from_device_response(device, debug=False):
    """
        Get a proper Tenma subclass depending on the version
        response from the unit.

        The subclasses mainly deal with the limit checks for each
        unit.
    """
    # First instantiate base to retrieve version
    powerSupply = Tenma72Base(device, debug=debug)
    ver = powerSupply.getVersion()
    if not ver:
        if debug:
            print("No version found, retrying with newline EOL")
        ver = powerSupply.getVersion(serialEol="\n")
    powerSupply.close()

    for cls in findSubclassesRecursively(Tenma72Base):
        for matchString in cls.MATCH_STR:
            if matchString in ver:
                return cls(device, debug=debug)

    print("Could not detect Tenma power supply model, assuming 72_2545")
    return Tenma72_2545(device, debug=debug)


def findSubclassesRecursively(cls):
    """
        Finds all subclasses of a given class recursively
    """
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(findSubclassesRecursively(subclass))
    return all_subclasses

