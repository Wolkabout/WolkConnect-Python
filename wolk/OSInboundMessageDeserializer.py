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

"""OSInboundMessageDeserializer Module."""

import json

from wolk.wolkcore import ActuatorCommand
from wolk.wolkcore import ActuatorCommandType
from wolk.wolkcore import ConfigurationCommand
from wolk.wolkcore import ConfigurationCommandType
from wolk.wolkcore import FileTransferPacket
from wolk.wolkcore import FirmwareCommand
from wolk.wolkcore import FirmwareCommandType
from wolk.wolkcore import InboundMessageDeserializer
from wolk import LoggerFactory


class OSInboundMessageDeserializer(InboundMessageDeserializer):
    """
    Deserialize messages received from the WolkAbout IoT Platform.

    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    """

    def __init__(self):
        """Just logger init."""
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug("Init")

    def deserialize_actuator_command(self, message):
        """
        Deserialize the message into an actuation command.

        :param message: Message to be deserialized
        :type message: wolk.wolkcore.InboundMessage.InboundMessage

        :returns: actuation
        :rtype: wolk.wolkcore.ActuatorCommand.ActuatorCommand
        """
        self.logger.debug("deserialize_actuator_command called")
        reference = message.channel.split("/")[-1]
        payload = json.loads(message.payload)
        command = payload.get("command")

        if str(command) == "SET":

            command_type = ActuatorCommandType.ACTUATOR_COMMAND_TYPE_SET
            value = payload.get("value")
            if "\n" in value:
                value = value.replace("\n", "\\n")
                value = value.replace("\r", "")
            if value == "true":
                value = True
            elif value == "false":
                value = False

            actuation = ActuatorCommand(reference, command_type, value)
            self.logger.info(
                "Received actuation command - Reference: %s ; Command: SET ;"
                " Value: %s",
                actuation.reference,
                actuation.value,
            )
            return actuation

        elif str(command) == "STATUS":

            command_type = ActuatorCommandType.ACTUATOR_COMMAND_TYPE_STATUS
            actuation = ActuatorCommand(reference, command_type)
            self.logger.info(
                "Received actuation command - Reference: %s ;"
                " Command: STATUS ",
                actuation.reference,
            )
            return actuation

        else:

            command_type = ActuatorCommandType.ACTUATOR_COMMAND_TYPE_UNKNOWN
            actuation = ActuatorCommand(reference, command_type)
            self.logger.warning(
                "Received actuation command - Reference: %s ;"
                " Command: %s (UNKNOWN)",
                actuation.reference,
                actuation.command,
            )
            return actuation

    def deserialize_firmware_command(self, message):
        """
        Deserialize the message into a firmware command.

        :param message: Message to be deserialized
        :type message: wolk.wolkcore.InboundMessage.InboundMessage

        :returns: firmware_command
        :rtype: wolk.wolkcore.FirmwareCommand.FirmwareCommand
        """
        self.logger.debug("deserialize_firmware_command called")
        payload = json.loads(message.payload)
        command = payload.get("command")

        if command == "FILE_UPLOAD":

            command = FirmwareCommandType.FIRMWARE_COMMAND_TYPE_FILE_UPLOAD
            firmware_command = FirmwareCommand(
                command,
                payload.get("fileName"),
                payload.get("fileSize"),
                payload.get("fileHash"),
                payload.get("autoInstall"),
            )
            self.logger.debug(
                "deserialize_firmware_command - Command: %s (FILE_UPLOAD) ; "
                "File name: %s ; File size: %s ; "
                "File hash: %s ; Auto install: %s",
                firmware_command.command,
                firmware_command.file_name,
                firmware_command.file_size,
                firmware_command.file_hash,
                firmware_command.auto_install,
            )
            return firmware_command

        elif command == "URL_DOWNLOAD":

            command = FirmwareCommandType.FIRMWARE_COMMAND_TYPE_URL_DOWNLOAD
            firmware_command = FirmwareCommand(
                command,
                file_url=payload.get("fileUrl"),
                auto_install=payload.get("autoInstall"),
            )
            self.logger.debug(
                "deserialize_firmware_command - Command: %s (URL_DOWNLOAD) ; "
                "File url: %s ; Auto install: %s",
                firmware_command.command,
                firmware_command.file_url,
                firmware_command.auto_install,
            )
            return firmware_command

        elif command == "INSTALL":

            command = FirmwareCommandType.FIRMWARE_COMMAND_TYPE_INSTALL

            firmware_command = FirmwareCommand(command)
            self.logger.debug(
                "deserialize_firmware_command - Command: %s (INSTALL)",
                firmware_command.command,
            )
            return firmware_command

        elif command == "ABORT":

            command = FirmwareCommandType.FIRMWARE_COMMAND_TYPE_ABORT

            firmware_command = FirmwareCommand(command)
            self.logger.debug(
                "deserialize_firmware_command - Command: %s (ABORT)",
                firmware_command.command,
            )
            return firmware_command

        else:

            command = FirmwareCommandType.FIRMWARE_COMMAND_TYPE_UNKNOWN

            firmware_command = FirmwareCommand(command)
            self.logger.debug(
                "deserialize_firmware_command - Command: %s (UNKNOWN)",
                firmware_command.command,
            )
            return firmware_command

    def deserialize_firmware_chunk(self, message):
        """
        Split the message into a packet.

        :param message: Message to be deserialized
        :type message: wolk.wolkcore.InboundMessage.InboundMessage

        :returns: packet
        :rtype: wolk.wolkcore.FileTransferPacket.FileTransferPacket
        """
        self.logger.debug("deserialize_firmware_chunk called")
        previous_hash = message.payload[:32]
        data = message.payload[32 : len(message.payload) - 32]
        current_hash = message.payload[-32:]

        packet = FileTransferPacket(previous_hash, data, current_hash)
        self.logger.debug(
            "deserialize_firmware_chunk - Previous hash: %s ; "
            "Data size: %s ; Current hash: %s",
            packet.previous_hash,
            len(packet.data),
            packet.current_hash,
        )
        return packet

    def deserialize_configuration_command(self, message):
        """
        Deserialize the message into a configuration command.

        :param message: message to be deserialized
        :type message: wolk.wolkcore.InboundMessage.InboundMessage

        :returns: configuration
        :rtype: wolk.wolkcore.ConfigurationCommand.ConfigurationCommand
        """
        self.logger.debug("deserialize_configuration_command called")
        payload = json.loads(message.payload)
        command = payload.get("command")

        if command == "SET":

            command = ConfigurationCommandType.CONFIGURATION_COMMAND_TYPE_SET

            configuration = ConfigurationCommand(
                command, payload.get("values")
            )

            self.logger.info(
                "Received configuration command - Command: SET  Values: %s",
                configuration.values,
            )

            for reference, value in configuration.values.items():
                if "\n" in value:
                    value = value.replace("\n", "\\n")
                    value = value.replace("\r", "")
                if value == "true":
                    value = True
                elif value == "false":
                    value = False

                if isinstance(value, bool):
                    pass
                else:
                    if "," in value:
                        values_list = value.split(",")
                        try:
                            if any("." in value for value in values_list):
                                values_list = [
                                    float(value) for value in values_list
                                ]
                            else:
                                values_list = [
                                    int(value) for value in values_list
                                ]
                        except ValueError:
                            pass

                        configuration.values[reference] = tuple(values_list)

            return configuration

        elif command == "CURRENT":

            command = (
                ConfigurationCommandType.CONFIGURATION_COMMAND_TYPE_CURRENT
            )

            configuration = ConfigurationCommand(command)
            self.logger.info(
                "Received configuration command - Command: CURRENT"
            )
            return configuration

        else:

            command = (
                ConfigurationCommandType.CONFIGURATION_COMMAND_TYPE_UNKNOWN
            )

            configuration = ConfigurationCommand(command)
            self.logger.warning(
                "Received configuration command - Command: %s (UNKONWN)",
                configuration.command,
            )
            return configuration
