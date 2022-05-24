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

from wolk.model.message import Message
from wolk.model.data_type import DataType
from wolk.model.feed_type import FeedType
from wolk.model.unit import Unit
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_error_type import FileManagementErrorType
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.firmware_update_status_type import FirmwareUpdateStatusType
from wolk.model.firmware_update_error_type import FirmwareUpdateErrorType
from wolk.wolkabout_protocol_message_factory import (
    WolkAboutProtocolMessageFactory as WAPMF,
)

unittest.util._MAX_LENGTH = 2000


class WolkAboutProtocolMessageFactoryTests(unittest.TestCase):
    """Tests for serializing messages using WolkAbout Protocol."""

    def setUp(self):
        """Set up commonly used values in tests."""
        self.device_key = "some_key"
        self.factory = WAPMF(self.device_key)

    def test_init(self):
        """Test that object is created with correct device key."""
        self.assertEqual(self.device_key, self.factory.device_key)

    def test_feed_value(self):
        """Test valid message for string feed."""
        reference = "SNL"
        value = "string"
        timestamp = round(time.time()) * 1000

        expected_topic = self.factory.common_topic + WAPMF.FEED_VALUES
        expected_payload = json.dumps(
            [{reference: value, "timestamp": timestamp}]
        )
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_from_feed_value(
            (reference, value), timestamp
        )

        self.assertEqual(expected_message, serialized_message)

    def test_feed_values(self):
        """Test valid message for two string feeds."""
        reference = "SNL"
        value = "string"
        reference_2 = "SNL"
        value_2 = "string"
        timestamp = round(time.time()) * 1000

        expected_topic = self.factory.common_topic + WAPMF.FEED_VALUES
        expected_payload = json.dumps(
            [{reference: value, "timestamp": timestamp}]
        )
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_from_feed_value(
            [(reference, value), (reference_2, value_2)], timestamp
        )

        self.assertEqual(expected_message, serialized_message)

    def test_feed_value_throws_on_invalid_data(self):
        """Test valid message for two string feeds."""
        self.assertRaises(
            ValueError, self.factory.make_from_feed_value, "foo", 1
        )

    def test_file_package_request(self):
        """Test message file package request."""
        file_name = "file_name"
        chunk_index = 0

        expected_topic = self.factory.common_topic + WAPMF.FILE_BINARY_REQUEST
        expected_payload = json.dumps(
            {
                "name": file_name,
                "chunkIndex": chunk_index,
            }
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = self.factory.make_from_package_request(
            file_name, chunk_index
        )

        self.assertEqual(expected_message, serialized_message)

    def test_file_status_ready(self):
        """Test message for file management status with file ready."""
        file_name = "file_name"
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        expected_topic = self.factory.common_topic + WAPMF.FILE_UPLOAD_STATUS
        expected_payload = json.dumps(
            {"name": file_name, "status": status.status.value}
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = self.factory.make_from_file_management_status(
            status, file_name
        )

        self.assertEqual(expected_message, serialized_message)

    def test_file_status_error(self):
        """Test message for file management status with error status."""
        file_name = "file_name"
        status = FileManagementStatus(
            FileManagementStatusType.ERROR,
            FileManagementErrorType.UNKNOWN,
        )
        expected_topic = self.factory.common_topic + WAPMF.FILE_UPLOAD_STATUS
        expected_payload = json.dumps(
            {
                "name": file_name,
                "status": status.status.value,
                "error": status.error.value,
            }
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = self.factory.make_from_file_management_status(
            status, file_name
        )

        self.assertEqual(expected_message, serialized_message)

    def test_file_url_status_ready(self):
        """Test message for file URL management status with file ready."""
        file_name = "file_name"
        file_url = "file_url"
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        expected_topic = (
            self.factory.common_topic + WAPMF.FILE_URL_DOWNLOAD_STATUS
        )
        expected_payload = json.dumps(
            {
                "fileUrl": file_url,
                "status": status.status.value,
                "fileName": file_name,
            }
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = self.factory.make_from_file_url_status(
            file_url, status, file_name
        )

        self.assertEqual(expected_message, serialized_message)

    def test_file_url_status_error(self):
        """Test message for file URL management status with error status."""
        file_url = "file_url"
        status = FileManagementStatus(
            FileManagementStatusType.ERROR,
            FileManagementErrorType.MALFORMED_URL,
        )
        expected_topic = (
            self.factory.common_topic + WAPMF.FILE_URL_DOWNLOAD_STATUS
        )
        expected_payload = json.dumps(
            {
                "fileUrl": file_url,
                "status": status.status.value,
                "error": status.error.value,
            }
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = self.factory.make_from_file_url_status(
            file_url, status
        )

        self.assertEqual(expected_message, serialized_message)

    def test_firmware_update_status(self):
        """Test message for firmware update status."""
        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.INSTALLING)
        expected_topic = (
            self.factory.common_topic + WAPMF.FIRMWARE_UPDATE_STATUS
        )

        expected_payload = json.dumps({"status": status.status.value})
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = self.factory.make_from_firmware_update_status(
            status
        )

        self.assertEqual(expected_message, serialized_message)

    def test_firmware_update_status_error(self):
        """Test message for firmware update status."""
        status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.ERROR,
            FirmwareUpdateErrorType.INSTALLATION_FAILED,
        )
        expected_topic = (
            self.factory.common_topic + WAPMF.FIRMWARE_UPDATE_STATUS
        )

        expected_payload = json.dumps(
            {"status": status.status.value, "error": status.error.value}
        )
        expected_message = Message(expected_topic, expected_payload)
        serialized_message = self.factory.make_from_firmware_update_status(
            status
        )

        self.assertEqual(expected_message, serialized_message)

    def test_time_request_message(self):
        """Test message for time request."""
        expected_topic = self.factory.common_topic + WAPMF.TIME
        expected_payload = None
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_time_request()

        self.assertEqual(expected_message, serialized_message)

    def test_pull_feed_values_message(self):
        """Test message for pull feed values request."""
        expected_topic = self.factory.common_topic + WAPMF.PULL_FEED_VALUES
        expected_payload = None
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_pull_feed_values()

        self.assertEqual(expected_message, serialized_message)

    def test_parameters_message(self):
        """Test message for push parameters value."""
        expected_topic = self.factory.common_topic + WAPMF.PARAMETERS
        values = {
            "bool_parameter": False,
            "int_parameter": 1,
            "float_parameter": 13.37,
            "string_parameter": "foo",
        }
        expected_payload = json.dumps(values)
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_from_parameters(values)

        self.assertEqual(expected_message, serialized_message)

    def test_pull_parameters_message(self):
        """Test message for pull parameters request."""
        expected_topic = self.factory.common_topic + WAPMF.PULL_PARAMETERS
        expected_payload = None
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_pull_parameters()

        self.assertEqual(expected_message, serialized_message)

    def test_feed_registration_message(self):
        """Test message for feed registration request."""
        expected_topic = self.factory.common_topic + WAPMF.FEED_REGISTRATION

        name = "test_feed_name"
        reference = "test_feed_reference"
        feed_type = FeedType.IN
        unit = Unit.CELSIUS

        expected_payload = json.dumps(
            [
                {
                    "name": name,
                    "reference": reference,
                    "type": feed_type.value,
                    "unitGuid": unit.value,
                }
            ]
        )
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_feed_registration(
            name, reference, feed_type, unit
        )

        self.assertEqual(expected_message, serialized_message)

    def test_feed_registration_message_custom_unit(self):
        """Test message for feed registration request with custom unit."""
        expected_topic = self.factory.common_topic + WAPMF.FEED_REGISTRATION

        name = "test_feed_name"
        reference = "test_feed_reference"
        feed_type = FeedType.IN
        unit = "USER_DEFINED_UNIT"

        expected_payload = json.dumps(
            [
                {
                    "name": name,
                    "reference": reference,
                    "type": feed_type.value,
                    "unitGuid": unit,
                }
            ]
        )
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_feed_registration(
            name, reference, feed_type, unit
        )

        self.assertEqual(expected_message, serialized_message)

    def test_feed_removal_message(self):
        """Test message for feed removal."""
        expected_topic = self.factory.common_topic + WAPMF.FEED_REMOVAL

        reference = "test_feed_reference"

        expected_payload = json.dumps([reference])
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_feed_removal(reference)

        self.assertEqual(expected_message, serialized_message)

    def test_attribute_registration_message(self):
        """Test message for attribute registration."""
        expected_topic = (
            self.factory.common_topic + WAPMF.ATTRIBUTE_REGISTRATION
        )

        name = "test_attribute_name"
        data_type = DataType.STRING
        value = "test_attribute_value"

        expected_payload = json.dumps(
            [
                {
                    "name": name,
                    "dataType": data_type.value,
                    "value": value,
                }
            ]
        )
        expected_message = Message(expected_topic, expected_payload)

        serialized_message = self.factory.make_attribute_registration(
            name, data_type, value
        )

        self.assertEqual(expected_message, serialized_message)
