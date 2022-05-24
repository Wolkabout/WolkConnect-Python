"""Factory for serializing messages according to WolkAbout Protocol."""
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
from time import time
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from wolk import logger_factory
from wolk.interface.message_factory import MessageFactory
from wolk.model.data_type import DataType
from wolk.model.feed_type import FeedType
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.firmware_update_status_type import FirmwareUpdateStatusType
from wolk.model.message import Message
from wolk.model.unit import Unit

OutgoingDataTypes = Union[bool, int, float, str]
Reading = Tuple[str, OutgoingDataTypes]


class WolkAboutProtocolMessageFactory(MessageFactory):
    """Serialize messages to be sent to WolkAbout IoT Platform."""

    DEVICE_TO_PLATFORM = "d2p/"
    CHANNEL_DELIMITER = "/"

    TIME = "time"

    PARAMETERS = "parameters"
    PULL_PARAMETERS = "pull_parameters"

    FEED_VALUES = "feed_values"
    PULL_FEED_VALUES = "pull_feed_values"

    FEED_REGISTRATION = "feed_registration"
    FEED_REMOVAL = "feed_removal"

    ATTRIBUTE_REGISTRATION = "attribute_registration"

    FILE_BINARY_REQUEST = "file_binary_request"
    FILE_LIST = "file_list"
    FILE_UPLOAD_STATUS = "file_upload_status"
    FILE_URL_DOWNLOAD_STATUS = "file_url_download_status"

    FIRMWARE_VERSION_UPDATE = "firmware_version_update"
    FIRMWARE_UPDATE_STATUS = "firmware_update_status"

    def __init__(self, device_key: str) -> None:
        """
        Create a factory for serializing messages.

        :param device_key: Device key to use when serializing messages
        :type device_key: str
        """
        self.device_key = device_key
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(f"Device key: {device_key}")
        self.common_topic = (
            self.DEVICE_TO_PLATFORM + self.device_key + self.CHANNEL_DELIMITER
        )

    def make_from_feed_value(
        self,
        reading: Union[Reading, List[Reading]],
        timestamp: Optional[int],
    ) -> Message:
        """
        Serialize feed value data.

        :param reading: Feed value data as (reference, value) or list of tuple
        :type reading: Union[Reading, List[Reading]]
        :param timestamp: Unix timestamp in ms. Default to current time if None
        :raises ValueError: Reading is invalid data type
        :returns: message
        :rtype: Message
        """
        topic = self.common_topic + self.FEED_VALUES

        if isinstance(reading, tuple):
            reference, value = reading
            feed_value = {reference: value}
        elif isinstance(reading, list):
            feed_value = dict(reading)
        else:
            raise ValueError(
                f"Expected reading as tuple or list, got {type(reading)}"
            )

        feed_value["timestamp"] = (
            timestamp if timestamp is not None else round(time() * 1000)
        )
        payload = [feed_value]

        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")

        return message

    def make_time_request(self) -> Message:
        """
        Serialize message requesting platform timestamp.

        :returns: message
        :rtype: Message
        """
        topic = self.common_topic + self.TIME

        message = Message(topic)
        self.logger.debug(f"{message}")

        return message

    def make_pull_feed_values(self) -> Message:
        """
        Serialize message requesting any pending inbound feed values.

        :returns: message
        :rtype: Message
        """
        topic = self.common_topic + self.PULL_FEED_VALUES

        message = Message(topic)
        self.logger.debug(f"{message}")

        return message

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
        topic = self.common_topic + self.PARAMETERS

        message = Message(topic, json.dumps(parameters))
        self.logger.debug(f"{message}")

        return message

    def make_pull_parameters(self) -> Message:
        """
        Serialize request to pull device parameters from the Platform.

        :returns: message
        :rtype: Message
        """
        topic = self.common_topic + self.PULL_PARAMETERS

        message = Message(topic)
        self.logger.debug(f"{message}")

        return message

    def make_feed_registration(
        self,
        name: str,
        reference: str,
        feed_type: FeedType,
        unit: Union[Unit, str],
    ) -> Message:
        """
        Serialize request to register a feed on the Platform.

        :param name: Feed name
        :type name: str
        :param reference: Unique identifier
        :type reference: str
        :param feed_type: Is the feed one or two-way communication
        :type feed_type: FeedType
        :param unit: Unit used to measure this feed
        :type unit: Union[Unit, str]
        :returns: message
        :rtype: Message
        """
        topic = self.common_topic + self.FEED_REGISTRATION

        payload = {
            "name": name,
            "reference": reference,
            "type": feed_type.value,
        }

        if isinstance(unit, Unit):
            payload["unitGuid"] = unit.value
        else:
            payload["unitGuid"] = unit

        message = Message(topic, json.dumps([payload]))
        self.logger.debug(f"{message}")

        return message

    def make_feed_removal(self, reference: str) -> Message:
        """
        Serialize request to remove a feed from the device on the Platform.

        :param reference: Unique identifier
        :type reference: str
        :returns: message
        :rtype: Message
        """
        topic = self.common_topic + self.FEED_REMOVAL

        payload = json.dumps([reference])

        message = Message(topic, payload)
        self.logger.debug(f"{message}")

        return message

    def make_attribute_registration(
        self, name: str, data_type: DataType, value: str
    ) -> Message:
        """
        Serialize request to register an attribute for the device.

        :param name: Unique identifier
        :type name: str
        :param data_type: Type of data this attribute holds
        :type data_type: DataType
        :param value: Value of the attribute
        :type value: str
        :returns: message
        :rtype: Message
        """
        topic = self.common_topic + self.ATTRIBUTE_REGISTRATION

        payload = [{"name": name, "dataType": data_type.value, "value": value}]

        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")

        return message

    def make_from_package_request(
        self, file_name: str, chunk_index: int
    ) -> Message:
        """
        Request a package of the file from WolkAbout IoT Platform.

        :param file_name: Name of the file that contains the requested package
        :type file_name: str
        :param chunk_index: Index of the requested package
        :type chunk_index: int
        :returns: message
        :rtype: Message
        """
        self.logger.debug(
            f"file_name: '{file_name}', " f"chunk_index: {chunk_index}, "
        )
        topic = self.common_topic + self.FILE_BINARY_REQUEST

        payload = {
            "name": file_name,
            "chunkIndex": chunk_index,
        }
        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")

        return message

    def make_from_file_list(
        self, file_list: List[Dict[str, Union[str, int]]]
    ) -> Message:
        """
        Serialize list of files present on device.

        :param file_list: Files present on device
        :type file_list: List[Dict[str, Union[str, int]]]
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{file_list}")
        topic = self.common_topic + self.FILE_LIST

        message = Message(topic, json.dumps(file_list))
        self.logger.debug(f"{message}")

        return message

    def make_from_file_management_status(
        self, status: FileManagementStatus, file_name: str
    ) -> Message:
        """
        Serialize device's current file management status.

        :param status: Current file management status
        :type status: FileManagementStatus
        :param file_name: Name of file being transferred
        :type file_name: str
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f" status: {status}, file_name: {file_name}")
        topic = self.common_topic + self.FILE_UPLOAD_STATUS

        payload = {"name": file_name, "status": status.status.value}
        if (
            status.status == FileManagementStatusType.ERROR
            and status.error is not None
        ):
            payload["error"] = status.error.value

        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")

        return message

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
        self.logger.debug(
            f"file_url: {file_url}, status: {status}, file_name: {file_name}"
        )
        topic = self.common_topic + self.FILE_URL_DOWNLOAD_STATUS

        payload = {"fileUrl": file_url, "status": status.status.value}

        if (
            status.status == FileManagementStatusType.ERROR
            and status.error is not None
        ):
            payload["error"] = status.error.value

        if file_name is not None:
            payload["fileName"] = file_name

        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")

        return message

    def make_from_firmware_update_status(
        self, firmware_update_status: FirmwareUpdateStatus
    ) -> Message:
        """
        Serialize firmware update status to be sent to WolkAbout IoT Platform.

        :param firmware_update_status: Firmware update status to be serialized
        :type firmware_status: FirmwareUpdateStatus
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{firmware_update_status}")
        topic = self.common_topic + self.FIRMWARE_UPDATE_STATUS
        payload = {"status": firmware_update_status.status.value}

        if (
            firmware_update_status.status == FirmwareUpdateStatusType.ERROR
            and firmware_update_status.error is not None
        ):
            payload["error"] = firmware_update_status.error.value

        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")

        return message
