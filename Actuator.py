#   Copyright 2017 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

""" Actuators
"""

from enum import Enum, unique
from ReadingType import ReadingType, DataType

@unique
class ActuatorState(Enum):
    """ Actuator states
    """
    READY = "READY"
    BUSY = "BUSY"
    ERROR = "ERROR"
    DISABLED = "DISABLED"

@unique
class ActuatorType(ReadingType):
    """ Actuator types
    """
    SWITCH = ("SW", DataType.BOOLEAN, ActuatorState.READY)
    SLIDER = ("SL", DataType.NUMERIC, ActuatorState.READY)

    def __init__(self, ref, dataType, actuatorState, dataSize=1, dataDelimiter=""):
        ReadingType.__init__(self, ref, dataType, dataSize=1, dataDelimiter="")
        self.state = actuatorState

    def __str__(self):
        superString = super().strRepresentation
        actuatorStateString = " state={0}".format(self.state.value)
        return superString + actuatorStateString


class ActuationException(Exception):
    """ ActuationException is raised whenever there is an error in
        actuation of an actuator
    """
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)

class Actuator():
    """  Actuator with ReadingType
    """
    def __init__(self, actuatorType, value=None):
        self.actuatorType = actuatorType
        self.value = value

    def setValue(self, value):
        """ Set actuator value
        """
        self.actuatorType.state = ActuatorState.BUSY
        if not self.actuatorType:
            self.actuatorType.state = ActuatorState.ERROR
            raise ActuationException("Actuator type missing")

class SwitchActuator(Actuator):
    """ Switch actuator
    """
    def __init__(self, value):
        super().__init__(ActuatorType.SWITCH, value)

    def setValue(self, value):
        super().setValue(value)

        if value.upper == "TRUE" or value == "1":
            self.value = True
            self.actuatorType.state = ActuatorState.READY
        elif value.upper == "FALSE" or value == "0":
            self.value = False
            self.actuatorType.state = ActuatorState.READY
        else:
            self.actuatorType.state = ActuatorState.ERROR
            raise ActuationException("Could not set Switch actuator to value {0}".format(value))

class SliderActuator(Actuator):
    """ Slider actuator
    """
    def __init__(self, value):
        super().__init__(ActuatorType.SLIDER, value)

    def setValue(self, value):
        super().setValue(value)

        try:
            self.value = float(value)
            self.actuatorType.state = ActuatorState.READY
        except ValueError:
            self.actuatorType.state = ActuatorState.ERROR
            raise ActuationException("Could not set Slider actuator to value {0}".format(value))
