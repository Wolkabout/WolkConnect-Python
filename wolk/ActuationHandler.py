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
Actuation Handler module.

Contains ActuationHandler "interface".
"""


class ActuationHandler:
    """
    Must be implemented in order to execute actuation commands.

    Commands are issued from WolkAbout IoT Platform.
    """

    def handle_actuation(self, reference, value):
        """
        Set the actuator, identified by reference, to the value specified.

        :param reference: reference of the actuator
        :type reference: str
        :param value: value to set to
        :type value: int or float or str
        """
        pass
