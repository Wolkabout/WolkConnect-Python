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
from wolk.model.file_transfer_package import FileTransferPackage
from wolk.wolkabout_protocol_message_deserializer import (
    WolkAboutProtocolMessageDeserializer as WAPMD,
)


class WolkAboutProtocolMessageDeserializerTests(unittest.TestCase):
    """Tests for deserializing messages using WolkAbout Protocol."""

    device = Device(
        key="some_key",
        password="some_password",
    )

    # TODO: update
    expected_topics = [
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.TIME,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FILE_BINARY,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FILE_DELETE,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FILE_PURGE,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FILE_LIST_CONFIRM,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FILE_LIST_REQUEST,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FILE_UPLOAD_ABORT,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FILE_UPLOAD_INITIATE,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FILE_URL_ABORT,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FILE_URL_INITIATE,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FIRMWARE_ABORT,
        WAPMD.PLATFORM_TO_DEVICE
        + device.key
        + WAPMD.CHANNEL_DELIMITER
        + WAPMD.FIRMWARE_INSTALL,
    ]

    def setUp(self):
        """Set up commonly used values in tests."""
        self.device = Device(
            key="some_key",
            password="some_password",
        )
        self.deserializer = WAPMD(self.device)

    @unittest.skip("Skip until updated topics")
    def test_inbound_topics_match(self):
        """Test creating a deserializer and assert topic lists match."""
        self.assertEqual(
            self.expected_topics, self.deserializer.inbound_topics
        )

    @unittest.skip("Skip until updated topics")
    def test_get_inbound_topics(self):
        """Test inbound topics are valid for device."""
        self.assertEqual(
            self.expected_topics, self.deserializer.get_inbound_topics()
        )

    def test_is_time_response(self):
        """Test if message is keep alive response."""
        message = Message(self.deserializer.time_topic, None)

        self.assertTrue(self.deserializer.is_time_response(message))

    def test_is_firmware_install(self):
        """Test if message is firmware install command."""
        message = Message(self.deserializer.firmware_install_topic, None)

        self.assertTrue(self.deserializer.is_firmware_install(message))

    def test_is_firmware_abort(self):
        """Test if message is firmware abort command."""
        message = Message(self.deserializer.firmware_abort_topic, None)

        self.assertTrue(self.deserializer.is_firmware_abort(message))

    def test_is_file_binary(self):
        """Test if message is file binary."""
        message = Message(self.deserializer.file_binary_topic, None)

        self.assertTrue(self.deserializer.is_file_binary_response(message))

    def test_is_file_delete_command(self):
        """Test if message is file delete command."""
        message = Message(self.deserializer.file_delete_topic, None)

        self.assertTrue(self.deserializer.is_file_delete_command(message))

    def test_is_file_purge_command(self):
        """Test if message is file purge command."""
        message = Message(self.deserializer.file_purge_topic, None)

        self.assertTrue(self.deserializer.is_file_purge_command(message))

    def test_is_file_list_confirm(self):
        """Test if message is file list confirm."""
        message = Message(self.deserializer.file_list_confirm_topic, None)

        self.assertTrue(self.deserializer.is_file_list_confirm(message))

    def test_is_file_list_request(self):
        """Test if message is file list request."""
        message = Message(self.deserializer.file_list_request_topic, None)

        self.assertTrue(self.deserializer.is_file_list_request(message))

    def test_is_file_upload_initiate(self):
        """Test if message is file upload initiate."""
        message = Message(self.deserializer.file_upload_initiate_topic, None)

        self.assertTrue(self.deserializer.is_file_upload_initiate(message))

    def test_is_file_upload_abort(self):
        """Test if message is file upload abort."""
        message = Message(self.deserializer.file_upload_abort_topic, None)

        self.assertTrue(self.deserializer.is_file_upload_abort(message))

    def test_is_file_url_initiate(self):
        """Test if message is file URL initiate."""
        message = Message(self.deserializer.file_url_initiate_topic, None)

        self.assertTrue(self.deserializer.is_file_url_initiate(message))

    def test_is_file_url_abort(self):
        """Test if message is file URL abort."""
        message = Message(self.deserializer.file_url_abort_topic, None)

        self.assertTrue(self.deserializer.is_file_url_abort(message))

    def test_parse_time_response(self):
        """Test parse keep alive response message."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        timestamp = 123

        incoming_topic = self.deserializer.time_topic
        incoming_payload = bytearray(json.dumps(timestamp), "utf-8")
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = timestamp

        self.assertEqual(
            expected, self.deserializer.parse_time_response(incoming_message)
        )

    def test_parse_firmware_install(self):
        """Test parse firmware install command."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "install_me.bin"

        incoming_topic = self.deserializer.firmware_install_topic
        incoming_payload = bytearray(
            json.dumps({"fileName": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = file_name

        self.assertEqual(
            expected,
            self.deserializer.parse_firmware_install(incoming_message),
        )

    def test_parse_firmware_install_invalid(self):
        """Test parse invalid firmware install command."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "install_me.bin"

        incoming_topic = self.deserializer.firmware_install_topic
        incoming_payload = bytearray(
            json.dumps({"file_name": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = ""

        self.assertEqual(
            expected,
            self.deserializer.parse_firmware_install(incoming_message),
        )

    def test_parse_file_binary_invalid(self):
        """Test parse invalid file binary payload."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "install_me.bin"

        incoming_topic = self.deserializer.file_binary_topic
        incoming_payload = bytearray(
            json.dumps({"file_name": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = FileTransferPackage(b"", b"", b"")

        self.assertEqual(
            expected, self.deserializer.parse_file_binary(incoming_message)
        )

    def test_parse_file_binary_invalid_size(self):
        """Test parse invalid file binary payload size."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        previous_hash = 15 * b"\x00"
        data = b"\x00"
        current_hash = 15 * b"\x00"

        incoming_topic = self.deserializer.file_binary_topic
        incoming_payload = previous_hash + data + current_hash
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = FileTransferPackage(b"", b"", b"")

        self.assertEqual(
            expected, self.deserializer.parse_file_binary(incoming_message)
        )

    def test_parse_file_binary(self):
        """Test parse file binary."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        previous_hash = 32 * b"\x00"
        data = 32 * b"\x00"
        current_hash = 32 * b"\x00"

        incoming_topic = self.deserializer.file_binary_topic
        incoming_payload = previous_hash + data + current_hash
        incoming_message = Message(incoming_topic, incoming_payload)

        expected = FileTransferPackage(previous_hash, data, current_hash)

        self.assertEqual(
            expected, self.deserializer.parse_file_binary(incoming_message)
        )

    def test_parse_file_delete_command(self):
        """Test parse file delete command."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "delete_me.bin"
        expected = file_name

        incoming_topic = self.deserializer.file_delete_topic
        incoming_payload = bytearray(
            json.dumps({"fileName": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected,
            self.deserializer.parse_file_delete_command(incoming_message),
        )

    def test_parse_file_delete_command_invalid(self):
        """Test parse file delete invalid command."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "delete_me.bin"
        expected = ""

        incoming_topic = self.deserializer.file_delete_topic
        incoming_payload = bytearray(
            json.dumps({"file_name": file_name}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected,
            self.deserializer.parse_file_delete_command(incoming_message),
        )

    def test_parse_file_url(self):
        """Test parse file URL command."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        file_url = "http://hello.there.hi/resource.png"
        expected = file_url

        incoming_topic = self.deserializer.file_url_initiate_topic
        incoming_payload = bytearray(
            json.dumps({"fileUrl": file_url}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected, self.deserializer.parse_file_url(incoming_message)
        )

    def test_parse_file_url_invalid(self):
        """Test parse file URL invalid command."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        file_url = "http://hello.there.hi/resource.png"
        expected = ""

        incoming_topic = self.deserializer.file_url_initiate_topic
        incoming_payload = bytearray(
            json.dumps({"file_url": file_url}), "utf-8"
        )
        incoming_message = Message(incoming_topic, incoming_payload)

        self.assertEqual(
            expected, self.deserializer.parse_file_url(incoming_message)
        )

    def test_parse_file_initiate(self):
        """Test parse file initiate command."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "file.bin"
        file_size = 128
        file_hash = "some_hash"
        expected = (file_name, file_size, file_hash)

        incoming_topic = self.deserializer.file_upload_initiate_topic
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
            expected, self.deserializer.parse_file_initiate(incoming_message)
        )

    def test_parse_file_initiate_invalid(self):
        """Test parse file initiate invalid command."""
        self.deserializer.logger.setLevel(logging.CRITICAL)
        file_name = "file.bin"
        file_size = 128
        file_hash = "some_hash"
        expected = ("", 0, "")

        incoming_topic = self.deserializer.file_upload_initiate_topic
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
            expected, self.deserializer.parse_file_initiate(incoming_message)
        )
