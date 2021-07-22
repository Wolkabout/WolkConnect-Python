"""Create messages from data that conform to device's specified protocol."""
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
from typing import Optional
from typing import Union

from wolk.model.file_management_status import FileManagementStatus
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.message import Message


class MessageFactory(ABC):
    """Serialize messages to be sent to WolkAbout IoT Platform."""

    @abstractmethod
    def make_from_feed_value(
        self,
        reference: str,
        value: Union[bool, int, float, str],
        timestamp: Optional[int],
    ) -> Message:
        """
        Serialize feed value data.

        :param reference: Feed identifier
        :type reference: str
        :param value: Value of the feed
        :type value: Union[bool, int, float, str]
        :param timestamp: Unix timestamp. Will assign current time if None
        :returns: message
        :rtype: Message
        """
        raise NotImplementedError()

    @abstractmethod
    def make_pull_feed_values(self) -> Message:
        """
        Serialize message requesting any pending inbound feed values.

        :returns: message
        :rtype: Message
        """
        raise NotImplementedError()

    @abstractmethod
    def make_from_parameters(
        self, parameters: Dict[str, Union[bool, int, float, str]]
    ) -> Message:
        """
        Serialize device parameters to be sent to the Platform.

        :param parameters: Device parameters
        :type parameters: Dict[str, Union[bool, int, float, str]]
        :returns: message
        :rtype: Message
        """
        raise NotImplementedError()

    @abstractmethod
    def make_pull_parameters(self) -> Message:
        """
        Serialize request to pull device parameters from the Platform.

        :returns: message
        :rtype: Message
        """
        raise NotImplementedError()

    @abstractmethod
    def make_from_firmware_update_status(
        self, firmware_update_status: FirmwareUpdateStatus
    ) -> Message:
        """
        Report the current status of the firmware update process.

        :param firmware_update_status: Status of the firmware update process
        :type firmware_update_status: FirmwareUpdateStatus
        :returns: message
        :rtype: Message
        """
        raise NotImplementedError()

    @abstractmethod
    def make_from_package_request(
        self, file_name: str, chunk_index: int, chunk_size: int
    ) -> Message:
        """
        Request a package of the file from WolkAbout IoT Platform.

        :param file_name: Name of the file that contains the requested package
        :type file_name: str
        :param chunk_index: Index of the requested package
        :type chunk_index: int
        :param chunk_size: Size of the requested package
        :type chunk_size: int
        :returns: message
        :rtype: Message
        """
        raise NotImplementedError()

    @abstractmethod
    def make_from_firmware_version_update(self, version: str) -> Message:
        """
        Report the device's current firmware version to WolkAbout IoT Platform.

        :param version: Current device firmware version
        :type version: str
        :returns: message
        :rtype: Message
        """
        raise NotImplementedError()

    @abstractmethod
    def make_from_file_list_update(self, file_list: List[str]) -> Message:
        """
        Serialize list of files present on device.

        :param file_list: Files present on device
        :type file_list: List[str]
        :returns: message
        :rtype: Message
        """
        raise NotImplementedError()

    @abstractmethod
    def make_from_file_list_request(self, file_list: List[str]) -> Message:
        """
        Serialize list of files present on device.

        :param file_list: Files present on device
        :type file_list: List[str]
        :returns: message
        :rtype: Message
        """
        raise NotImplementedError()

    @abstractmethod
    def make_from_file_management_status(
        self, status: FileManagementStatus, file_name: str
    ) -> Message:
        """
        Serialize device's current file management status.

        :param status: Current file management status
        :type status: FileManagementStatus
        :param file_name: Name of file being transfered
        :type file_name: str
        :returns: message
        :rtype: Message
        """

    @abstractmethod
    def make_from_file_url_status(
        self,
        file_url: str,
        status: FileManagementStatus,
        file_name: Optional[str] = None,
    ) -> Message:
        """
        Serialize device's current file URL download status.

        :param file_url: URL from where the file is to be downloaded
        :type file_url: str
        :param status: Current file management status
        :type status: FileManagementStatus
        :param file_name: Only present when download of file is completed
        :type file_name: Optional[str]
        """
        raise NotImplementedError()
