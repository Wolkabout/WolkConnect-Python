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
ActuatorStatus Module.
"""


class ActuatorStatus:
    """Current status of an actuator."""

    def __init__(self, reference, state, value):
        """
        Information about actuator status.

        :param reference: Reference of the actuator
        :type reference: str
        :param state: Actuators current state
        :type state: wolk.models.ActuatorState.ActuatorState
        :param value: Actuators current value
        :type value: int or float or str
        """
        self.reference = reference
        self.state = state
        self.value = value
