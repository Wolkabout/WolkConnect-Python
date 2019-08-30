"""Deserialize messages received in JSON_PROTOCOL format."""
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

import json

from wolk.model.actuator_command import ActuatorCommand, ActuatorCommandType
from wolk.model.configuration_command import (
    ConfigurationCommand,
    ConfigurationCommandType,
)
from wolk.model.device import Device
from wolk.model.FileTransferPackage import FileTransferPackage
from wolk.model.Message import Message
from wolk.interface.message_deserializer import MessageDeserializer
from wolk import logger_factory


class JSONProtocolMessageDeserializer(MessageDeserializer):
    """
    Deserialize messages received from the WolkAbout IoT Platform.

    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    """

    def __init__(self, device: Device) -> None:
        """
        Create inbound topics from device key.

        :param device: Device key and actuator references for inbound topics
        :type device: Device
        """
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(f"{device}")

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
        self.logger.debug(f"inbound topics: {inbound_topics}")
        super().__init__(inbound_topics)

    def is_actuation_command(self, message: Message) -> bool:
        """
        Check if message is actuation command.

        :param message: The message received
        :type message: Message
        :returns: actuation_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/actuator")

    def is_firmware_install(self, message: Message) -> bool:
        """
        Check if message is firmware update install command.

        :param message: The message received
        :type message: Message
        :returns: firmware_update_install_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/firmware_update_install")

    def is_firmware_abort(self, message: Message) -> bool:
        """
        Check if message is firmware update command.

        :param message: The message received
        :type message: Message
        :returns: firmware_update_abort_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/firmware_update_abort")

    def is_file_binary_response(self, message: Message) -> bool:
        """
        Check if message is file binary message.

        :param message: The message received
        :type message: Message
        :returns: file_chunk
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_binary")

    def is_configuration_command(self, message: Message) -> bool:
        """
        Check if message is configuration command.

        :param message: The message received
        :type message: Message
        :returns: configuration
        :rtype: bool
        """
        return message.topic.startswith("p2d/configuration")

    def is_file_delete_command(self, message: Message) -> bool:
        """
        Check if message if file delete command.

        :param message: The message received
        :type message: Message
        :returns: file_delete_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_delete")

    def is_file_purge_command(self, message: Message) -> bool:
        """
        Check if message if file purge command.

        :param message: The message received
        :type message: Message
        :returns: file_purge_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_purge")

    def is_file_list_confirm(self, message: Message) -> bool:
        """
        Check if message is file list confirm.

        :param message: The message received
        :type message: Message
        :returns: file_list_confirm
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_list_confirm")

    def is_file_list_request(self, message: Message) -> bool:
        """
        Check if message is file list request.

        :param message: The message received
        :type message: Message
        :returns: file_list_request
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_list_request")

    def is_file_upload_initiate(self, message: Message) -> bool:
        """
        Check if message is file upload command.

        :param message: The message received
        :type message: Message
        :returns: file_upload_initiate_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_upload_initiate")

    def is_file_upload_abort(self, message: Message) -> bool:
        """
        Check if message is file upload command.

        :param message: The message received
        :type message: Message
        :returns: file_upload_abort_command
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_upload_abort")

    def is_file_url_install(self, message: Message) -> bool:
        """
        Check if message is file URL download command.

        :param message: The message received
        :type message: Message
        :returns: file_url_download_initiate
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_url_download_initiate")

    def is_file_url_abort(self, message: Message) -> bool:
        """
        Check if message is file URL download command.

        :param message: The message received
        :type message: Message
        :returns: file_url_download_abort
        :rtype: bool
        """
        return message.topic.startswith("p2d/file_url_download_abort")

    def parse_actuator_command(self, message):
        """
        Parse the message into an actuation command.

        :param message: Message to be deserialized
        :type message: wolk.models.Message.Message

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
            self.logger.info(f"Received actuation command: {actuation}")
            return actuation

        elif "actuator_get" in message.topic:

            command_type = ActuatorCommandType.GET
            actuation = ActuatorCommand(reference, command_type)
            self.logger.info(f"Received actuation command: {actuation}")
            return actuation

    def parse_firmware_install(self, message: Message) -> str:
        """
        Return file name from message.

        :param message: The message received
        :type message: Message
        :returns: file_name
        :rtype: str
        """
        payload = json.loads(message.payload.decode("utf-8"))
        file_name = payload.at("fileName")
        self.logger.debug(f"File name: {file_name}")
        return file_name

    def parse_file_binary(self, message: Message) -> FileTransferPackage:
        """
        Parse the message into a file transfer package.

        :param message: The message received
        :type message: Message
        :returns: file_transfer_package
        :rtype: FileTransferPackage
        """
        previous_hash = message.payload[:32]
        data = message.payload[32 : len(message.payload) - 32]
        current_hash = message.payload[-32:]

        file_transfer_package = FileTransferPackage(
            previous_hash, data, current_hash
        )
        self.logger.debug(
            f"Received file transfer package: {file_transfer_package}"
        )
        return file_transfer_package

    def parse_configuration(self, message: Message) -> ConfigurationCommand:
        """
        Parse the message into a configuration command.

        :param message: The message received
        :type message: Message

        :returns: configuration
        :rtype: ConfigurationCommand
        """
        payload = json.loads(message.payload.decode("utf-8"))

        if "configuration_set" in message.topic:

            command = ConfigurationCommandType.SET

            configuration = ConfigurationCommand(command, payload)

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

        elif "configuration_get" in message.topic:
            command = ConfigurationCommandType.GET
            configuration = ConfigurationCommand(command)

        self.logger.info(f"Received configuration command: {configuration}")
        return configuration

    def parse_file_delete_command(self, message: Message) -> str:
        """
        Parse the message into a file name to delete.

        :param message: The message received
        :type message: Message
        :returns: file_name
        :rtype: str
        """
        payload = json.loads(message.payload.decode("utf-8"))
        if "fileName" not in payload:
            self.logger.error(
                "Received firmware update install command"
                " with invalid payload! %s",
                message.payload.decode("utf-8"),
            )
            return

        return payload.at("fileName")

    def parse_file_url(self, message: Message) -> str:
        """
        Parse the message into a URL string.

        :param message: The message received
        :type message: Message
        :returns: file_url
        :rtype: str
        """
        payload = json.loads(message.payload.decode("utf-8"))
        if "fileUrl" not in payload:
            self.logger.error(
                "Received firmware update install command"
                " with invalid payload! %s",
                message.payload.decode("utf-8"),
            )
            return

        return payload.at("fileUrl")
