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

@unique
class ActuatorState(Enum):
    """ Actuator states
    """
    READY = "READY"
    BUSY = "BUSY"
    ERROR = "ERROR"

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
    """ Actuator as defined in device manifest
        actuatorRef - Actuator reference
        dataType - Any of DataType values (NUMERIC, STRING or BOOLEAN)
        actuatorState - Any of ActuatorState values (READY, BUSY, ERROR)
        value - Current value of the actuator.
    """
    def __init__(self, actuatorRef, dataType, actuatorState=ActuatorState.READY, value=None):
        self.actuatorRef = actuatorRef
        self.dataType = dataType
        self.actuatorState = actuatorState
        self.value = value

    def setValue(self, value):
        """ Set actuator value
        """
        self.actuatorState = ActuatorState.BUSY
        if not self.actuatorRef:
            self.actuatorState = ActuatorState.ERROR
            raise ActuationException("Actuator type missing")

        self.value = value
        self.actuatorState = ActuatorState.READY

    def __str__(self):
        actuatorStateString = "{0}:{1} state={2}".format(self.actuatorRef, self.dataType.value, self.actuatorState.value)
        return actuatorStateString
