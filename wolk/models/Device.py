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

"""Device Module."""

from wolk import LoggerFactory


class Device:
    """
    Hold all necessary information to communicate with WolkAbout IoT Platform.

    :ivar actuator_references: Actuator references enabled on device
    :vartype actuator_references: list
    :ivar key: Device key obtained when creating device on WolkAbout IoT Platform
    :vartype key: str
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar password: Password obtained when creating device on WolkAbout IoT Platform
    :vartype password: str

    """

    def __init__(self, key, password, actuator_references=None):
        """
        Contain device credentials necessary for connection to WolkAbout IoT Platform.

        :param key: Device key obtained when creating device on WolkAbout IoT Platform
        :type key: str
        :param password: Password obtained when creating device on WolkAbout IoT Platform
        :type password: str
        :param actuator_references: Actuator references enabled on device
        :type actuator_references: list or None
        """
        self.key = key
        self.password = password
        if actuator_references:
            self.actuator_references = actuator_references
        else:
            self.actuator_references = list()
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(
            "Init - Key: %s ; Password: %s ; Actuator references: %s",
            key,
            password,
            actuator_references,
        )
