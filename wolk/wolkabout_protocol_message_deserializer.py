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
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from wolk import logger_factory
from wolk.interface.message_deserializer import MessageDeserializer
from wolk.model.device import Device
from wolk.model.file_transfer_package import FileTransferPackage
from wolk.model.message import Message


class WolkAboutProtocolMessageDeserializer(MessageDeserializer):
    """
    Deserialize messages received from the WolkAbout IoT Platform.

    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    """

    PLATFORM_TO_DEVICE = "p2d/"
    CHANNEL_DELIMITER = "/"

    TIME = "time"
    PARAMETERS = "parameters"
    FEED_VALUES = "feed_values"

    FILE_BINARY = "file_binary_response"
    FILE_DELETE = "file_delete"
    FILE_PURGE = "file_purge"
    FILE_LIST = "file_list"
    FILE_UPLOAD_ABORT = "file_upload_abort"
    FILE_UPLOAD_INITIATE = "file_upload_initiate"
    FILE_URL_ABORT = "file_url_download_abort"
    FILE_URL_INITIATE = "file_url_download_initiate"

    FIRMWARE_ABORT = "firmware_update_abort"
    FIRMWARE_INSTALL = "firmware_update_install"

    def __init__(self, device: Device) -> None:
        """
        Create inbound topics from device key.

        :param device: Contains device key used for inbound topics
        :type device: Device
        """
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(f"{device}")
        self.key = device.key

        self.time_topic = self._form_topic(self.TIME)
        self.feed_values_topic = self._form_topic(self.FEED_VALUES)
        self.parameters_topic = self._form_topic(self.PARAMETERS)

        self.file_binary_topic = self._form_topic(self.FILE_BINARY)
        self.file_delete_topic = self._form_topic(self.FILE_DELETE)
        self.file_purge_topic = self._form_topic(self.FILE_PURGE)
        self.file_list = self._form_topic(self.FILE_LIST)
        self.file_upload_abort_topic = self._form_topic(self.FILE_UPLOAD_ABORT)
        self.file_upload_initiate_topic = self._form_topic(
            self.FILE_UPLOAD_INITIATE
        )
        self.file_url_abort_topic = self._form_topic(self.FILE_URL_ABORT)
        self.file_url_initiate_topic = self._form_topic(self.FILE_URL_INITIATE)

        self.firmware_abort_topic = self._form_topic(self.FIRMWARE_ABORT)
        self.firmware_install_topic = self._form_topic(self.FIRMWARE_INSTALL)

        self.inbound_topics = [
            self.time_topic,
            self.feed_values_topic,
            self.parameters_topic,
            self.file_binary_topic,
            self.file_delete_topic,
            self.file_purge_topic,
            self.file_list,
            self.file_upload_abort_topic,
            self.file_upload_initiate_topic,
            self.file_url_abort_topic,
            self.file_url_initiate_topic,
            self.firmware_abort_topic,
            self.firmware_install_topic,
        ]
        self.logger.debug(f"inbound topics: {self.inbound_topics}")

        self.file_management_message_checks = [
            self.is_file_purge_command,
            self.is_file_delete_command,
            self.is_file_binary_response,
            self.is_file_upload_initiate,
            self.is_file_upload_abort,
            self.is_file_list,
            self.is_file_url_initiate,
            self.is_file_url_abort,
        ]

        self.firmware_update_message_checks = [
            self.is_firmware_install,
            self.is_firmware_abort,
        ]

    def _form_topic(self, message_type: str) -> str:
        return (
            self.PLATFORM_TO_DEVICE
            + self.key
            + self.CHANNEL_DELIMITER
            + message_type
        )

    def get_inbound_topics(self) -> List[str]:
        """
        Return list of inbound topics for device.

        :returns: List of topics to subscribe to
        :rtype: List[str]
        """
        return self.inbound_topics

    def is_time_response(self, message: Message) -> bool:
        """
        Check if message is response to time request.

        :param message: The message received
        :type message: Message
        :returns: is_time_response
        :rtype: bool
        """
        is_time_response = message.topic == self.time_topic
        self.logger.debug(
            f"{message.topic} is time response: {is_time_response}"
        )
        return is_time_response

    def is_feed_values(self, message: Message) -> bool:
        """
        Check if message is for incoming feed values.

        :param message: The message received
        :type message: Message
        :returns: is_feed_values
        :rtype: bool
        """
        is_feed_values = message.topic == self.feed_values_topic
        self.logger.debug(f"{message.topic} is feed values: {is_feed_values}")
        return is_feed_values

    def is_parameters(self, message: Message) -> bool:
        """
        Check if message is for updating device parameters.

        :param message: The message received
        :type message: Message
        :returns: is_parameters
        :rtype: bool
        """
        is_parameters = message.topic == self.parameters_topic
        self.logger.debug(
            f"{message.topic} is parameters message: " f"{is_parameters}"
        )
        return is_parameters

    def is_file_management_message(self, message: Message) -> bool:
        """
        Check if message is any kind of file management related message.

        :param message: The message received
        :type message: Message
        :returns: is_file_management_message
        :rtype: bool
        """
        return any(
            is_message(message)
            for is_message in self.file_management_message_checks
        )

    def is_firmware_message(self, message: Message) -> bool:
        """
        Check if message is any kind of firmware related message.

        :param message: The message received
        :type message: Message
        :returns: is_firmware_message
        :rtype: bool
        """
        return any(
            is_message(message)
            for is_message in self.firmware_update_message_checks
        )

    def is_firmware_install(self, message: Message) -> bool:
        """
        Check if message is firmware update install command.

        :param message: The message received
        :type message: Message
        :returns: firmware_update_install
        :rtype: bool
        """
        firmware_update_install = message.topic == self.firmware_install_topic
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
        firmware_update_abort = message.topic == self.firmware_abort_topic
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
        file_binary = message.topic == self.file_binary_topic
        self.logger.debug(f"{message.topic} is file binary: {file_binary}")
        return file_binary

    def is_file_delete_command(self, message: Message) -> bool:
        """
        Check if message if file delete command.

        :param message: The message received
        :type message: Message
        :returns: file_delete_command
        :rtype: bool
        """
        file_delete_command = message.topic == self.file_delete_topic
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
        file_purge_command = message.topic == self.file_purge_topic
        self.logger.debug(
            f"{message.topic} is file purge: {file_purge_command}"
        )
        return file_purge_command

    def is_file_list(self, message: Message) -> bool:
        """
        Check if message is file list request message.

        :param message: The message received
        :type message: Message
        :returns: file_list
        :rtype: bool
        """
        file_list = message.topic == self.file_list
        self.logger.debug(f"{message.topic} is file list request: {file_list}")
        return file_list

    def is_file_upload_initiate(self, message: Message) -> bool:
        """
        Check if message is file upload command.

        :param message: The message received
        :type message: Message
        :returns: file_upload_initiate
        :rtype: bool
        """
        file_upload_initiate = message.topic == self.file_upload_initiate_topic
        self.logger.debug(
            f"{message.topic} is file upload initiate: {file_upload_initiate}"
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
        file_upload_abort_command = (
            message.topic == self.file_upload_abort_topic
        )
        self.logger.debug(
            f"{message.topic} is file upload abort: {file_upload_abort_command}"
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
        file_url_download_init = message.topic == self.file_url_initiate_topic
        self.logger.debug(
            f"{message.topic} is file URL download: {file_url_download_init}"
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
        file_url_download_abort = message.topic == self.file_url_abort_topic
        self.logger.debug(
            f"{message.topic} is file URL abort: {file_url_download_abort}"
        )
        return file_url_download_abort

    def parse_time_response(self, message: Message) -> int:
        """
        Parse the message into an UTC timestamp.

        :param message: The message received
        :type message: Message
        :returns: timestamp
        :rtype: int
        """
        self.logger.debug(f"{message}")
        payload = json.loads(message.payload.decode("utf-8"))  # type: ignore

        timestamp = payload

        self.logger.debug(f"received timestamp: {timestamp}")
        return timestamp

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
            file_name = payload
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

    def parse_file_delete_command(self, message: Message) -> List[str]:
        """
        Parse the message into a list of file names.

        :param message: The message received
        :type message: Message
        :returns: file_name
        :rtype: List[str]
        """
        self.logger.debug(f"{message}")
        try:
            payload = json.loads(
                message.payload.decode("utf-8")  # type: ignore
            )
            self.logger.debug(f"file names: {payload}")
            return payload
        except Exception:
            self.logger.warning(
                f"Failed to get file name from message {message}"
            )
            return []

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
            return payload
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
        :returns: (name, size, hash)
        :rtype: Tuple[str, int, str]
        """
        self.logger.debug(f"{message}")
        try:
            payload = json.loads(
                message.payload.decode("utf-8")  # type: ignore
            )
            self.logger.debug(
                f'name={payload["name"]}, '
                f'size={payload["size"]}, '
                f'hash={payload["hash"]}'
            )
            return (
                payload["name"],
                payload["size"],
                payload["hash"],
            )
        except Exception:
            self.logger.warning(
                f"Received invalid file upload initiate message: {message}"
            )
            return "", 0, ""

    def parse_parameters(
        self, message: Message
    ) -> Dict[str, Union[bool, int, float, str]]:
        """
        Parse the incoming parameters message.

        :param message: The message received
        :type message: Message
        :returns: parameters
        :rtype: Dict[str, Union[bool, int, float, str]]
        """
        self.logger.debug(f"{message}")
        try:
            parameters = json.loads(message.payload)
            return parameters
        except Exception as e:
            self.logger.exception(f"Failed to parse parameters message: {e}")
            return {}

    def parse_feed_values(
        self, message: Message
    ) -> List[Dict[str, Union[bool, int, float, str]]]:
        """
        Parse the incoming feed values message.

        :param message: The message received
        :type message: Message
        :returns: feed_values
        :rtype: List[Dict[str, Union[bool, int, float, str]]]
        """
        self.logger.debug(f"{message}")
        try:
            feed_values = json.loads(message.payload)
            return feed_values
        except Exception as e:
            self.logger.exception(f"Failed to parse feed values message: {e}")
            return []
