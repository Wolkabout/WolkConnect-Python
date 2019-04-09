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
InboundMessageDeserializer Module.
"""


class InboundMessageDeserializer(ABC):
    """Deserialize messages received from the platform."""

    @abstractmethod
    def is_actuation_command(self, message):
        """
        Check if message is actuation command

        :param message: The message received
        :type message: wolk.wolkcore.InboundMessage.InboundMessage
        :returns: actuation_command
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_firmware_command(self, message):
        """
        Check if message is firmware command

        :param message: The message received
        :type message: wolk.wolkcore.InboundMessage.InboundMessage
        :returns: firmware_command
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_file_chunk(self, message):
        """
        Check if message is file chunk

        :param message: The message received
        :type message: wolk.wolkcore.InboundMessage.InboundMessage
        :returns: file_chunk
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_configuration(self, message):
        """
        Check if message is configuration

        :param message: The message received
        :type message: wolk.wolkcore.InboundMessage.InboundMessage
        :returns: configuration
        :rtype: bool
        """
        pass

    @abstractmethod
    def deserialize_actuator_command(self, message):
        """
        Deserialize the message into an ActuatorCommand.

        :param message: The message received
        :type message: wolk.wolkcore.InboundMessage.InboundMessage
        :returns: actuation
        :rtype: wolk.wolkcore.ActuatorCommand.ActuatorCommand
        """
        pass

    @abstractmethod
    def deserialize_firmware_command(self, message):
        """
        Deserialize the message into a FirmwareCommand.

        :param message: The message received
        :type message: wolk.wolkcore.InboundMessage.InboundMessage
        :returns: firmware_command
        :rtype: wolk.wolkcore.FirmwareCommand.FirmwareCommand
        """
        pass

    @abstractmethod
    def deserialize_firmware_chunk(self, message):
        """
        Deserialize the message into a tuple of bytes.

        :param message: The message received
        :type message: wolk.wolkcore.InboundMessage.InboundMessage
        :returns: (previous_hash, chunk, chunk_hash)
        :rtype: (bytes, bytes, bytes)
        """
        pass

    @abstractmethod
    def deserialize_configuration_command(self, message):
        """
        Deserialize the message into a ConfigurationCommand.

        :param message: The message received
        :type message: wolk.wolkcore.InboundMessage.InboundMessage
        :returns: configuration
        :rtype: wolk.wolkcore.ConfigurationCommand.ConfigurationCommand
        """
        pass
