"""Process messages received from WolkAbout IoT Platform."""
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
from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from wolk.model.file_transfer_package import FileTransferPackage
from wolk.model.message import Message


class MessageDeserializer(ABC):
    """Deserialize messages received from the platform."""

    @abstractmethod
    def get_inbound_topics(self) -> List[str]:
        """
        Return list of inbound topics for device.

        :returns: List of topics to subscribe to
        :rtype: List[str]
        """
        raise NotImplementedError()

    @abstractmethod
    def is_time_response(self, message: Message) -> bool:
        """
        Check if message is response to time request.

        :param message: The message received
        :type message: Message
        :returns: is_time_response
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_file_management_message(self, message: Message) -> bool:
        """
        Check if message is any kind of file management related message.

        :param message: The message received
        :type message: Message
        :returns: is_file_management_message
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_firmware_message(self, message: Message) -> bool:
        """
        Check if message is any kind of firmware related message.

        :param message: The message received
        :type message: Message
        :returns: is_firmware_message
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_feed_values(self, message: Message) -> bool:
        """
        Check if message is for incoming feed values.

        :param message: The message received
        :type message: Message
        :returns: is_feed_values
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_parameters(self, message: Message) -> bool:
        """
        Check if message is for updating device parameters.

        :param message: The message received
        :type message: Message
        :returns: is_parameters
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_firmware_install(self, message: Message) -> bool:
        """
        Check if message is firmware update install command.

        :param message: The message received
        :type message: Message
        :returns: firmware_update_install_command
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_firmware_abort(self, message: Message) -> bool:
        """
        Check if message is firmware update command.

        :param message: The message received
        :type message: Message
        :returns: firmware_update_abort_command
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_file_binary_response(self, message: Message) -> bool:
        """
        Check if message is file binary message.

        :param message: The message received
        :type message: Message
        :returns: file_binary_response
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_file_delete_command(self, message: Message) -> bool:
        """
        Check if message if file delete command.

        :param message: The message received
        :type message: Message
        :returns: file_delete_command
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_file_purge_command(self, message: Message) -> bool:
        """
        Check if message if file purge command.

        :param message: The message received
        :type message: Message
        :returns: file_purge_command
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_file_list(self, message: Message) -> bool:
        """
        Check if message is file list request message.

        :param message: The message received
        :type message: Message
        :returns: file_list
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_file_upload_initiate(self, message: Message) -> bool:
        """
        Check if message is file upload command.

        :param message: The message received
        :type message: Message
        :returns: file_upload_initiate_command
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_file_upload_abort(self, message: Message) -> bool:
        """
        Check if message is file upload command.

        :param message: The message received
        :type message: Message
        :returns: file_upload_abort_command
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_file_url_initiate(self, message: Message) -> bool:
        """
        Check if message is file URL download command.

        :param message: The message received
        :type message: Message
        :returns: file_url_download_initiate
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_file_url_abort(self, message: Message) -> bool:
        """
        Check if message is file URL download command.

        :param message: The message received
        :type message: Message
        :returns: file_url_download_abort
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def parse_time_response(self, message: Message) -> int:
        """
        Parse the message into an UTC timestamp.

        :param message: The message received
        :type message: Message
        :returns: timestamp
        :rtype: int
        """
        raise NotImplementedError()

    @abstractmethod
    def parse_firmware_install(self, message: Message) -> str:
        """
        Return file name from message.

        :param message: The message received
        :type message: Message
        :returns: file_name
        :rtype: str
        """
        raise NotImplementedError()

    @abstractmethod
    def parse_file_initiate(self, message: Message) -> Tuple[str, int, str]:
        """
        Return file name, file size and file hash from message.

        :param message: The message received
        :type message: Message
        :returns: (file_name, file_size, file_hash)
        :rtype: Tuple[str, int, str]
        """
        raise NotImplementedError()

    @abstractmethod
    def parse_file_url(self, message: Message) -> str:
        """
        Parse the message into a URL string.

        :param message: The message received
        :type message: Message
        :returns file_url:
        :rtype: str
        """
        raise NotImplementedError()

    @abstractmethod
    def parse_file_binary(self, message: Message) -> FileTransferPackage:
        """
        Parse the message into a file transfer package.

        :param message: The message received
        :type message: Message
        :returns: file_transfer_package
        :rtype: FileTransferPackage
        """
        raise NotImplementedError()

    @abstractmethod
    def parse_file_delete_command(self, message: Message) -> List[str]:
        """
        Parse the message into a list of file names.

        :param message: The message received
        :type message: Message
        :returns: file_name
        :rtype: List[str]
        """
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()
