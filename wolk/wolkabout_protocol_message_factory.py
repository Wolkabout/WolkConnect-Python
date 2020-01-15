"""Factory for serializing messages according to WolkAbout Protocol."""
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
import json
from typing import List
from typing import Optional

from wolk import logger_factory
from wolk.interface.message_factory import MessageFactory
from wolk.model.actuator_status import ActuatorStatus
from wolk.model.alarm import Alarm
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.firmware_update_status_type import FirmwareUpdateStatusType
from wolk.model.message import Message
from wolk.model.sensor_reading import SensorReading


class WolkAboutProtocolMessageFactory(MessageFactory):
    """Serialize messages to be sent to WolkAbout IoT Platform."""

    DEVICE_PATH_PREFIX = "d/"
    REFERENCE_PATH_PREFIX = "r/"
    CHANNEL_WILDCARD = "#"
    CHANNEL_DELIMITER = "/"
    SENSOR_READING = "d2p/sensor_reading/"
    ALARM = "d2p/events/"
    ACTUATOR_SET = "p2d/actuator_set/"
    ACTUATOR_GET = "p2d/actuator_get/"
    ACTUATOR_STATUS = "d2p/actuator_status/"
    CONFIGURATION_SET = "p2d/configuration_set/"
    CONFIGURATION_GET = "p2d/configuration_get/"
    CONFIGURATION_STATUS = "d2p/configuration_get/"
    FILE_BINARY_REQUEST = "d2p/file_binary_request/"
    FIRMWARE_VERSION_UPDATE = "d2p/firmware_version_update/"
    FILE_LIST_UPDATE = "d2p/file_list_update/"
    FILE_LIST_RESPONSE = "d2p/file_list_response/"
    FILE_UPLOAD_STATUS = "d2p/file_upload_status/"
    FILE_URL_DOWNLOAD_STATUS = "d2p/file_url_download_status/"

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

    def make_from_sensor_reading(self, reading: SensorReading) -> Message:
        """
        Serialize the sensor reading to be sent to WolkAbout IoT Platform.

        :param reading: Sensor reading to be serialized
        :type reading: SensorReading
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{reading}")

        topic = (
            self.SENSOR_READING
            + self.DEVICE_PATH_PREFIX
            + self.device_key
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + reading.reference
        )

        if isinstance(reading.value, tuple):
            for value in reading.value:
                if isinstance(value, bool):
                    value = str(value).lower()
                if ("\n" in str(value) or '"' in str(value)) and isinstance(
                    value, str
                ):
                    value = value.replace("\n", "\\n")
                    value = value.replace("\r", "")
                    value = value.replace('"', '\\"')
            reading.value = ",".join(map(str, reading.value))

        elif isinstance(reading.value, bool):
            reading.value = str(reading.value).lower()

        elif (
            "\n" in str(reading.value) or '"' in str(reading.value)
        ) and isinstance(reading.value, str):
            reading.value = reading.value.replace("\n", "\\n")
            reading.value = reading.value.replace("\r", "")
            reading.value = reading.value.replace('"', '\\"')

        if reading.timestamp is not None:
            payload = json.dumps(
                {"data": str(reading.value), "utc": int(reading.timestamp)}
            )
        else:
            payload = json.dumps({"data": str(reading.value)})

        message = Message(topic, payload)
        self.logger.debug(f"{message}")

        return message

    def make_from_alarm(self, alarm: Alarm) -> Message:
        """
        Serialize the alarm to be sent to WolkAbout IoT Platform.

        :param alarm: Alarm event to be serialized
        :type alarm: Alarm
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{alarm}")

        topic = (
            self.ALARM
            + self.DEVICE_PATH_PREFIX
            + self.device_key
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + alarm.reference
        )

        active = str(alarm.active).lower()

        if alarm.timestamp is not None:
            payload = json.dumps({"data": active, "utc": int(alarm.timestamp)})
        else:
            payload = json.dumps({"data": active})

        message = Message(topic, payload)
        self.logger.debug(f"{message}")

        return message

    def make_from_actuator_status(self, actuator: ActuatorStatus) -> Message:
        """
        Serialize the actuator status to be sent to WolkAbout IoT Platform.

        :param actuator: Actuator status to be serialized
        :type actuator: ActuatorStatus
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{actuator}")

        topic = (
            self.ACTUATOR_STATUS
            + self.DEVICE_PATH_PREFIX
            + self.device_key
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + actuator.reference
        )

        if isinstance(actuator.value, bool):
            actuator.value = str(actuator.value).lower()

        elif (
            "\n" in str(actuator.value) or '"' in str(actuator.value)
        ) and isinstance(actuator.value, str):
            actuator.value = actuator.value.replace("\n", "\\n")
            actuator.value = actuator.value.replace("\r", "")
            actuator.value = actuator.value.replace('"', '\\"')

        payload = json.dumps(
            {"status": actuator.state.value, "value": str(actuator.value)}
        )

        message = Message(topic, payload)
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
        topic = "d2p/firmware_update_status/d/" + self.device_key
        payload = {}

        if (
            firmware_update_status.status
            == FirmwareUpdateStatusType.INSTALLATION
        ):
            payload["status"] = firmware_update_status.status.value
        elif (
            firmware_update_status.status == FirmwareUpdateStatusType.COMPLETED
        ):
            payload["status"] = firmware_update_status.status.value
        elif firmware_update_status.status == FirmwareUpdateStatusType.ABORTED:
            payload["status"] = firmware_update_status.status.value
        elif (
            firmware_update_status.status == FirmwareUpdateStatusType.ERROR
            and firmware_update_status.error is not None
        ):
            payload["status"] = firmware_update_status.status.value
            payload["error"] = firmware_update_status.error.value

        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")

        return message

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
        self.logger.debug(
            f"file_name: '{file_name}', "
            f"chunk_index: {chunk_index}, "
            f"chunk_size: {chunk_size}"
        )
        topic = (
            self.FILE_BINARY_REQUEST
            + self.DEVICE_PATH_PREFIX
            + self.device_key
        )
        payload = {
            "fileName": file_name,
            "chunkIndex": chunk_index,
            "chunkSize": chunk_size,
        }
        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")

        return message

    def make_from_firmware_version(self, version: str) -> Message:
        """
        Report the current version of firmware to WolkAbout IoT Platform.

        :param version: Firmware version to report
        :type version: str
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"version: {version}")
        topic = (
            self.FIRMWARE_VERSION_UPDATE
            + self.DEVICE_PATH_PREFIX
            + self.device_key
        )
        message = Message(topic, str(version))
        self.logger.debug(f"{message}")

        return message

    def make_from_configuration(self, configuration: dict) -> Message:
        """
        Report device's configuration to WolkAbout IoT Platform.

        :param configuration: Device's current configuration
        :type configuration: dict
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{configuration}")
        topic = (
            self.CONFIGURATION_STATUS
            + self.DEVICE_PATH_PREFIX
            + self.device_key
        )

        for reference, value in configuration.items():

            if isinstance(value, tuple):
                for single_value in value:
                    if isinstance(single_value, bool):
                        single_value = str(single_value).lower()
                        continue
                    if (
                        "\n" in str(single_value) or '"' in str(single_value)
                    ) and isinstance(single_value, str):
                        single_value = single_value.replace("\n", "\\n")
                        single_value = single_value.replace("\r", "")
                        single_value = single_value.replace('"', '\\"')
                configuration[reference] = ",".join(map(str, value))

            elif isinstance(value, bool):
                configuration[reference] = str(value).lower()

            elif ("\n" in str(value) or '"' in str(value)) and isinstance(
                value, str
            ):
                configuration[reference] = value.replace("\n", "\\n")
                configuration[reference] = value.replace("\r", "")
                configuration[reference] = value.replace('"', '\\"')
            else:
                configuration[reference] = str(value)

        message = Message(topic, json.dumps({"values": configuration}))
        self.logger.debug(f"{message}")

        return message

    def make_from_file_list_update(self, file_list: List[str]) -> Message:
        """
        Serialize list of files present on device.

        :param file_list: Files present on device
        :type file_list: List[str]
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{file_list}")
        topic = (
            self.FILE_LIST_UPDATE + self.DEVICE_PATH_PREFIX + self.device_key
        )
        message = Message(
            topic, json.dumps([{"fileName": file} for file in file_list])
        )
        self.logger.debug(f"{message}")

        return message

    def make_from_file_list_request(self, file_list: List[str]) -> Message:
        """
        Serialize list of files present on device.

        :param file_list: Files present on device
        :type file_list: List[str]
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{file_list}")
        topic = (
            self.FILE_LIST_RESPONSE + self.DEVICE_PATH_PREFIX + self.device_key
        )
        message = Message(
            topic, json.dumps([{"fileName": file} for file in file_list])
        )
        self.logger.debug(f"{message}")

        return message

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
        self.logger.debug(f" status: {status}, file_name: {file_name}")
        topic = (
            self.FILE_UPLOAD_STATUS + self.DEVICE_PATH_PREFIX + self.device_key
        )
        payload = {"fileName": file_name}

        if status.status == FileManagementStatusType.FILE_TRANSFER:
            payload["status"] = status.status.value
        elif status.status == FileManagementStatusType.FILE_READY:
            payload["status"] = status.status.value
        elif status.status == FileManagementStatusType.ABORTED:
            payload["status"] = status.status.value
        elif (
            status.status == FileManagementStatusType.ERROR
            and status.error is not None
        ):
            payload["status"] = status.status.value
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
        topic = (
            self.FILE_URL_DOWNLOAD_STATUS
            + self.DEVICE_PATH_PREFIX
            + self.device_key
        )
        payload = {"fileUrl": file_url}

        if status.status.value == "FILE_TRANSFER":
            payload["status"] = status.status.value
        elif status.status.value == "FILE_READY" and file_name is not None:
            payload["status"] = status.status.value
            payload["fileName"] = file_name
        elif status.status.value == "ABORTED":
            payload["status"] = status.status.value
        elif status.status.value == "ERROR" and status.error is not None:
            payload["status"] = status.status.value
            payload["error"] = status.error.value

        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")

        return message
