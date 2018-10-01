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

"""ActuatorStatusProvider Module."""


class ActuatorStatusProvider:
    """Read the status of device's actuators."""

    def get_actuator_status(self, reference):
        """
        Get current actuator status.

        Reads the status of actuator from device
        and returns as tuple containing actuator state and current value.
        Must be implemented as non blocking.
        Must be implemented as thread safe.

        The possible actuator states are:

        - ``wolk.ACTUATOR_STATE_READY``
        - ``wolk.ACTUATOR_STATE_BUSY``
        - ``wolk.ACTUATOR_STATE_ERROR``


        :param reference: Actuator reference
        :type reference: str
        :returns: (state, value)
        :rtype: (wolk.ActuatorState, int or float or str)
        """
        pass
