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

"""JsonSingleInboundMessageDeserializer Module."""

import json

from wolk.models.ActuatorCommand import ActuatorCommand
from wolk.models.ActuatorCommandType import ActuatorCommandType
from wolk.models.ConfigurationCommand import ConfigurationCommand
from wolk.models.ConfigurationCommandType import ConfigurationCommandType
from wolk.models.FileTransferPacket import FileTransferPacket
from wolk.models.FirmwareCommand import FirmwareCommand
from wolk.models.FirmwareCommandType import FirmwareCommandType
from wolk.interfaces.InboundMessageDeserializer import InboundMessageDeserializer
from wolk import LoggerFactory


class JsonSingleInboundMessageDeserializer(InboundMessageDeserializer):
    """
    Deserialize messages received from the WolkAbout IoT Platform.

    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    """

    def __init__(self, device):
        """
        Create inbound topics from device key.

        :param device: Device with key and actuator references used for inbound topics 
        :type message: wolk.models.Device.Device
        """
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug("Init: device %s", device)

        inbound_topics = [
            "service/commands/firmware/" + device.key,
            "service/binary/" + device.key,
            "configurations/commands/" + device.key,
            "pong/" + device.key,
        ]

        for reference in device.actuator_references:
            inbound_topics.append("actuators/commands/" + device.key + "/" + reference)

        super().__init__(inbound_topics)

    def is_actuation_command(self, message):
        """
        Check if message is actuation command

        :param message: The message received
        :type message: wolk.models.InboundMessage.InboundMessage
        :returns: actuation_command
        :rtype: bool
        """
        if message.topic.startswith("actuators/commands/"):
            return True
        return False

    def is_firmware_command(self, message):
        """
        Check if message is firmware command

        :param message: The message received
        :type message: wolk.models.InboundMessage.InboundMessage
        :returns: firmware_command
        :rtype: bool
        """
        if message.topic.startswith("service/commands/firmware/"):
            return True
        return False

    def is_file_chunk(self, message):
        """
        Check if message is file chunk

        :param message: The message received
        :type message: wolk.models.InboundMessage.InboundMessage
        :returns: file_chunk
        :rtype: bool
        """
        if message.topic.startswith("service/binary/"):
            return True
        return False

    def is_configuration(self, message):
        """
        Check if message is configuration

        :param message: The message received
        :type message: wolk.models.InboundMessage.InboundMessage
        :returns: configuration
        :rtype: bool
        """
        if message.topic.startswith("configurations/commands/"):
            return True
        return False

    def deserialize_actuator_command(self, message):
        """
        Deserialize the message into an actuation command.

        :param message: Message to be deserialized
        :type message: wolk.models.InboundMessage.InboundMessage

        :returns: actuation
        :rtype: wolk.models.ActuatorCommand.ActuatorCommand
        """
        self.logger.debug("deserialize_actuator_command called")
        reference = message.topic.split("/")[-1]
        payload = json.loads(message.payload.decode("utf-8"))
        command = payload.get("command")

        if str(command) == "SET":

            command_type = ActuatorCommandType.SET
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

            command_type = ActuatorCommandType.STATUS
            actuation = ActuatorCommand(reference, command_type)
            self.logger.info(
                "Received actuation command - Reference: %s ;" " Command: STATUS ",
                actuation.reference,
            )
            return actuation

        else:

            command_type = ActuatorCommandType.UNKNOWN
            actuation = ActuatorCommand(reference, command_type)
            self.logger.warning(
                "Received unknown actuation command on topic - : %s ; Payload: %s",
                message.topic,
                message.payload,
            )
            return actuation

    def deserialize_firmware_command(self, message):
        """
        Deserialize the message into a firmware command.

        :param message: Message to be deserialized
        :type message: wolk.models.InboundMessage.InboundMessage

        :returns: firmware_command
        :rtype: wolk.models.FirmwareCommand.FirmwareCommand
        """
        self.logger.debug("deserialize_firmware_command called")
        payload = json.loads(message.payload.decode("utf-8"))
        command = payload.get("command")

        if command == "FILE_UPLOAD":

            command = FirmwareCommandType.FILE_UPLOAD
            firmware_command = FirmwareCommand(
                command,
                payload.get("fileName"),
                payload.get("fileSize"),
                payload.get("fileHash"),
                payload.get("autoInstall"),
            )
            self.logger.debug(
                "deserialize_firmware_command - Command: %s ; "
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

            command = FirmwareCommandType.URL_DOWNLOAD
            firmware_command = FirmwareCommand(
                command,
                file_url=payload.get("fileUrl"),
                auto_install=payload.get("autoInstall"),
            )
            self.logger.debug(
                "deserialize_firmware_command - Command: %s ; "
                "File url: %s ; Auto install: %s",
                firmware_command.command,
                firmware_command.file_url,
                firmware_command.auto_install,
            )
            return firmware_command

        elif command == "INSTALL":

            command = FirmwareCommandType.INSTALL

            firmware_command = FirmwareCommand(command)
            self.logger.debug(
                "deserialize_firmware_command - Command: %s", firmware_command.command
            )
            return firmware_command

        elif command == "ABORT":

            command = FirmwareCommandType.ABORT

            firmware_command = FirmwareCommand(command)
            self.logger.debug(
                "deserialize_firmware_command - Command: %s", firmware_command.command
            )
            return firmware_command

        else:

            command = FirmwareCommandType.UNKNOWN

            firmware_command = FirmwareCommand(command)
            self.logger.debug(
                "deserialize_firmware_command - Command: %s", firmware_command.command
            )
            return firmware_command

    def deserialize_firmware_chunk(self, message):
        """
        Split the message into a packet.

        :param message: Message to be deserialized
        :type message: wolk.models.InboundMessage.InboundMessage

        :returns: packet
        :rtype: wolk.models.FileTransferPacket.FileTransferPacket
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
        :type message: wolk.models.InboundMessage.InboundMessage

        :returns: configuration
        :rtype: wolk.models.ConfigurationCommand.ConfigurationCommand
        """
        self.logger.debug("deserialize_configuration_command called")
        payload = json.loads(message.payload.decode("utf-8"))
        command = payload.get("command")

        if command == "SET":

            command = ConfigurationCommandType.SET

            configuration = ConfigurationCommand(command, payload.get("values"))

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
                                values_list = [float(value) for value in values_list]
                            else:
                                values_list = [int(value) for value in values_list]
                        except ValueError:
                            pass

                        configuration.values[reference] = tuple(values_list)

            return configuration

        elif command == "CURRENT":

            command = ConfigurationCommandType.CURRENT

            configuration = ConfigurationCommand(command)
            self.logger.info("Received configuration command - Command: CURRENT")
            return configuration

        else:

            command = ConfigurationCommandType.UNKNOWN

            configuration = ConfigurationCommand(command)
            self.logger.warning(
                "Received configuration command - Command: %s", configuration.command
            )
            return configuration
