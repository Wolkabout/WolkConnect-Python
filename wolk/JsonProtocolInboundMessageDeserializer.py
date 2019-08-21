#   Copyright 2019 WolkAbout Technology s.r.o.
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

"""JsonProtocolInboundMessageDeserializer Module."""

import json

from wolk.models.ActuatorCommand import ActuatorCommand
from wolk.models.ActuatorCommandType import ActuatorCommandType
from wolk.models.ConfigurationCommand import ConfigurationCommand
from wolk.models.ConfigurationCommandType import ConfigurationCommandType
from wolk.interfaces.InboundMessageDeserializer import (
    InboundMessageDeserializer,
)
from wolk.models.InboundMessage import InboundMessage
from wwolk.models.FirmwareUpdateCommand import FirmwareUpdateCommand
from wwolk.models.FirmwareUpdateCommandType import FirmwareUpdateCommandType
from wolk.models.FileTransferPackage import FileTransferPackage
from wolk import LoggerFactory


class JsonProtocolInboundMessageDeserializer(InboundMessageDeserializer):
    """
    Deserialize messages received from the WolkAbout IoT Platform.

    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    """

    def __init__(self, device):
        """
        Create inbound topics from device key.

        :param device: Device key and actuator references for inbound topics
        :type message: wolk.models.Device.Device
        """
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug("Init: device %s", device)

        inbound_topics = [
            "p2d/configuration_get/d/" + device.key,
            "p2d/configuration_set/d/" + device.key,
            "p2d/file_binary_response/d/" + device.key,
            "p2d/file_delete/d/" + device.key,
            "p2d/file_purge/d/" + device.key,
            "p2d/file_list_confirm/d/" + device.key,
            "p2d/file_list_request/d/" + device.key,
            "p2d/file_upload_abort/d/" + device.key,
            "p2d/file_upload_initiate/d/" + device.key,
            "p2d/file_url_download_abort/d/" + device.key,
            "p2d/file_url_download_initiate/d/" + device.key,
            "p2d/firmware_update_abort/d/" + device.key,
            "p2d/firmware_update_install/d/" + device.key,
        ]

        for reference in device.actuator_references:
            inbound_topics.append(
                "p2d/actuator_set/d/" + device.key + "/r/" + reference
            )
            inbound_topics.append(
                "p2d/actuator_get/d/" + device.key + "/r/" + reference
            )

        super().__init__(inbound_topics)

    def is_actuation_command(self, message: InboundMessage) -> bool:
        """
        Check if message is actuation command.

        :param message: The message received
        :type message: InboundMessage
        :returns: actuation_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/actuator")

    def is_firmware_update_command(self, message: InboundMessage) -> bool:
        """
        Check if message is firmware command.

        :param message: The message received
        :type message: InboundMessage
        :returns: firmware_update_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/firmware_update")

    def is_file_binary_response(self, message: InboundMessage) -> bool:
        """
        Check if message is file binary message.

        :param message: The message received
        :type message: InboundMessage
        :returns: file_chunk
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_binary")

    def is_configuration_command(self, message: InboundMessage) -> bool:
        """
        Check if message is configuration command.

        :param message: The message received
        :type message: InboundMessage
        :returns: configuration
        :rtype: bool
        """
        return message.topic.startswith("p2d/configuration")

    def is_file_delete_command(self, message: InboundMessage) -> bool:
        """
        Check if message if file delete command.

        :param message: The message received
        :type message: InboundMessage
        :returns: file_delete_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_delete")

    def is_file_purge_command(self, message: InboundMessage) -> bool:
        """
        Check if message if file purge command.

        :param message: The message received
        :type message: InboundMessage
        :returns: file_purge_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_purge")

    def is_file_list_confirm(self, message: InboundMessage) -> bool:
        """
        Check if message is file list confirm.

        :param message: The message received
        :type message: InboundMessage
        :returns: file_list_confirm
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_list_confirm")

    def is_file_list_request(self, message: InboundMessage) -> bool:
        """
        Check if message is file list request.

        :param message: The message received
        :type message: InboundMessage
        :returns: file_list_request
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_list_request")

    def is_file_upload_command(self, message: InboundMessage) -> bool:
        """
        Check if message is file upload command.

        :param message: The message received
        :type message: InboundMessage
        :returns: file_upload_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_upload")

    def is_file_url_download_command(self, message: InboundMessage) -> bool:
        """
        Check if message is file URL download command.

        :param message: The message received
        :type message: InboundMessage
        :returns: file_url_download_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_url")

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

        if "actuator_set" in message.topic:

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

        elif "actuator_get" in message.topic:

            command_type = ActuatorCommandType.STATUS
            actuation = ActuatorCommand(reference, command_type)
            self.logger.info(
                "Received actuation command - Reference: %s ;"
                " Command: STATUS ",
                actuation.reference,
            )
            return actuation

        else:

            command_type = ActuatorCommandType.UNKNOWN
            actuation = ActuatorCommand(reference, command_type)
            self.logger.warning(
                "Received unknown actuation command on topic - : %s ;"
                " Payload: %s",
                message.topic,
                message.payload,
            )
            return actuation

    def deserialize_firmware_update_command(
        self, message: InboundMessage
    ) -> FirmwareUpdateCommand:
        """
        Deserialize the message into a FirmwareUpdateCommand.

        :param message: The message received
        :type message: InboundMessage
        :returns: firmware_update_command
        :rtype: FirmwareUpdateCommand
        """
        self.logger.debug("deserialize_firmware_update_command called")
        firmware_update_command = FirmwareUpdateCommand(
            FirmwareUpdateCommandType.UNKNOWN
        )
        if "abort" in message.topic:
            firmware_update_command.command = FirmwareUpdateCommandType.ABORT
        elif "install" in message.topic:
            payload = json.loads(message.payload.decode("utf-8"))
            if "fileName" not in payload:
                self.logger.error(
                    "Received firmware update install command"
                    " with invalid payload! %s",
                    message.payload.decode("utf-8"),
                )
                return firmware_update_command
            else:
                firmware_update_command.file_name = payload.at("fileName")
                firmware_update_command.command = (
                    FirmwareUpdateCommandType.INSTALL
                )

        return firmware_update_command

    def deserialize_file_binary(
        self, message: InboundMessage
    ) -> FileTransferPackage:
        """
        Deserialize the message into a file transfer package.

        :param message: The message received
        :type message: InboundMessage
        :returns: file_transfer_package
        :rtype: FileTransferPackage
        """
        self.logger.debug("deserialize_file_binary called")
        previous_hash = message.payload[:32]
        data = message.payload[32 : len(message.payload) - 32]
        current_hash = message.payload[-32:]

        file_transfer_package = FileTransferPackage(
            previous_hash, data, current_hash
        )
        self.logger.debug(
            "deserialize_firmware_chunk - Previous hash: %s ; "
            "Data size: %s ; Current hash: %s",
            file_transfer_package.previous_hash,
            len(file_transfer_package.data),
            file_transfer_package.current_hash,
        )
        return file_transfer_package

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

        if "configuration_set" in message.topic:

            command = ConfigurationCommandType.SET

            configuration = ConfigurationCommand(command, payload)

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

        elif "configuration_get" in message.topic:

            command = ConfigurationCommandType.CURRENT

            configuration = ConfigurationCommand(command)
            self.logger.info(
                "Received configuration command - Command: CURRENT"
            )
            return configuration

        else:

            command = ConfigurationCommandType.UNKNOWN

            configuration = ConfigurationCommand(command)
            self.logger.warning(
                "Received configuration command - Command: %s",
                configuration.command,
            )
            return configuration

    def deserialize_file_delete_command(self, message: InboundMessage) -> str:
        """
        Deserialize the message into a file name to delete.

        :param message: The message received
        :type message: InboundMessage
        :returns: file_name
        :rtype: str
        """
        self.logger.debug("deserialize_file_delete_command called")
        payload = json.loads(message.payload.decode("utf-8"))
        if "fileName" not in payload:
            self.logger.error(
                "Received firmware update install command"
                " with invalid payload! %s",
                message.payload.decode("utf-8"),
            )
            return None

        return payload.at("fileName")
