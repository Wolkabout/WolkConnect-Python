"""Factory for serializing messages according to JSON_PROTOCOL."""
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
from typing import List, Optional

from wolk.model.alarm import Alarm
from wolk.model.actuator_state import ActuatorState
from wolk.model.actuator_status import ActuatorStatus
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.message import Message
from wolk.model.sensor_reading import SensorReading
from wolk.interface.message_factory import MessageFactory
from wolk import logger_factory


class JSONProtocolMessageFactory(MessageFactory):
    """
    Serialize messages to be sent to WolkAbout IoT Platform.

    :ivar device_key: Device key to use when serializing messages
    :vartype device_key: str
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    """

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

        if isinstance(reading.value, tuple):

            delimiter = ","

            values_list = list()

            for value in reading.value:
                if value is True:
                    value = "true"
                elif value is False:
                    value = "false"
                if "\n" in str(value):
                    value = value.replace("\n", "\\n")
                    value = value.replace("\r", "")
                if '"' in str(value):
                    value = value.replace('"', '\\"')
                values_list.append(value)
                values_list.append(delimiter)

            values_list.pop()

            reading.value = "".join(map(str, values_list))

        if reading.value is True:
            reading.value = "true"
        elif reading.value is False:
            reading.value = "false"

        if "\n" in str(reading.value):
            reading.value = reading.value.replace("\n", "\\n")
            reading.value = reading.value.replace("\r", "")
        if '"' in str(reading.value):
            reading.value = reading.value.replace('"', '\\"')

        if reading.timestamp is None:
            message = Message(
                "d2p/sensor_reading/d/"
                + self.device_key
                + "/r/"
                + reading.reference,
                '{"data":"' + str(reading.value) + '"}',
            )
        else:
            message = Message(
                "d2p/sensor_reading/d/"
                + self.device_key
                + "/r/"
                + reading.reference,
                '{"utc":"'
                + str(reading.timestamp)
                + '","data":"'
                + str(reading.value)
                + '"}',
            )

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

        if alarm.active is True:
            alarm.active = "ON"
        elif alarm.active is False:
            alarm.active = "OFF"

        if alarm.timestamp is None:
            message = Message(
                "d2p/events/d/" + self.device_key + "/r/" + alarm.reference,
                '{"data":"' + str(alarm.active) + '"}',
            )

        else:
            message = Message(
                "d2p/events/d/" + self.device_key + "/r/" + alarm.reference,
                '{"utc":"'
                + str(alarm.timestamp)
                + '","data":"'
                + str(alarm.active)
                + '"}',
            )
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
        if actuator.state == ActuatorState.READY:
            actuator.state = "READY"

        elif actuator.state == ActuatorState.BUSY:
            actuator.state = "BUSY"

        elif actuator.state == ActuatorState.ERROR:
            actuator.state = "ERROR"

        if actuator.value is True:
            actuator.value = "true"
        elif actuator.value is False:
            actuator.value = "false"

        if "\n" in str(actuator.value):
            actuator.value = actuator.value.replace("\n", "\\n")
            actuator.value = actuator.value.replace("\r", "")
        if '"' in str(actuator.value):
            actuator.value = actuator.value.replace('"', '\\"')

        message = Message(
            "d2p/actuator_status/d/"
            + self.device_key
            + "/r/"
            + actuator.reference,
            '{"status":"'
            + actuator.state
            + '","value":"'
            + str(actuator.value)
            + '"}',
        )
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

        if firmware_update_status.status.value == "INSTALLATION":
            payload["status"] = firmware_update_status.status.value
        elif firmware_update_status.status.value == "COMPLETED":
            payload["status"] = firmware_update_status.status.value
        elif firmware_update_status.status.value == "ABORTED":
            payload["status"] = firmware_update_status.status.value
        elif firmware_update_status.status.value == "ERROR":
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
        topic = "d2p/file_binary_request/d/" + self.device_key
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
        message = Message(
            "d2p/firmware_version_update/d/" + self.device_key, str(version)
        )
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
        values = str()

        for reference, value in configuration.items():

            if isinstance(value, tuple):

                delimiter = ","

                values_list = list()

                for single_value in value:
                    if single_value is True:
                        single_value = "true"
                    elif single_value is False:
                        single_value = "false"
                    if "\n" in str(single_value):
                        single_value = single_value.replace("\n", "\\n")
                        single_value = single_value.replace("\r", "")
                    values_list.append(single_value)
                    values_list.append(delimiter)

                values_list.pop()
                value = "".join(map(str, values_list))

            if value is True:
                value = "true"
            elif value is False:
                value = "false"

            if "\n" in str(value):
                value = value.replace("\n", "\\n")
                value = value.replace("\r", "")

            values += '"' + reference + '":"' + str(value) + '",'

        values = values[:-1]

        message = Message(
            "d2p/configuration_get/d/" + self.device_key,
            '{"values":{' + values + "}}",
        )
        self.logger.debug(f"{message}")
        return message

    def make_from_file_list_update(self, file_list: List[str]) -> Message:
        """Serialize list of files present on device.

        :param file_list: Files present on device
        :type file_list: List[str]
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{file_list}")
        payload = "{" + str([{"fileName": file} for file in file_list]) + "}"
        topic = "d2p/file_list_update/d/" + self.device_key
        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")
        return message

    def make_from_file_list_request(self, file_list: List[str]) -> Message:
        """Serialize list of files present on device.

        :param file_list: Files present on device
        :type file_list: List[str]
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"{file_list}")
        payload = "{" + str([{"fileName": file} for file in file_list]) + "}"
        topic = "d2p/file_list_response/d/" + self.device_key
        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")
        return message

    def make_from_file_management_status(
        self, file_name: str, status: FileManagementStatus
    ) -> Message:
        """Serialize device's current file management status.

        :param file_name: Name of file being transfered
        :type file_name: str
        :param status: Current file management status
        :type status: FileManagementStatus
        :returns: message
        :rtype: Message
        """
        self.logger.debug(f"file_name: {file_name}, status: {status}")
        topic = "d2p/file_upload_status/d/" + self.device_key
        payload = {"fileName": file_name}

        if status.status.value == "FILE_TRANSFER":
            payload["status"] = status.status.value
        elif status.status.value == "FILE_READY":
            payload["status"] = status.status.value
        elif status.status.value == "ABORTED":
            payload["status"] = status.status.value
        elif status.status.value == "ERROR":
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
        """Serialize device's current file URL download status.

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
        topic = "d2p/file_url_download_status/d/" + self.device_key
        payload = {"fileUrl": file_url}

        if status.status.value == "FILE_TRANSFER":
            payload["status"] = status.status.value
        elif status.status.value == "FILE_READY":
            payload["status"] = status.status.value
            payload["fileName"] = file_name
        elif status.status.value == "ABORTED":
            payload["status"] = status.status.value
        elif status.status.value == "ERROR":
            payload["status"] = status.status.value
            payload["error"] = status.error.value

        message = Message(topic, json.dumps(payload))
        self.logger.debug(f"{message}")
        return message
