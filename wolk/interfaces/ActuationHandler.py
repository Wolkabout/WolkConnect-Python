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

from abc import ABC, abstractmethod

"""
ActuationHandler Module.
"""


class ActuationHandler(ABC):
    """Handle actuation commands received from WolkAbout IoT platform."""

    @abstractmethod
    def handle_actuation(self, reference, value):
        """
        Set actuator to value.

        When the actuation command is given from the platform, it will be delivered to this method.
        This method should pass the new value to the device's actuator.
        Must be implemented as non blocking.
        Must be implemented as thread safe.

        :param reference: Reference of the actuator
        :type reference: str
        :param value: Value to which to set the actuator
        :type value: int or float or str
        """
        pass
