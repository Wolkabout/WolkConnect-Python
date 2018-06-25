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
Configuration Handler module.

Contains ConfigurationHandler "interface".
"""


class ConfigurationHandler:
    """
    Must be implemented in order to set to the configuration values received.

    The configuration values are issued from the WolkAbout IoT Platform.
    """

    def handle_configuration(self, configuration):
        """
        Update device configuration with received configuration values.

        Must be implemented as non blocking.
        Must be implemented as thread safe.

        :param configuration: dictionary of configuration reference/value pairs
        :type configuration: dict
        """
        pass
