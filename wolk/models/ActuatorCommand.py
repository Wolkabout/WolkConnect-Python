#   Copyright 2018 WolkAbout Technology s.r.o.
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

"""
ActuatorCommand Module.
"""


class ActuatorCommand:
    """Deserialized actuator command sent from WolkAbout IoT Platform."""

    def __init__(self, reference, command, value=None):
        """
        Actuator command received.

        :param reference: Reference of the actuator
        :type reference: str
        :param command: Command to be executed
        :type command: wolk.models.ActuatorCommandType.ActuatorCommandType
        :param value: Value to be set to
        :type value: int or float or str or None
        """
        self.reference = reference
        self.command = command
        self.value = value
