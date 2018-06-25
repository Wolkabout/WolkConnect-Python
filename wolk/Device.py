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
Device module.

Contains Device class that holds connection credentials.
"""
from wolk import LoggerFactory


class Device:
    """

    Contains required information for connecting to the WolkAbout IoT Platform.

    :ivar actuator_references: actuator references defined in device manifest
    :vartype actuator_references: list
    :ivar key: key obtained when creating device on WolkAbout IoT Platform
    :vartype key: str
    :ivar logger: Logger instance issued from the LoggerFactory class
    :vartype logger: logger
    :ivar password: password obtained when creating device on platform
    :vartype password: str

    """

    def __init__(self, key, password, actuator_references=None):
        """
        Contain device credentials necessary for connection to the platform.

        :param key: key obtained when creating device on WolkAbout IoT Platform
        :type key: str
        :param password: password obtained when creating device on platform
        :type password: str
        :param actuator_references: references defined in device manifest
        :type actuator_references: list or None, optional
        """
        self.key = key
        self.password = password
        self.actuator_references = actuator_references
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(
            "Init - Key: %s ; Password: %s ; Actuator references: %s",
            key,
            password,
            actuator_references,
        )
