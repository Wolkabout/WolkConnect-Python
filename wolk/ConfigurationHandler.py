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

"""ConfigurationHandler Module."""


class ConfigurationHandler:
    """Set device's configuration options."""

    def handle_configuration(self, configuration):
        """
        Change device's configuration options.

        When the configuration command is given from WolkAbout IoT Platform, it will be delivered to this method.
        This function should update device configuration with received configuration values.
        Must be implemented as non blocking.
        Must be implemented as thread safe.

        :param configuration: Configuration option reference:value pairs
        :type configuration: dict
        """
        pass
