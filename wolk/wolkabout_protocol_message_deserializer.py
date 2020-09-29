"""Deserialize messages received in WolkAbout Protocol format."""
#   Copyright 2020 WolkAbout Technology s.r.o.
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
from distutils.util import strtobool
from typing import List
from typing import Tuple

from wolk import logger_factory
from wolk.interface.message_deserializer import MessageDeserializer
from wolk.model.actuator_command import ActuatorCommand
from wolk.model.configuration_command import ConfigurationCommand
from wolk.model.device import Device
from wolk.model.file_transfer_package import FileTransferPackage
from wolk.model.message import Message


class WolkAboutProtocolMessageDeserializer(MessageDeserializer):
    """
    Deserialize messages received from the WolkAbout IoT Platform.

    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    """

    DEVICE_PATH_DELIMITER = "d/"
    REFERENCE_PATH_PREFIX = "r/"
    CHANNEL_DELIMITER = "/"
    KEEP_ALIVE_RESPONSE = "pong/"
    ACTUATOR_SET = "p2d/actuator_set/"
    CONFIGURATION_SET = "p2d/configuration_set/"
    FILE_BINARY_RESPONSE = "p2d/file_binary_response/"
    FILE_DELETE = "p2d/file_delete/"
    FILE_PURGE = "p2d/file_purge/"
    FILE_LIST_CONFIRM = "p2d/file_list_confirm/"
    FILE_LIST_REQUEST = "p2d/file_list_request/"
    FILE_UPLOAD_ABORT = "p2d/file_upload_abort/"
    FILE_UPLOAD_INITIATE = "p2d/file_upload_initiate/"
    FILE_URL_DOWNLOAD_ABORT = "p2d/file_url_download_abort/"
    FILE_URL_DOWNLOAD_INITIATE = "p2d/file_url_download_initiate/"
    FIRMWARE_UPDATE_ABORT = "p2d/firmware_update_abort/"
    FIRMWARE_UPDATE_INSTALL = "p2d/firmware_update_install/"

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

        self.inbound_topics = [
            self.KEEP_ALIVE_RESPONSE + device.key,
            self.CONFIGURATION_SET + self.DEVICE_PATH_DELIMITER + device.key,
            self.FILE_BINARY_RESPONSE
            + self.DEVICE_PATH_DELIMITER
            + device.key,
            self.FILE_DELETE + self.DEVICE_PATH_DELIMITER + device.key,
            self.FILE_PURGE + self.DEVICE_PATH_DELIMITER + device.key,
            self.FILE_LIST_CONFIRM + self.DEVICE_PATH_DELIMITER + device.key,
            self.FILE_LIST_REQUEST + self.DEVICE_PATH_DELIMITER + device.key,
            self.FILE_UPLOAD_ABORT + self.DEVICE_PATH_DELIMITER + device.key,
            self.FILE_UPLOAD_INITIATE
            + self.DEVICE_PATH_DELIMITER
            + device.key,
            self.FILE_URL_DOWNLOAD_ABORT
            + self.DEVICE_PATH_DELIMITER
            + device.key,
            self.FILE_URL_DOWNLOAD_INITIATE
            + self.DEVICE_PATH_DELIMITER
            + device.key,
            self.FIRMWARE_UPDATE_ABORT
            + self.DEVICE_PATH_DELIMITER
            + device.key,
            self.FIRMWARE_UPDATE_INSTALL
            + self.DEVICE_PATH_DELIMITER
            + device.key,
        ]

        for reference in device.actuator_references:
            self.inbound_topics.append(
                self.ACTUATOR_SET
                + self.DEVICE_PATH_DELIMITER
                + device.key
                + self.CHANNEL_DELIMITER
                + self.REFERENCE_PATH_PREFIX
                + reference
            )
        self.logger.debug(f"inbound topics: {self.inbound_topics}")

    def get_inbound_topics(self) -> List[str]:
        """
        Return list of inbound topics for device.

        :returns: List of topics to subscribe to
        :rtype: List[str]
        """
        return self.inbound_topics

    def is_keep_alive_response(self, message: Message) -> bool:
        """
        Check if message is keep alive response.

        :param message: The message received
        :type message: Message
        :returns: keep_alive_response
        :rtype: bool
        """
        keep_alive_response = message.topic.startswith(
            self.KEEP_ALIVE_RESPONSE
        )
        self.logger.debug(
            f"{message.topic} is keep alive response: {keep_alive_response}"
        )
        return keep_alive_response

    def is_actuation_command(self, message: Message) -> bool:
        """
        Check if message is actuation command.

        :param message: The message received
        :type message: Message
        :returns: actuation_command
        :rtype: bool
        """
        actuation_command = message.topic.startswith(self.ACTUATOR_SET)
        self.logger.debug(
            f"{message.topic} is actuation command: {actuation_command}"
        )
        return actuation_command

    def is_firmware_install(self, message: Message) -> bool:
        """
        Check if message is firmware update install command.

        :param message: The message received
        :type message: Message
        :returns: firmware_update_install
        :rtype: bool
        """
        firmware_update_install = message.topic.startswith(
            self.FIRMWARE_UPDATE_INSTALL
        )
        self.logger.debug(
            f"{message.topic} is firmware install: {firmware_update_install}"
        )
        return firmware_update_install

    def is_firmware_abort(self, message: Message) -> bool:
        """
        Check if message is firmware update command.

        :param message: The message received
        :type message: Message
        :returns: firmware_update_abort
        :rtype: bool
        """
        firmware_update_abort = message.topic.startswith(
            self.FIRMWARE_UPDATE_ABORT
        )
        self.logger.debug(
            f"{message.topic} is firmware abort: {firmware_update_abort}"
        )
        return firmware_update_abort

    def is_file_binary_response(self, message: Message) -> bool:
        """
        Check if message is file binary message.

        :param message: The message received
        :type message: Message
        :returns: file_binary
        :rtype: bool
        """
        file_binary = message.topic.startswith(self.FILE_BINARY_RESPONSE)
        self.logger.debug(f"{message.topic} is file binary: {file_binary}")
        return file_binary

    def is_configuration_command(self, message: Message) -> bool:
        """
        Check if message is configuration command.

        :param message: The message received
        :type message: Message
        :returns: configuration
        :rtype: bool
        """
        configuration = message.topic.startswith(self.CONFIGURATION_SET)
        self.logger.debug(f"{message.topic} is configuration: {configuration}")
        return configuration

    def is_file_delete_command(self, message: Message) -> bool:
        """
        Check if message if file delete command.

        :param message: The message received
        :type message: Message
        :returns: file_delete_command
        :rtype: bool
        """
        file_delete_command = message.topic.startswith(self.FILE_DELETE)
        self.logger.debug(
            f"{message.topic} is file delete: {file_delete_command}"
        )
        return file_delete_command

    def is_file_purge_command(self, message: Message) -> bool:
        """
        Check if message if file purge command.

        :param message: The message received
        :type message: Message
        :returns: file_purge_command
        :rtype: bool
        """
        file_purge_command = message.topic.startswith(self.FILE_PURGE)
        self.logger.debug(
            f"{message.topic} is file purge: {file_purge_command}"
        )
        return file_purge_command

    def is_file_list_confirm(self, message: Message) -> bool:
        """
        Check if message is file list confirm.

        :param message: The message received
        :type message: Message
        :returns: file_list_confirm
        :rtype: bool
        """
        file_list_confirm = message.topic.startswith(self.FILE_LIST_CONFIRM)
        self.logger.debug(
            f"{message.topic} is file list confirm: {file_list_confirm}"
        )
        return file_list_confirm

    def is_file_list_request(self, message: Message) -> bool:
        """
        Check if message is file list request.

        :param message: The message received
        :type message: Message
        :returns: file_list_request
        :rtype: bool
        """
        file_list_request = message.topic.startswith(self.FILE_LIST_REQUEST)
        self.logger.debug(
            f"{message.topic} is file list request: {file_list_request}"
        )
        return file_list_request

    def is_file_upload_initiate(self, message: Message) -> bool:
        """
        Check if message is file upload command.

        :param message: The message received
        :type message: Message
        :returns: file_upload_initiate
        :rtype: bool
        """
        file_upload_initiate = message.topic.startswith(
            self.FILE_UPLOAD_INITIATE
        )
        self.logger.debug(
            f"{message.topic} is file upload init: {file_upload_initiate}"
        )
        return file_upload_initiate

    def is_file_upload_abort(self, message: Message) -> bool:
        """
        Check if message is file upload command.

        :param message: The message received
        :type message: Message
        :returns: file_upload_abort_command
        :rtype: bool
        """
        file_upload_abort_command = message.topic.startswith(
            self.FILE_UPLOAD_ABORT
        )
        self.logger.debug(
            f"{message.topic} is file purge: {file_upload_abort_command}"
        )
        return file_upload_abort_command

    def is_file_url_initiate(self, message: Message) -> bool:
        """
        Check if message is file URL download command.

        :param message: The message received
        :type message: Message
        :returns: file_url_download_init
        :rtype: bool
        """
        file_url_download_init = message.topic.startswith(
            self.FILE_URL_DOWNLOAD_INITIATE
        )
        self.logger.debug(
            f"{message.topic} is file url download: {file_url_download_init}"
        )
        return file_url_download_init

    def is_file_url_abort(self, message: Message) -> bool:
        """
        Check if message is file URL download command.

        :param message: The message received
        :type message: Message
        :returns: file_url_download_abort
        :rtype: bool
        """
        file_url_download_abort = message.topic.startswith(
            self.FILE_URL_DOWNLOAD_ABORT
        )
        self.logger.debug(
            f"{message.topic} is file url abort: {file_url_download_abort}"
        )
        return file_url_download_abort

    def parse_keep_alive_response(self, message: Message) -> int:
        """
        Parse the message into an UTC timestamp.

        :param message: The message received
        :type message: Message
        :returns: timestamp
        :rtype: int
        """
        self.logger.debug(f"{message}")
        payload = json.loads(message.payload.decode("utf-8"))  # type: ignore

        timestamp = payload["value"]

        self.logger.debug(f"received timestamp: {timestamp}")
        return timestamp

    def parse_actuator_command(self, message: Message) -> ActuatorCommand:
        """
        Parse the message into an actuation command.

        :param message: Message to be deserialized
        :type message: Message

        :returns: actuation
        :rtype: ActuatorCommand
        """
        self.logger.debug(f"{message}")
        reference = message.topic.split("/")[-1]

        payload = json.loads(message.payload.decode("utf-8"))  # type: ignore
        value = payload["value"]
        if "\\n" in value:
            value = value.replace("\\n", "\n")
        if value in ["true", "false"]:
            value = bool(strtobool(value))
        else:
            try:
                value = float(value)
            except ValueError:
                try:
                    value = int(value)
                except ValueError:
                    pass

        actuation = ActuatorCommand(reference, value)
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
        try:
            payload = json.loads(
                message.payload.decode("utf-8")  # type: ignore
            )
            file_name = payload["fileName"]
        except Exception:
            self.logger.warning(
                f"Received invalid firmware install message: {message}"
            )
            file_name = ""

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
        if not isinstance(message.payload, bytes):
            self.logger.warning(
                f"Expected payload in bytes, got {type(message.payload)}"
            )
            self.logger.info("Treating as invalid package")
            file_transfer_package = FileTransferPackage(b"", b"", b"")
        else:
            try:
                if len(message.payload) < 65:
                    raise ValueError(
                        "Received file transfer package too small"
                    )
                previous_hash = message.payload[:32]
                data = message.payload[32 : len(message.payload) - 32]
                current_hash = message.payload[-32:]

                file_transfer_package = FileTransferPackage(
                    previous_hash, data, current_hash
                )
                self.logger.debug(
                    "Received file transfer package: "
                    f"FileTransferPackage(previous_hash={previous_hash!r},"
                    f" data={len(data)} bytes, current_hash={current_hash!r}"
                )
            except Exception:
                self.logger.warning("Received malformed file chunk!")
                file_transfer_package = FileTransferPackage(b"", b"", b"")
        return file_transfer_package

    def parse_configuration(self, message: Message) -> ConfigurationCommand:
        """
        Parse the message into a configuration command.

        :param message: The message received
        :type message: Message

        :returns: configuration
        :rtype: ConfigurationCommand
        """
        self.logger.debug(f"{message}")

        payload = json.loads(message.payload.decode("utf-8"))  # type: ignore
        values = payload["values"]

        if isinstance(values, dict):
            for reference, value in values.items():
                if value in ["true", "false"]:
                    value = bool(strtobool(value))
                if isinstance(value, str):
                    value = value.replace("\\n", "\n")
                    try:
                        if "." in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass
                values[reference] = value

        configuration = ConfigurationCommand(values)
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
        self.logger.debug(f"{message}")
        try:
            payload = json.loads(
                message.payload.decode("utf-8")  # type: ignore
            )
            self.logger.debug(f'file name: {payload["fileName"]}')
            return payload["fileName"]
        except Exception:
            self.logger.warning(
                f"Failed to get file name from message {message}"
            )
            return ""

    def parse_file_url(self, message: Message) -> str:
        """
        Parse the message into a URL string.

        :param message: The message received
        :type message: Message
        :returns: file_url
        :rtype: str
        """
        self.logger.debug(f"{message}")
        try:
            payload = json.loads(
                message.payload.decode("utf-8")  # type: ignore
            )
            self.logger.debug(f'file URL: {payload["fileUrl"]}')
            return payload["fileUrl"]
        except Exception:
            self.logger.warning(
                f"Failed to get file URL from message {message}"
            )
            return ""

    def parse_file_initiate(self, message: Message) -> Tuple[str, int, str]:
        """
        Return file name, file size and file hash from message.

        :param message: The message received
        :type message: Message
        :returns: (file_name, file_size, file_hash)
        :rtype: Tuple[str, int, str]
        """
        self.logger.debug(f"{message}")
        try:
            payload = json.loads(
                message.payload.decode("utf-8")  # type: ignore
            )
            self.logger.debug(
                f'file_name={payload["fileName"]}, '
                f'file_size={payload["fileSize"]}, '
                f'file_hash={payload["fileHash"]}'
            )
            return (
                payload["fileName"],
                payload["fileSize"],
                payload["fileHash"],
            )
        except Exception:
            self.logger.warning(
                f"Received invalid file upload initiate message: {message}"
            )
            return "", 0, ""
