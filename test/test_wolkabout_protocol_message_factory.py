"""Tests for WolkAboutProtocolMessageFactory."""
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
import sys
import time
import unittest

sys.path.append("..")  # noqa

from wolk.model.actuator_state import ActuatorState
from wolk.model.actuator_status import ActuatorStatus
from wolk.model.alarm import Alarm
from wolk.model.message import Message
from wolk.model.sensor_reading import SensorReading
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_error_type import FileManagementErrorType
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.firmware_update_status_type import FirmwareUpdateStatusType
from wolk.model.firmware_update_error_type import FirmwareUpdateErrorType
from wolk.wolkabout_protocol_message_factory import (
    WolkAboutProtocolMessageFactory as WAPMF,
)


class WolkAboutProtocolMessageFactoryTests(unittest.TestCase):
    """Tests for serializing messages using WolkAbout Protocol."""

    def test_init(self):
        """Test that object is created with correct device key."""
        device_key = "some_key"

        factory = WAPMF(device_key)

        self.assertEqual(device_key, factory.device_key)

    def test_sensor_bool(self):
        """Test that valid message is created for bool sensor reading."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "B"
        value = False
        expected_value = str(value).lower()

        expected_topic = (
            WAPMF.SENSOR_READING
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps({"data": expected_value})
        expected_message = Message(expected_topic, expected_payload)

        reading = SensorReading(reference, value)

        serialized_message = factory.make_from_sensor_reading(reading)

        self.assertEqual(expected_message, serialized_message)

    def test_sensor_string_with_newline(self):
        """Test valid message for string with newline sensor reading."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "SNL"
        value = "string\nin\na\ncouple\nof\nrows"
        expected_value = value  # escaped in json.dumps

        expected_topic = (
            WAPMF.SENSOR_READING
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps({"data": expected_value})
        expected_message = Message(expected_topic, expected_payload)

        reading = SensorReading(reference, value)

        serialized_message = factory.make_from_sensor_reading(reading)

        self.assertEqual(expected_message, serialized_message)

    def test_sensor_with_timestamp(self):
        """Test valid messagefor sensor reading with timestamp."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "TS"
        value = "value"
        timestamp = int(round(time.time() * 1000))

        reading = SensorReading(reference, value, timestamp)

        serialized_message = factory.make_from_sensor_reading(reading)

        self.assertIn("utc", json.loads(serialized_message.payload))

    def test_sensor_multi_value_float(self):
        """Test valid message for multi-value float sensor reading."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "MVF"
        value = (12.3, 45.6)
        expected_value = ",".join(map(str, value))

        expected_topic = (
            WAPMF.SENSOR_READING
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps({"data": expected_value})
        expected_message = Message(expected_topic, expected_payload)

        reading = SensorReading(reference, value)

        serialized_message = factory.make_from_sensor_reading(reading)

        self.assertEqual(expected_message, serialized_message)

    def test_sensor_multi_value_string(self):
        """Test valid message for multi-value string sensor reading."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "MVS"
        value = ("string1", "string2")
        expected_value = ",".join(value)

        expected_topic = (
            WAPMF.SENSOR_READING
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps({"data": expected_value})
        expected_message = Message(expected_topic, expected_payload)

        reading = SensorReading(reference, value)

        serialized_message = factory.make_from_sensor_reading(reading)

        self.assertEqual(expected_message, serialized_message)

    def test_sensor_multi_value_string_with_newline(self):
        """Test message for multi-value string with newline sensor reading."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "MVSNL"
        value = ("string1\nstring1", "string2")
        expected_value = ",".join(value)  # new line escaped in json dumps

        expected_topic = (
            WAPMF.SENSOR_READING
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps({"data": expected_value})
        expected_message = Message(expected_topic, expected_payload)

        reading = SensorReading(reference, value)

        serialized_message = factory.make_from_sensor_reading(reading)

        self.assertEqual(expected_message, serialized_message)

    def test_alarm_no_timestamp(self):
        """Test message for alarm without timestamp."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = False
        expected_value = value

        expected_topic = (
            WAPMF.ALARM
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps({"active": expected_value})
        expected_message = Message(expected_topic, expected_payload)

        alarm = Alarm(reference, value)

        serialized_message = factory.make_from_alarm(alarm)

        self.assertEqual(expected_message, serialized_message)

    def test_alarm_with_code(self):
        """Test message for alarm with code."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = True
        code = "E404"
        expected_value = value

        expected_topic = (
            WAPMF.ALARM
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps({"active": expected_value, "code": code})
        expected_message = Message(expected_topic, expected_payload)

        alarm = Alarm(reference, value, code)

        serialized_message = factory.make_from_alarm(alarm)

        self.assertEqual(expected_message, serialized_message)

    def test_alarm_with_timestamp(self):
        """Test message for alarm with timestamp."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = True
        expected_value = value
        timestamp = int(round(time.time() * 1000))

        expected_topic = (
            WAPMF.ALARM
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps(
            {"active": expected_value, "utc": timestamp}
        )
        expected_message = Message(expected_topic, expected_payload)

        alarm = Alarm(reference, value, timestamp=timestamp)

        serialized_message = factory.make_from_alarm(alarm)

        self.assertEqual(expected_message, serialized_message)

    def test_alarm_with_timestamp_and_code(self):
        """Test message for alarm with timestamp and code."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = True
        code = "E404"
        expected_value = value
        timestamp = int(round(time.time() * 1000))

        expected_topic = (
            WAPMF.ALARM
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps(
            {"active": expected_value, "code": code, "utc": timestamp}
        )
        expected_message = Message(expected_topic, expected_payload)

        alarm = Alarm(reference, value, code, timestamp)

        serialized_message = factory.make_from_alarm(alarm)

        self.assertEqual(expected_message, serialized_message)

    def test_actuator_bool(self):
        """Test message for bool actuator with ready state."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = True
        status = ActuatorState.READY
        expected_value = str(value).lower()

        expected_topic = (
            WAPMF.ACTUATOR_STATUS
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps(
            {"status": status.value, "value": expected_value}
        )
        expected_message = Message(expected_topic, expected_payload)

        actuator = ActuatorStatus(reference, status, value)

        serialized_message = factory.make_from_actuator_status(actuator)

        self.assertEqual(expected_message, serialized_message)

    def test_actuator_float(self):
        """Test message for float actuator with ready state."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = 12.3
        status = ActuatorState.READY
        expected_value = str(value)

        expected_topic = (
            WAPMF.ACTUATOR_STATUS
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps(
            {"status": status.value, "value": expected_value}
        )
        expected_message = Message(expected_topic, expected_payload)

        actuator = ActuatorStatus(reference, status, value)

        serialized_message = factory.make_from_actuator_status(actuator)

        self.assertEqual(expected_message, serialized_message)

    def test_actuator_string_with_newline(self):
        """Test message for string with newline actuator with ready state."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = "string\nstring"
        status = ActuatorState.READY
        expected_value = value  # escaped in json.dumps

        expected_topic = (
            WAPMF.ACTUATOR_STATUS
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps(
            {"status": status.value, "value": expected_value}
        )
        expected_message = Message(expected_topic, expected_payload)

        actuator = ActuatorStatus(reference, status, value)

        serialized_message = factory.make_from_actuator_status(actuator)

        self.assertEqual(expected_message, serialized_message)

    def test_actuator_error_with_value_none(self):
        """Test message for actuator with error state and no value."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = None
        status = ActuatorState.ERROR

        actuator = ActuatorStatus(reference, status, value)

        serialized_message = factory.make_from_actuator_status(actuator)

        self.assertNotIn("value", json.loads(serialized_message.payload))

    def test_actuator_with_timestamp(self):
        """Test message for actuator with error state and no value."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = "true"
        status = ActuatorState.READY
        timestamp = int(round(time.time() * 1000))

        actuator = ActuatorStatus(reference, status, value, timestamp)

        expected_topic = (
            WAPMF.ACTUATOR_STATUS
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
            + WAPMF.CHANNEL_DELIMITER
            + WAPMF.REFERENCE_PATH_PREFIX
            + reference
        )
        expected_payload = json.dumps(
            {"status": status.value, "value": value, "utc": timestamp}
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_from_actuator_status(actuator)
        self.assertEqual(expected_message, serialized_message)

    def test_actuator_error_without_timestamp(self):
        """Test message for actuator status with no timestamp."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "A"
        value = None
        status = ActuatorState.ERROR

        actuator = ActuatorStatus(reference, status, value)

        serialized_message = factory.make_from_actuator_status(actuator)

        self.assertNotIn("utc", json.loads(serialized_message.payload))

    def test_configuration_bool(self):
        """Test message for configuration bool."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "B"
        value = True
        configuration = {reference: value}
        expected_value = str(value).lower()

        expected_topic = (
            WAPMF.CONFIGURATION_STATUS + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps({"values": {reference: expected_value}})
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = factory.make_from_configuration(configuration)

        self.assertEqual(expected_message, serialized_message)

    def test_configuration_float(self):
        """Test message for configuration float."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "F"
        value = 12.3
        configuration = {reference: value}
        expected_value = str(value)

        expected_topic = (
            WAPMF.CONFIGURATION_STATUS + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps({"values": {reference: expected_value}})
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = factory.make_from_configuration(configuration)

        self.assertEqual(expected_message, serialized_message)

    def test_configuration_string_with_newline(self):
        """Test message for configuration string with newline."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "SNL"
        value = "string\nstring"
        configuration = {reference: value}
        expected_value = value  # escaped in json.dumps

        expected_topic = (
            WAPMF.CONFIGURATION_STATUS + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps({"values": {reference: expected_value}})
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = factory.make_from_configuration(configuration)

        self.assertEqual(expected_message, serialized_message)

    def test_configuration_multi_value_float(self):
        """Test message for configuration multi value float."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "F"
        value = (12.3, 45.6)
        configuration = {reference: value}
        expected_value = ",".join(map(str, value))

        expected_topic = (
            WAPMF.CONFIGURATION_STATUS + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps({"values": {reference: expected_value}})
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = factory.make_from_configuration(configuration)

        self.assertEqual(expected_message, serialized_message)

    def test_configuration_multi_value_string_with_newline(self):
        """Test message for configuration multi value string with newline."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "F"
        value = ("string1\nstring1", "string2", "string3\nstring3")
        configuration = {reference: value}
        expected_value = ",".join(map(str, value))  # escaped in json.dumps

        expected_topic = (
            WAPMF.CONFIGURATION_STATUS + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps({"values": {reference: expected_value}})
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = factory.make_from_configuration(configuration)

        self.assertEqual(expected_message, serialized_message)

    def test_file_list_update(self):
        """Test message for file list update."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        file_list = ["file1.txt", "file2.bin", "file3 with spaces.jpg"]

        expected_topic = (
            WAPMF.FILE_LIST_UPDATE + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps(
            [{"fileName": file} for file in file_list]
        )
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = factory.make_from_file_list_update(file_list)

        self.assertEqual(expected_message, serialized_message)

    def test_file_list_request(self):
        """Test message for file list request."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        file_list = ["file1.txt", "file2.bin", "file3 with spaces.jpg"]

        expected_topic = (
            WAPMF.FILE_LIST_RESPONSE + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps(
            [{"fileName": file} for file in file_list]
        )
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = factory.make_from_file_list_request(file_list)

        self.assertEqual(expected_message, serialized_message)

    def test_file_package_request(self):
        """Test message file package request."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        file_name = "file_name"
        chunk_index = 0
        chunk_size = 256

        expected_topic = (
            WAPMF.FILE_BINARY_REQUEST + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps(
            {
                "fileName": file_name,
                "chunkIndex": chunk_index,
                "chunkSize": chunk_size,
            }
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_from_package_request(
            file_name, chunk_index, chunk_size
        )

        self.assertEqual(expected_message, serialized_message)

    def test_file_status_ready(self):
        """Test message for file management status with file ready."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        file_name = "file_name"
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        expected_topic = (
            WAPMF.FILE_UPLOAD_STATUS + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps(
            {"fileName": file_name, "status": status.status.value}
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_from_file_management_status(
            status, file_name
        )

        self.assertEqual(expected_message, serialized_message)

    def test_file_status_error(self):
        """Test message for file management status with error status."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        file_name = "file_name"
        status = FileManagementStatus(
            FileManagementStatusType.ERROR,
            FileManagementErrorType.UNSPECIFIED_ERROR,
        )
        expected_topic = (
            WAPMF.FILE_UPLOAD_STATUS + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = json.dumps(
            {
                "fileName": file_name,
                "status": status.status.value,
                "error": status.error.value,
            }
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_from_file_management_status(
            status, file_name
        )

        self.assertEqual(expected_message, serialized_message)

    def test_file_url_status_ready(self):
        """Test message for file url management status with file ready."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        file_name = "file_name"
        file_url = "file_url"
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        expected_topic = (
            WAPMF.FILE_URL_DOWNLOAD_STATUS
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
        )
        expected_payload = json.dumps(
            {
                "fileUrl": file_url,
                "status": status.status.value,
                "fileName": file_name,
            }
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_from_file_url_status(
            file_url, status, file_name
        )

        self.assertEqual(expected_message, serialized_message)

    def test_file_url_status_error(self):
        """Test message for file url management status with error status."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        file_url = "file_url"
        status = FileManagementStatus(
            FileManagementStatusType.ERROR,
            FileManagementErrorType.MALFORMED_URL,
        )
        expected_topic = (
            WAPMF.FILE_URL_DOWNLOAD_STATUS
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
        )
        expected_payload = json.dumps(
            {
                "fileUrl": file_url,
                "status": status.status.value,
                "error": status.error.value,
            }
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_from_file_url_status(
            file_url, status
        )

        self.assertEqual(expected_message, serialized_message)

    def test_firmware_update_status(self):
        """Test message for firmware update status."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.INSTALLATION)
        expected_topic = (
            WAPMF.FIRMWARE_UPDATE_STATUS
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
        )
        expected_payload = json.dumps({"status": status.status.value})
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_from_firmware_update_status(status)

        self.assertEqual(expected_message, serialized_message)

    def test_firmware_update_status_error(self):
        """Test message for firmware update status."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.ERROR,
            FirmwareUpdateErrorType.INSTALLATION_FAILED,
        )
        expected_topic = (
            WAPMF.FIRMWARE_UPDATE_STATUS
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
        )
        expected_payload = json.dumps(
            {"status": status.status.value, "error": status.error.value}
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_from_firmware_update_status(status)

        self.assertEqual(expected_message, serialized_message)

    def test_last_will_message(self):
        """Test message for last will."""
        device_key = "some_key"
        factory = WAPMF(device_key)

        expected_topic = (
            WAPMF.LAST_WILL + WAPMF.DEVICE_PATH_PREFIX + device_key
        )
        expected_payload = None
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_last_will_message(device_key)

        self.assertEqual(expected_message, serialized_message)

    def test_firmware_version(self):
        """Test message for firmware version."""
        """Test message for last will."""
        device_key = "some_key"
        factory = WAPMF(device_key)
        version = "v1.0.0"

        expected_topic = (
            WAPMF.FIRMWARE_VERSION_UPDATE
            + WAPMF.DEVICE_PATH_PREFIX
            + device_key
        )
        expected_payload = version
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = factory.make_from_firmware_version(version)

        self.assertEqual(expected_message, serialized_message)
