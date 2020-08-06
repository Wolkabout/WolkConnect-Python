"""Tests for WolkAboutProtocolMessageDeserializer."""
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
import logging
import sys
import unittest

sys.path.append("..")  # noqa

from wolk.model.device import Device
from wolk.model.message import Message
from wolk.model.actuator_command import ActuatorCommand
from wolk.model.configuration_command import ConfigurationCommand
from wolk.model.file_transfer_package import FileTransferPackage
from wolk.wolkabout_protocol_message_deserializer import (
    WolkAboutProtocolMessageDeserializer as WAPMD,
)


class WolkAboutProtocolMessageDeserializerTests(unittest.TestCase):
    """Tests for deserializing messages using WolkAbout Protocol."""

    device = Device(
        key="some_key",
        password="some_password",
        actuator_references=["SW", "SL", "ST"],
    )

    expected_topics = [
        WAPMD.KEEP_ALIVE_RESPONSE + device.key,
        WAPMD.CONFIGURATION_SET + WAPMD.DEVICE_PATH_DELIMITER + device.key,
        WAPMD.FILE_BINARY_RESPONSE + WAPMD.DEVICE_PATH_DELIMITER + device.key,
        WAPMD.FILE_DELETE + WAPMD.DEVICE_PATH_DELIMITER + device.key,
        WAPMD.FILE_PURGE + WAPMD.DEVICE_PATH_DELIMITER + device.key,
        WAPMD.FILE_LIST_CONFIRM + WAPMD.DEVICE_PATH_DELIMITER + device.key,
        WAPMD.FILE_LIST_REQUEST + WAPMD.DEVICE_PATH_DELIMITER + device.key,
        WAPMD.FILE_UPLOAD_ABORT + WAPMD.DEVICE_PATH_DELIMITER + device.key,
        WAPMD.FILE_UPLOAD_INITIATE + WAPMD.DEVICE_PATH_DELIMITER + device.key,
        WAPMD.FILE_URL_DOWNLOAD_ABORT
        + WAPMD.DEVICE_PATH_DELIMITER
        + device.key,
        WAPMD.FILE_URL_DOWNLOAD_INITIATE
        + WAPMD.DEVICE_PATH_DELIMITER
        + device.key,
        WAPMD.FIRMWARE_UPDATE_ABORT + WAPMD.DEVICE_PATH_DELIMITER + device.key,
        WAPMD.FIRMWARE_UPDATE_INSTALL
        + WAPMD.DEVICE_PATH_DELIMITER
        + device.key,
    ]
    for reference in device.actuator_references:
        expected_topics.append(
            WAPMD.ACTUATOR_SET
            + WAPMD.DEVICE_PATH_DELIMITER
            + device.key
            + WAPMD.CHANNEL_DELIMITER
            + WAPMD.REFERENCE_PATH_PREFIX
            + reference
        )

    def test_init(self):
        """Test creating a deserializer and assert topic lists match."""
        deserializer = WAPMD(self.device)

        self.assertEqual(self.expected_topics, deserializer.inbound_topics)

    def test_get_inbound_topics(self):
        """Test inbound topics are valid for device."""
        deserializer = WAPMD(self.device)

        self.assertEqual(
            self.expected_topics, deserializer.get_inbound_topics()
        )

    def test_is_actuation_command(self):
        """Test if message is actuation command."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.ACTUATOR_SET, None)

        self.assertTrue(deserializer.is_actuation_command(message))

    def test_is_keep_alive_response(self):
        """Test if message is keep alive response."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.KEEP_ALIVE_RESPONSE, None)

        self.assertTrue(deserializer.is_keep_alive_response(message))

    def test_is_firmware_install(self):
        """Test if message is firmware install command."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.ACTUATOR_SET, None)

        self.assertFalse(deserializer.is_firmware_install(message))

    def test_is_firmware_abort(self):
        """Test if message is firmware abort command."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FIRMWARE_UPDATE_ABORT, None)

        self.assertTrue(deserializer.is_firmware_abort(message))

    def test_is_file_binary(self):
        """Test if message is file binary."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FILE_BINARY_RESPONSE, None)

        self.assertTrue(deserializer.is_file_binary_response(message))

    def test_is_configuration_command(self):
        """Test if message is configuration command."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.CONFIGURATION_SET, None)

        self.assertTrue(deserializer.is_configuration_command(message))

    def test_is_file_delete_command(self):
        """Test if message is file delete command."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FILE_DELETE, None)

        self.assertTrue(deserializer.is_file_delete_command(message))

    def test_is_file_purge_command(self):
        """Test if message is file purge command."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FILE_PURGE, None)

        self.assertTrue(deserializer.is_file_purge_command(message))

    def test_is_file_list_confirm(self):
        """Test if message is file list confirm."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FILE_LIST_CONFIRM, None)

        self.assertTrue(deserializer.is_file_list_confirm(message))

    def test_is_file_list_request(self):
        """Test if message is file list request."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FILE_LIST_REQUEST, None)

        self.assertTrue(deserializer.is_file_list_request(message))

    def test_is_file_upload_initiate(self):
        """Test if message is file upload initiate."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FILE_UPLOAD_INITIATE, None)

        self.assertTrue(deserializer.is_file_upload_initiate(message))

    def test_is_file_upload_abort(self):
        """Test if message is file upload abort."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FILE_UPLOAD_ABORT, None)

        self.assertTrue(deserializer.is_file_upload_abort(message))

    def test_is_file_url_initiate(self):
        """Test if message is file url initiate."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FILE_URL_DOWNLOAD_INITIATE, None)

        self.assertTrue(deserializer.is_file_url_initiate(message))

    def test_is_file_url_abort(self):
        """Test if message is file url abort."""
        deserializer = WAPMD(self.device)
        message = Message(WAPMD.FILE_URL_DOWNLOAD_ABORT, None)

        self.assertTrue(deserializer.is_file_url_abort(message))

    def test_parse_acutator_command_set_bool(self):
        """Test parse actuator command with command set and value type bool."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)  # Disable logging
        reference = "SW"
        value = False

        incoming_topic = (
            WAPMD.ACTUATOR_SET
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
            + WAPMD.CHANNEL_DELIMITER
            + WAPMD.REFERENCE_PATH_PREFIX
            + reference
        )
        incoming_payload = bytearray(
            json.dumps({"value": str(value).lower()}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ActuatorCommand(reference, value)

        self.assertEqual(
            expected, deserializer.parse_actuator_command(incoming_message)
        )

    def test_parse_acutator_command_set_string_with_newline(self):
        """Test parse actuator command with command set and type string."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        reference = "SW"
        value = "string\nstring"
        expected_value = value.replace("\n", "\\n")

        incoming_topic = (
            WAPMD.ACTUATOR_SET
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
            + WAPMD.CHANNEL_DELIMITER
            + WAPMD.REFERENCE_PATH_PREFIX
            + reference
        )
        incoming_payload = bytearray(
            json.dumps({"value": expected_value}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ActuatorCommand(reference, value)

        self.assertEqual(
            expected, deserializer.parse_actuator_command(incoming_message)
        )

    def test_parse_acutator_command_set_float(self):
        """Test parse actuator command with command set and type float."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        reference = "SL"
        value = "12.3"

        incoming_topic = (
            WAPMD.ACTUATOR_SET
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
            + WAPMD.CHANNEL_DELIMITER
            + WAPMD.REFERENCE_PATH_PREFIX
            + reference
        )
        incoming_payload = bytearray(json.dumps({"value": value}), "utf-8")
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ActuatorCommand(reference, float(value))

        self.assertEqual(
            expected, deserializer.parse_actuator_command(incoming_message)
        )

    def test_parse_acutator_command_set_int(self):
        """Test parse actuator command with command set and type int."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        reference = "SL"
        value = "12"

        incoming_topic = (
            WAPMD.ACTUATOR_SET
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
            + WAPMD.CHANNEL_DELIMITER
            + WAPMD.REFERENCE_PATH_PREFIX
            + reference
        )
        incoming_payload = bytearray(json.dumps({"value": value}), "utf-8")
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ActuatorCommand(reference, int(value))

        self.assertEqual(
            expected, deserializer.parse_actuator_command(incoming_message)
        )

    def test_parse_keep_alive_response(self):
        """Test parse keep alive response message."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        timestamp = 123

        incoming_topic = WAPMD.KEEP_ALIVE_RESPONSE + self.device.key
        incoming_payload = bytearray(json.dumps({"value": timestamp}), "utf-8")
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = timestamp

        self.assertEqual(
            expected, deserializer.parse_keep_alive_response(incoming_message)
        )

    def test_parse_firmware_install(self):
        """Test parse firmware install command."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "install_me.bin"

        incoming_topic = (
            WAPMD.FIRMWARE_UPDATE_INSTALL
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"fileName": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = file_name

        self.assertEqual(
            expected, deserializer.parse_firmware_install(incoming_message)
        )

    def test_parse_firmware_install_invalid(self):
        """Test parse invalid firmware install command."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "install_me.bin"

        incoming_topic = (
            WAPMD.FIRMWARE_UPDATE_INSTALL
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"file_name": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ""

        self.assertEqual(
            expected, deserializer.parse_firmware_install(incoming_message)
        )

    def test_parse_file_binary_invalid(self):
        """Test parse invalid file binary payload."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "install_me.bin"

        incoming_topic = (
            WAPMD.FILE_BINARY_RESPONSE
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"file_name": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = FileTransferPackage(b"", b"", b"")

        self.assertEqual(
            expected, deserializer.parse_file_binary(incoming_message)
        )

    def test_parse_file_binary_invalid_size(self):
        """Test parse invalid file binary payload size."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        previous_hash = 15 * b"\x00"
        data = b"\x00"
        current_hash = 15 * b"\x00"

        incoming_topic = (
            WAPMD.FILE_BINARY_RESPONSE
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = previous_hash + data + current_hash
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = FileTransferPackage(b"", b"", b"")

        self.assertEqual(
            expected, deserializer.parse_file_binary(incoming_message)
        )

    def test_parse_file_binary(self):
        """Test parse file binary."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        previous_hash = 32 * b"\x00"
        data = 32 * b"\x00"
        current_hash = 32 * b"\x00"

        incoming_topic = (
            WAPMD.FILE_BINARY_RESPONSE
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = previous_hash + data + current_hash
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = FileTransferPackage(previous_hash, data, current_hash)

        self.assertEqual(
            expected, deserializer.parse_file_binary(incoming_message)
        )

    def test_parse_configuration_set_bool(self):
        """Test parse configuration set command with bool type."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        reference = "B"
        value = "true"

        incoming_topic = (
            WAPMD.CONFIGURATION_SET
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"values": {reference: value}}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ConfigurationCommand({reference: True})

        self.assertEqual(
            expected, deserializer.parse_configuration(incoming_message)
        )

    def test_parse_configuration_set_string_with_newline(self):
        """Test parse configuration set command for string with newline."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        reference = "S"
        value = "string\nstring"  # escaped in json.dumps

        incoming_topic = (
            WAPMD.CONFIGURATION_SET
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"values": {reference: value}}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ConfigurationCommand({reference: value})

        self.assertEqual(
            expected, deserializer.parse_configuration(incoming_message)
        )

    def test_parse_configuration_set_float(self):
        """Test parse configuration set command for float."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        reference = "F"
        value = 12.3

        incoming_topic = (
            WAPMD.CONFIGURATION_SET
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"values": {reference: str(value)}}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ConfigurationCommand({reference: value})

        self.assertEqual(
            expected, deserializer.parse_configuration(incoming_message)
        )

    def test_parse_configuration_set_int(self):
        """Test parse configuration set command for int."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        reference = "F"
        value = 12

        incoming_topic = (
            WAPMD.CONFIGURATION_SET
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"values": {reference: str(value)}}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ConfigurationCommand({reference: value})

        self.assertEqual(
            expected, deserializer.parse_configuration(incoming_message)
        )

    def test_parse_file_delete_command(self):
        """Test parse file delete command."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "delete_me.bin"
        expected = file_name

        incoming_topic = (
            WAPMD.FILE_DELETE + WAPMD.DEVICE_PATH_DELIMITER + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"fileName": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected, deserializer.parse_file_delete_command(incoming_message)
        )

    def test_parse_file_delete_command_invalid(self):
        """Test parse file delete invalid command."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "delete_me.bin"
        expected = ""

        incoming_topic = (
            WAPMD.FILE_DELETE + WAPMD.DEVICE_PATH_DELIMITER + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"file_name": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected, deserializer.parse_file_delete_command(incoming_message)
        )

    def test_parse_file_url(self):
        """Test parse file url command."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        file_url = "http://hello.there.hi/resource.png"
        expected = file_url

        incoming_topic = (
            WAPMD.FILE_URL_DOWNLOAD_INITIATE
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"fileUrl": file_url}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected, deserializer.parse_file_url(incoming_message)
        )

    def test_parse_file_url_invalid(self):
        """Test parse file url invalid command."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        file_url = "http://hello.there.hi/resource.png"
        expected = ""

        incoming_topic = (
            WAPMD.FILE_URL_DOWNLOAD_INITIATE
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps({"file_url": file_url}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected, deserializer.parse_file_url(incoming_message)
        )

    def test_parse_file_initiate(self):
        """Test parse file initiate command."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "file.bin"
        file_size = 128
        file_hash = "some_hash"
        expected = (file_name, file_size, file_hash)

        incoming_topic = (
            WAPMD.FILE_UPLOAD_INITIATE
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps(
                {
                    "fileName": file_name,
                    "fileSize": file_size,
                    "fileHash": file_hash,
                }
            ),
            "utf-8",
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected, deserializer.parse_file_initiate(incoming_message)
        )

    def test_parse_file_initiate_invalid(self):
        """Test parse file initiate invalid command."""
        deserializer = WAPMD(self.device)
        deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "file.bin"
        file_size = 128
        file_hash = "some_hash"
        expected = ("", 0, "")

        incoming_topic = (
            WAPMD.FILE_UPLOAD_INITIATE
            + WAPMD.DEVICE_PATH_DELIMITER
            + self.device.key
        )
        incoming_payload = bytearray(
            json.dumps(
                {
                    "obviously_wrong_name": file_name,
                    "fileSize": file_size,
                    "fileHash": file_hash,
                }
            ),
            "utf-8",
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected, deserializer.parse_file_initiate(incoming_message)
        )
