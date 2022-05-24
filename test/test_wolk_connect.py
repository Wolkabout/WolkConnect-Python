"""Tests for WolkConnect."""
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
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.append("..")

from wolk.wolk_connect import WolkConnect
from wolk.model.device import Device
from wolk.model.data_delivery import DataDelivery
from wolk.model.data_type import DataType
from wolk.model.feed_type import FeedType
from wolk.model.unit import Unit
from wolk.model.message import Message
from wolk.model.firmware_update_status import (
    FirmwareUpdateStatus,
    FirmwareUpdateStatusType,
)
from wolk.model.file_management_status import (
    FileManagementStatus,
    FileManagementStatusType,
)
from wolk.interface.firmware_handler import FirmwareHandler
from wolk.message_deque import MessageDeque
from wolk.wolkabout_protocol_message_deserializer import (
    WolkAboutProtocolMessageDeserializer as WAPMD,
)
from wolk.wolkabout_protocol_message_factory import (
    WolkAboutProtocolMessageFactory as WAPMF,
)
from wolk.mqtt_connectivity_service import MQTTConnectivityService


class TestWolkConnect(unittest.TestCase):
    """Tests for WolkConnect class."""

    class MockFirmwareHandler(FirmwareHandler):
        """Mock firmware installer class that whose methods will be mocked."""

        def install_firmware(self, firmware_file_path: str) -> None:
            """
            Handle the installation of the firmware file.

            :param firmware_file_path: Path where the firmware file is located
            :type firmware_file_path: str
            """
            raise NotImplementedError()

        def get_current_version(self) -> str:
            """
            Obtain device's current firmware version.

            :returns: version
            :rtype: str
            """
            raise NotImplementedError()

    def setUp(self) -> None:
        """Set up values that are commonly used in tests."""
        self.maxDiff = None
        self.device_key = "some_key"
        self.device_password = "some_password"
        self.device = Device(self.device_key, self.device_password)

        self.wolk_device = WolkConnect(self.device)
        self.wolk_device.logger.setLevel(logging.CRITICAL)
        self.file_directory = "test_files"

        self.firmware_handler = self.MockFirmwareHandler()

        self.message = Message("some_topic", "payload")

        self.file_name = "file"
        self.file_url = "file_url"

    def test_init_default_server(self):
        """Test creating instance with default server parameters."""
        self.assertIsNotNone(self.wolk_device.connectivity_service.ca_cert)

    def test_init_custom_server_unsecure(self):
        """Test creating instance with server on unsecure port."""
        self.wolk_device = WolkConnect(self.device, "some_host", 1883)
        self.assertIsNone(self.wolk_device.connectivity_service.ca_cert)

    def test_init_custom_server_secure(self):
        """Test creating instance with server on secure port."""
        self.wolk_device = WolkConnect(
            self.device, "some_host", 1883, "some_cert"
        )
        self.assertIsNotNone(self.wolk_device.connectivity_service.ca_cert)

    def test_with_feed_value_handler_not_callable(self):
        """Test adding faulty feed value handler that is not callable."""
        self.assertRaises(
            ValueError,
            self.wolk_device.with_incoming_feed_value_handler,
            None,
        )

    def test_with_feed_handler_invalid_signature(self):
        """Test adding faulty feed value handler with bad signature."""
        self.assertRaises(
            ValueError,
            self.wolk_device.with_incoming_feed_value_handler,
            lambda a, b, c: a,
        )

    def test_with_configuration_valid(self):
        """Test adding configurations with valid handler and provider."""
        self.wolk_device.with_incoming_feed_value_handler(lambda a: None)

        self.assertIsNotNone(self.wolk_device.incoming_feed_value_handler)

    def test_with_file_management(self):
        """Test enabling file management module."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        self.assertTrue(os.path.exists(self.file_directory))
        os.rmdir(self.file_directory)

    def test_with_file_management_with_custom_url_download(self):
        """Test enabling file management module with custom URL download."""

        def _downloader(a, b):
            pass

        self.wolk_device.with_file_management(
            self.file_directory, 1024, _downloader
        )
        os.rmdir(self.file_directory)
        self.assertEqual(
            _downloader, self.wolk_device.file_management.url_downloader
        )

    def test_with_firmware_update_no_file_management(self):
        """Test enabling firmware update module fails if no file management."""
        self.assertRaises(
            RuntimeError, self.wolk_device.with_firmware_update, 12
        )

    def test_with_firmware_update_and_file_management(self):
        """Test enabling firmware update module with file management module."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )

        self.wolk_device.with_firmware_update(self.firmware_handler)

        self.assertIsNotNone(self.wolk_device.file_management)
        self.assertIsNotNone(self.wolk_device.firmware_update)

    def test_with_custom_message_queue_invalid_instance(self):
        """Test using custom message queue with passing bad message queue."""
        self.assertRaises(
            ValueError, self.wolk_device.with_custom_message_queue, 1
        )

    def test_with_custom_message_queue_valid_instance(self):
        """Test using custom message queue with passing good message queue."""

        class MockMessageQueue(MessageDeque):
            pass

        self.wolk_device.with_custom_message_queue(MockMessageQueue())

        self.assertIsInstance(self.wolk_device.message_queue, MockMessageQueue)

    def test_with_custom_protocol_bad_factory(self):
        """Test using custom protocol with bad message factory."""
        self.assertRaises(
            ValueError, self.wolk_device.with_custom_protocol, 12, 34
        )

    def test_with_custom_protocol_bad_deserializer(self):
        """Test using custom protocol with bad message deserializer."""

        class MockFactory(WAPMF):
            pass

        self.assertRaises(
            ValueError,
            self.wolk_device.with_custom_protocol,
            MockFactory(self.device_key),
            34,
        )

    def test_with_custom_protocol_valid(self):
        """Test using custom protocol with valid factory and deserializer."""

        class MockFactory(WAPMF):
            pass

        class MockDeserializer(WAPMD):
            pass

        self.wolk_device.with_custom_protocol(
            MockFactory(self.device_key), MockDeserializer(self.device)
        )

        self.assertIsInstance(self.wolk_device.message_factory, MockFactory)
        self.assertIsInstance(
            self.wolk_device.message_deserializer, MockDeserializer
        )

    def test_with_custom_connectivity_invalid_instance(self):
        """Test using custom connectivity with bad instance."""
        self.assertRaises(
            ValueError, self.wolk_device.with_custom_connectivity, 1
        )

    def test_with_custom_connectivity_valid_instance(self):
        """Test using custom connectivity with valid instance."""

        class MockCS(MQTTConnectivityService):
            pass

        mock_cs = MockCS(self.device, [])
        mock_cs.set_inbound_message_listener = MagicMock()

        self.wolk_device.with_custom_connectivity(mock_cs)

        mock_cs.set_inbound_message_listener.assert_called_once_with(
            self.wolk_device._on_inbound_message
        )

    def test_connect_already_connected(self):
        """Test connecting when already connected."""
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.logger.info = MagicMock()

        self.wolk_device.connect()
        self.wolk_device.logger.info.assert_called_once()

    def test_connect_cs_raises_exception(self):
        """Test connecting with connectivity service failing."""
        self.wolk_device.connectivity_service.connect = MagicMock(
            side_effect=Exception()
        )
        self.wolk_device.logger.exception = MagicMock()

        self.wolk_device.connect()
        self.wolk_device.logger.exception.assert_called_once()

    def test_connect_fail_to_connect(self):
        """Test connecting fails."""
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.connectivity_service.connect = MagicMock(
            return_value=False
        )
        self.wolk_device.logger.exception = MagicMock()

        self.wolk_device.connect()
        self.assertEqual(
            2, self.wolk_device.connectivity_service.is_connected.call_count
        )

    def test_connect_connects(self):
        """Test connecting passes."""
        self.wolk_device.connectivity_service.is_connected = MagicMock()
        self.wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            False,
            True,
        ]
        self.wolk_device.connectivity_service.connect = MagicMock(
            return_value=True
        )
        self.wolk_device.connect()
        self.assertEqual(
            2, self.wolk_device.connectivity_service.is_connected.call_count
        )

    def test_connect_publish_file_list_fails(self):
        """Test connecting passes and fails to publishes file list."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device.connectivity_service.is_connected = MagicMock()
        self.wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        self.wolk_device.connectivity_service.connect = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.connect()
        self.wolk_device.message_queue.put.assert_any_call(
            Message("d2p/some_key/file_list", "[]")
        )
        os.rmdir(self.file_directory)

    def test_connect_publish_file_list(self):
        """Test connecting passes and publishes file list."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device.connectivity_service.is_connected = MagicMock()
        self.wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        self.wolk_device.connectivity_service.connect = MagicMock(
            return_value=True
        )
        self.wolk_device.connect()
        self.wolk_device.message_queue.put.assert_not_called()
        os.rmdir(self.file_directory)

    def test_connect_publish_firmware_version_fails(self):
        """Test connecting passes and firmware version fails to send."""
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )

        self.wolk_device.with_file_management(self.file_directory, 1024)
        self.wolk_device.with_firmware_update(self.firmware_handler)
        self.wolk_device.file_management = None
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device.connectivity_service.is_connected = MagicMock()
        self.wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        self.wolk_device.connectivity_service.connect = MagicMock(
            return_value=True
        )
        self.wolk_device.connect()
        self.wolk_device.message_queue.put.assert_called_once()
        os.rmdir(self.file_directory)

    def test_connect_publish_firmware_version_passes(self):
        """Test connecting passes and firmware version is sent."""
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )

        self.wolk_device.with_file_management(self.file_directory, 1024)
        self.wolk_device.with_firmware_update(self.firmware_handler)
        self.wolk_device.file_management = None
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device.connectivity_service.is_connected = MagicMock()
        self.wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        self.wolk_device.connectivity_service.connect = MagicMock(
            return_value=True
        )
        self.wolk_device.connect()
        self.wolk_device.message_queue.put.assert_not_called()
        os.rmdir(self.file_directory)

    def test_connect_publish_pull_device(self):
        """Test connecting passes and PULL type device calls pull functions."""
        self.wolk_device.device.data_delivery = DataDelivery.PULL
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.pull_parameters = MagicMock()
        self.wolk_device.pull_feed_values = MagicMock()

        self.wolk_device.connectivity_service.is_connected = MagicMock()
        self.wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        self.wolk_device.connectivity_service.connect = MagicMock(
            return_value=True
        )
        self.wolk_device.connect()
        self.wolk_device.pull_parameters.assert_called_once()
        self.wolk_device.pull_feed_values.assert_called_once()

    def test_disconnect_not_connected(self):
        """Test calling disconnect when not connected."""
        self.wolk_device.logger.setLevel(logging.DEBUG)
        self.wolk_device.logger.debug = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.disconnect()
        self.wolk_device.logger.debug.assert_not_called()

    def test_disconnect_when_connected(self):
        """Test calling disconnect when connected."""
        self.wolk_device.logger.setLevel(logging.DEBUG)
        self.wolk_device.logger.debug = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.disconnect = MagicMock()
        self.wolk_device.disconnect()
        self.wolk_device.logger.debug.assert_called_once()

    def test_publish_not_connected(self):
        """Test publishing when not connected."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.publish()
        self.wolk_device.logger.warning.assert_called_once()

    def test_publish_emtpy_queue(self):
        """Test publishing when queue is empty."""
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.peek = MagicMock(return_value=None)
        self.wolk_device.publish()
        self.wolk_device.message_queue.peek.assert_called_once()

    def test_publish_fail_to_publish(self):
        """Test publishing and failing to publish message."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.peek = MagicMock(return_value=True)
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.publish()
        self.wolk_device.logger.warning.assert_called_once()

    def test_publish_success(self):
        """Test publishing successfully."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.peek = MagicMock()
        self.wolk_device.message_queue.peek.side_effect = [True, None]
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.get = MagicMock()
        self.wolk_device.publish()
        self.wolk_device.message_queue.get.assert_called_once()

    def test_on_inbound_message_binary_topic(self):
        """Test on inbound message with 'binary' in topic."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        message = Message("binary", "payload")
        self.wolk_device.logger.warning = MagicMock()

        self.wolk_device._on_inbound_message(message)
        self.wolk_device.logger.warning.assert_called_once()

    def test_on_inbound_message_unknown(self):
        """Test on inbound message for unknown message."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()

        self.wolk_device._on_inbound_message(self.message)
        self.wolk_device.logger.warning.assert_called_once()

    def test_on_inbound_message_actuation_no_handlers(self):
        """Test on inbound actuation message but no actuation handler set."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_deserializer.is_actuation_command = MagicMock(
            return_value=True
        )

        self.wolk_device._on_inbound_message(self.message)
        self.wolk_device.logger.warning.assert_called_once()

    def test_on_inbound_message_time_response(self):
        """Test on inbound time response message."""
        timestamp = 1

        self.wolk_device.message_deserializer.is_time_response = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.parse_time_response = MagicMock(
            return_value=timestamp
        )
        self.wolk_device._on_inbound_message(self.message)
        self.assertEqual(timestamp, self.wolk_device.last_platform_timestamp)

    def test_on_inbound_message_file_management_message(self):
        """Test on inbound file management message."""
        self.wolk_device._on_file_management_message = MagicMock()
        self.wolk_device.message_deserializer.is_file_management_message = (
            MagicMock(return_value=True)
        )
        self.wolk_device._on_inbound_message(self.message)
        self.wolk_device._on_file_management_message.assert_called_once()

    def test_on_inbound_message_firmware_message(self):
        """Test on inbound firmware message."""
        self.wolk_device._on_firmware_message = MagicMock()
        self.wolk_device.message_deserializer.is_firmware_message = MagicMock(
            return_value=True
        )
        self.wolk_device._on_inbound_message(self.message)
        self.wolk_device._on_firmware_message.assert_called_once()

    def test_on_file_management_message_no_module_fail_to_send(self):
        """Test on file management message with no module."""
        self.wolk_device.message_factory.make_from_file_management_status = (
            MagicMock()
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.message_queue.put.assert_called_once()

    def test_on_file_management_message_no_module_sends_error(self):
        """Test on file management message with no module, sends message."""
        self.wolk_device.message_factory.make_from_file_management_status = (
            MagicMock()
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_file_management_message_invalid_file_upload_init(self):
        """Test on file management message - invalid file upload initiate."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_upload_initiate = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_deserializer.parse_file_initiate = MagicMock(
            return_value=("", 0, b"")
        )
        self.wolk_device.file_management.handle_upload_initiation = MagicMock()
        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.file_management.handle_upload_initiation.assert_not_called()

    def test_on_file_management_message_file_upload_init(self):
        """Test on file management message file upload initiate."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_upload_initiate = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_deserializer.parse_file_initiate = MagicMock(
            return_value=("file", 0, b"")
        )
        self.wolk_device.file_management.handle_upload_initiation = MagicMock()
        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.file_management.handle_upload_initiation.assert_called_once_with(
            "file", 0, b""
        )

    def test_on_file_management_message_file_binary_response(self):
        """Test on file management message file binary response."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_binary_response = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_deserializer.parse_file_binary = MagicMock(
            return_value=True
        )
        self.wolk_device.file_management.handle_file_binary_response = (
            MagicMock()
        )
        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.file_management.handle_file_binary_response.assert_called_once_with(
            True
        )

    def test_on_file_management_message_file_upload_abort(self):
        """Test on file management message file upload abort."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_upload_abort = MagicMock(
            return_value=True
        )
        self.wolk_device.file_management.handle_file_upload_abort = MagicMock()
        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.file_management.handle_file_upload_abort.assert_called_once()

    def test_on_file_management_message_file_url_abort(self):
        """Test on file management message file URL abort."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_url_abort = MagicMock(
            return_value=True
        )
        self.wolk_device.file_management.handle_file_upload_abort = MagicMock()
        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.file_management.handle_file_upload_abort.assert_called_once()

    def test_on_file_management_message_invalid_file_url_init(self):
        """Test on file management message - invalid file URL initiate."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_url_initiate = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.parse_file_url = MagicMock(
            return_value=""
        )
        self.wolk_device.file_management.handle_url_initiation = MagicMock()
        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.file_management.handle_url_initiation.assert_not_called()

    def test_on_file_management_message_file_url_init(self):
        """Test on file management message file URL initiate."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_url_initiate = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.parse_file_url = MagicMock(
            return_value="URL"
        )
        self.wolk_device.file_management.handle_file_url_download_initiation = (
            MagicMock()
        )
        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.file_management.handle_file_url_download_initiation.assert_called_once_with(
            "URL"
        )

    def test_on_file_management_message_file_file_list_(self):
        """Test on file management message file URL initiate."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_url_initiate = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.parse_file_url = MagicMock(
            return_value="URL"
        )
        self.wolk_device.file_management.handle_file_url_download_initiation = (
            MagicMock()
        )
        self.wolk_device._on_file_management_message(self.message)
        self.wolk_device.file_management.handle_file_url_download_initiation.assert_called_once_with(
            "URL"
        )

    def test_on_file_management_message_file_list_request_publishes(self):
        """Test on file list request fails to publish and puts in queue."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_list_request = MagicMock(
            return_value=True
        )
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_management_message(self.message)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_file_management_message_file_delete_invalid_name(self):
        """Test receiving invalid file delete command."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_delete_command = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_deserializer.parse_file_delete_command = (
            MagicMock(return_value="")
        )
        self.wolk_device.file_management.handle_file_delete = MagicMock()

        self.wolk_device._on_file_management_message(self.message)

        self.wolk_device.file_management.handle_file_delete.assert_not_called()

    def test_on_file_management_message_file_delete_fail_to_publish(self):
        """Test receiving file delete command and fail to publish file list."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_delete_command = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_deserializer.parse_file_delete_command = (
            MagicMock(return_value="file")
        )
        self.wolk_device.file_management.handle_file_delete = MagicMock()
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        self.wolk_device.message_factory.make_from_file_list = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_management_message(self.message)

        self.wolk_device.message_queue.put.assert_called_once()

    def test_on_file_management_message_file_delete_publishes(self):
        """Test receiving file delete command and send file list."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_delete_command = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_deserializer.parse_file_delete_command = (
            MagicMock(return_value="file")
        )
        self.wolk_device.file_management.handle_file_delete = MagicMock()
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        self.wolk_device.message_factory.make_from_file_list = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_management_message(self.message)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_file_management_message_file_purge_fail_to_publish(self):
        """Test receiving file purge command and fail to publish file list."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_purge_command = (
            MagicMock(return_value=True)
        )
        self.wolk_device.file_management.handle_file_purge = MagicMock()
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        self.wolk_device.message_factory.make_from_file_list = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_management_message(self.message)

        self.wolk_device.message_queue.put.assert_called_once()

    def test_on_file_management_message_file_purge_publishes(self):
        """Test receiving file purge command and send file list."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_deserializer.is_file_purge_command = (
            MagicMock(return_value=True)
        )
        self.wolk_device.file_management.handle_file_purge = MagicMock()
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        self.wolk_device.message_factory.make_from_file_list = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_management_message(self.message)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_file_management_message_unkown(self):
        """Test receiving unknown file management message."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.logger.warning = MagicMock()

        self.wolk_device._on_file_management_message(self.message)

        self.wolk_device.logger.warning.assert_called_once()

    def test_on_firmware_message_no_module_fail_to_publish(self):
        """Test receiving firmware message with no module and fail to publish."""
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )

        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device._on_firmware_message(self.message)
        self.wolk_device.message_queue.put.assert_called_once()

    def test_on_firmware_message_no_module_fail_publishes(self):
        """Test receiving firmware message with no module and fail to publish."""
        self.wolk_device.logger.warning = MagicMock()

        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )

        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device._on_firmware_message(self.message)
        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_message_firmware_install_no_path_fail_to_publish(
        self,
    ):
        """Test install command non-present file and fail to publish status."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)
        self.wolk_device.message_deserializer.is_firmware_install = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.parse_firmware_install = (
            MagicMock(return_value=None)
        )
        self.wolk_device.file_management.get_file_path = MagicMock(
            return_value=None
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_firmware_message(self.message)

        self.wolk_device.message_queue.put.assert_called_once()

    def test_on_firmware_message_firmware_install_no_path_publishes(
        self,
    ):
        """Test install command non-present file and publishes status."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.is_firmware_install = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.parse_firmware_install = (
            MagicMock(return_value=None)
        )
        self.wolk_device.file_management.get_file_path = MagicMock(
            return_value=None
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_firmware_message(self.message)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_message_firmware_install_with_path_calls_intsall(
        self,
    ):
        """Test install command present file calls handle install."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.is_firmware_install = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.parse_firmware_install = (
            MagicMock(return_value=None)
        )
        self.wolk_device.file_management.get_file_path = MagicMock(
            return_value="file"
        )
        self.wolk_device.firmware_update.handle_install = MagicMock()
        self.wolk_device._on_firmware_message(self.message)

        self.wolk_device.firmware_update.handle_install.assert_called_once_with(
            "file"
        )

    def test_on_firmware_message_firmware_abort(self):
        """Test abort command calls handle abort."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)
        self.wolk_device.message_deserializer.is_firmware_abort = MagicMock(
            return_value=True
        )
        self.wolk_device.firmware_update.handle_abort = MagicMock()
        self.wolk_device._on_firmware_message(self.message)

        self.wolk_device.firmware_update.handle_abort.assert_called_once_with()

    def test_on_firmware_message_firmware_version_request_pulishes(self):
        """Test receiving version request and publishes response."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)
        self.wolk_device.message_deserializer.is_firmware_version_request = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_factory.make_from_firmware_version_response = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_firmware_message(self.message)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_message_unknown(self):
        """Test receiving unknown firmware message."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)
        self.wolk_device.logger.warning = MagicMock()

        self.wolk_device._on_firmware_message(self.message)

        self.wolk_device.logger.warning.assert_called_once()

    def test_on_package_request_fails_to_publish(self):
        """Test making package request and failing to send it."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.wolk_device.message_factory.make_from_package_request = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_package_request("file", 0)

        self.wolk_device.message_queue.put.assert_called_once()

    def test_on_package_request_publishes(self):
        """Test making package request and publishing it."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.wolk_device.message_factory.make_from_package_request = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_package_request("file", 0)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_update_status_not_connected(self):
        """Test on firmware update status call when not connected."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.INSTALLING)
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.connectivity_service.publish = MagicMock()
        self.wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device._on_firmware_update_status(status)

        self.wolk_device.connectivity_service.publish.assert_not_called()

    def test_on_firmware_update_status_fail_to_publish(self):
        """Test on firmware update status and fail to publish."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.INSTALLING)
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device._on_firmware_update_status(status)

        self.wolk_device.message_queue.put.assert_called_once()

    def test_on_firmware_update_status_publishes(self):
        """Test on firmware update status and publishes the message."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.INSTALLING)
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device._on_firmware_update_status(status)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_update_status_completed_not_connected(self):
        """Test on firmware status completed and not connected."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.SUCCESS)
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.connectivity_service.publish = MagicMock()
        self.wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_factory.make_from_firmware_version_update = (
            MagicMock(return_value=True)
        )
        self.wolk_device._on_firmware_update_status(status)

        self.wolk_device.connectivity_service.publish.assert_not_called()

    def test_on_firmware_update_status_completed_fail_to_publish(self):
        """Test on firmware status completed and fail to publish."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.SUCCESS)
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_factory.make_from_firmware_version_update = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device._on_firmware_update_status(status)

        self.assertEqual(2, self.wolk_device.message_queue.put.call_count)

    def test_on_firmware_update_status_completed_publishes(self):
        """Test on firmware status completed and publishes message."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)
        self.firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        self.wolk_device.with_firmware_update(self.firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.SUCCESS)
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_factory.make_from_firmware_version_update = (
            MagicMock(return_value=True)
        )
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device._on_firmware_update_status(status)
        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_file_upload_status_fail_to_publish(self):
        """Test on file upload status and fail to publish message."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_TRANSFER)
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_upload_status(self.file_name, status)

        self.wolk_device.message_queue.put.assert_called_once()

    def test_on_file_upload_status_publishes(self):
        """Test on file upload status and publishes message."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_TRANSFER)
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_upload_status(self.file_name, status)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_file_upload_status_file_ready_fail_to_publish(self):
        """Test on file upload status and fail to publish message."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_factory.make_from_file_list = MagicMock(
            return_value=True
        )
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_upload_status(self.file_name, status)

        self.assertEqual(2, self.wolk_device.message_queue.put.call_count)

    def test_on_file_upload_status_file_ready_published(self):
        """Test on file upload status and publishes message."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_factory.make_from_file_list = MagicMock(
            return_value=True
        )
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_upload_status(self.file_name, status)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_file_url_status_fail_to_publish(self):
        """Test on file URL status and fail to publish update."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_factory.make_from_file_url_status = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_TRANSFER)
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_url_status(self.file_url, status)

        self.wolk_device.message_queue.put.assert_called_once()

    def test_on_file_url_status_publishes(self):
        """Test on file URL status and publishes update."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_factory.make_from_file_url_status = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_TRANSFER)
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_url_status(self.file_url, status)

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_file_url_status_with_file_name_fail_to_publish(self):
        """Test on URL upload status and fail to publish message."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_factory.make_from_file_url_status = MagicMock(
            return_value=True
        )
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_url_status(
            self.file_url, status, self.file_name
        )

        self.assertEqual(2, self.wolk_device.message_queue.put.call_count)

    def test_on_file_url_status_with_file_name_publishes(self):
        """Test on URL upload status and publishes message."""
        self.wolk_device.with_file_management(self.file_directory, 1024)
        os.rmdir(self.file_directory)

        self.wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_factory.make_from_file_url_status = MagicMock(
            return_value=True
        )
        self.wolk_device.file_management.get_file_list = MagicMock(
            return_value=[]
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        self.wolk_device.message_queue.put = MagicMock()

        self.wolk_device._on_file_url_status(
            self.file_url, status, self.file_name
        )

        self.wolk_device.message_queue.put.assert_not_called()

    def test_on_parameters_message(self):
        """Test on parameters message received."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.message_deserializer.parse_parameters = MagicMock(
            return_value=[{}]
        )
        self.wolk_device.message_deserializer.is_parameters = MagicMock(
            return_value=True
        )
        self.wolk_device.parameters = MagicMock()
        self.wolk_device.parameters.update = MagicMock()
        self.wolk_device._on_inbound_message(Message("test"))

        self.wolk_device.parameters.update.assert_called_once()

    def test_on_feed_values_message_no_handler(self):
        """Test on feed values message received with no handler."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_deserializer.is_parameters = MagicMock(
            return_value=False
        )
        self.wolk_device.message_deserializer.is_feed_values = MagicMock(
            return_value=True
        )
        self.wolk_device.incoming_feed_value_handler = None
        self.wolk_device._on_inbound_message(Message("test"))

        self.wolk_device.logger.warning.assert_called_once()

    def test_on_feed_values_message_fail_to_parse(self):
        """Test on feed values message that failed to parse."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_deserializer.is_parameters = MagicMock(
            return_value=False
        )
        self.wolk_device.message_deserializer.is_feed_values = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.parse_feed_values = MagicMock(
            return_value=None
        )
        self.wolk_device.incoming_feed_value_handler = True
        self.wolk_device._on_inbound_message(Message("test"))

        self.wolk_device.logger.warning.assert_called_once()

    def test_on_feed_values_message(self):
        """Test on feed values message."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_deserializer.is_parameters = MagicMock(
            return_value=False
        )
        self.wolk_device.message_deserializer.is_feed_values = MagicMock(
            return_value=True
        )
        self.wolk_device.message_deserializer.parse_feed_values = MagicMock(
            return_value=True
        )
        self.wolk_device.incoming_feed_value_handler = MagicMock()
        self.wolk_device._on_inbound_message(Message("test"))

        self.wolk_device.incoming_feed_value_handler.assert_called_once_with(
            True
        )
        self.wolk_device.logger.warning.assert_not_called()

    def test_request_timestamp_when_none(self):
        """Test request timestamp returns none."""
        self.assertIsNone(self.wolk_device.request_timestamp())

    def test_request_timestamp_when_not_none(self):
        """Test request timestamp returns value."""
        self.wolk_device.last_platform_timestamp = 1

        self.assertIsNotNone(self.wolk_device.request_timestamp())

    def test_add_feed_value(self):
        """Test add feed value."""
        self.wolk_device.logger.setLevel(logging.CRITICAL)
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.message_factory.make_from_feed_value = MagicMock(
            return_value=True
        )

        self.wolk_device.add_feed_value("foo", "bar")

        self.wolk_device.message_queue.put.assert_called_once()

    def test_pull_parameters_not_pull_device(self):
        """Test pull parameters for a device that isn't PULL."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()

        self.wolk_device.pull_parameters()

        self.wolk_device.logger.warning.assert_called_once()

    def test_pull_parameters_not_connected(self):
        """Test pull parameters when not connected."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.device.data_delivery = DataDelivery.PULL

        self.wolk_device.pull_parameters()

        self.wolk_device.logger.warning.assert_called_once()

    def test_pull_parameters_fails_to_publish(self):
        """Test pull parameters fails to publish."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.device.data_delivery = DataDelivery.PULL
        self.wolk_device.message_factory.make_pull_parameters = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )

        self.wolk_device.pull_parameters()

        self.wolk_device.logger.warning.assert_called_once()

    def test_pull_parameters_publishes(self):
        """Test pull parameters publishes."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.device.data_delivery = DataDelivery.PULL
        self.wolk_device.message_factory.make_pull_parameters = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )

        self.wolk_device.pull_parameters()

        self.wolk_device.logger.warning.assert_not_called()

    def test_pull_feed_values_not_pull_device(self):
        """Test pull feed values for a device that isn't PULL."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()

        self.wolk_device.pull_feed_values()

        self.wolk_device.logger.warning.assert_called_once()

    def test_pull_feed_values_not_connected(self):
        """Test pull feed values when not connected."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.device.data_delivery = DataDelivery.PULL

        self.wolk_device.pull_feed_values()

        self.wolk_device.logger.warning.assert_called_once()

    def test_pull_feed_values_fails_to_publish(self):
        """Test pull feed values fails to publish."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.device.data_delivery = DataDelivery.PULL
        self.wolk_device.message_factory.make_pull_feed_values = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )

        self.wolk_device.pull_feed_values()

        self.wolk_device.logger.warning.assert_called_once()

    def test_pull_feed_values_publishes(self):
        """Test pull feed values publishes."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.device.data_delivery = DataDelivery.PULL
        self.wolk_device.message_factory.make_pull_feed_values = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )

        self.wolk_device.pull_feed_values()

        self.wolk_device.logger.warning.assert_not_called()

    def test_register_feed_not_connected(self):
        """Test registering a feed when not connected."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.message_factory.make_feed_registration = MagicMock(
            return_value=True
        )

        self.wolk_device.register_feed("foo", "bar", FeedType.IN, Unit.CELSIUS)

        self.wolk_device.logger.warning.assert_called_once()

    def test_register_feed_fails_to_publish(self):
        """Test registering a feed when not connected."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.message_factory.make_feed_registration = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )

        self.wolk_device.register_feed("foo", "bar", FeedType.IN, Unit.CELSIUS)

        self.wolk_device.logger.warning.assert_called_once()
        self.wolk_device.message_queue.put.assert_called_once()

    def test_register_feed_custom_unit(self):
        """Test registering a feed with custom unit."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.message_factory.make_feed_registration = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )

        self.wolk_device.register_feed("foo", "bar", FeedType.IN, "custom")

        self.wolk_device.logger.warning.assert_called_once()

    def test_remove_feed_not_connected(self):
        """Test removing a feed when not connected."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.message_factory.make_feed_removal = MagicMock(
            return_value=True
        )

        self.wolk_device.remove_feed("foo")

        self.wolk_device.logger.warning.assert_called_once()
        self.wolk_device.message_queue.put.assert_called_once()

    def test_remove_feed_fail_to_publish(self):
        """Test removing a feed fails to publish."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.message_factory.make_feed_removal = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )

        self.wolk_device.remove_feed("foo")

        self.wolk_device.logger.warning.assert_called_once()
        self.wolk_device.message_queue.put.assert_called_once()

    def test_remove_feed_publishes(self):
        """Test remove feed request publishes."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.message_factory.make_feed_removal = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )

        self.wolk_device.remove_feed("foo")

        self.wolk_device.logger.warning.assert_not_called()
        self.wolk_device.message_queue.put.assert_not_called()

    def test_register_attribute_not_connected(self):
        """Test registering attribute when not connected."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        self.wolk_device.message_factory.make_attribute_registration = (
            MagicMock(return_value=True)
        )

        self.wolk_device.register_attribute("foo", DataType.STRING, "bar")

        self.wolk_device.logger.warning.assert_called_once()
        self.wolk_device.message_queue.put.assert_called_once()

    def test_register_attribute_fails_to_publish(self):
        """Test registering attribute that fails to publish."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        self.wolk_device.message_factory.make_attribute_registration = (
            MagicMock(return_value=True)
        )

        self.wolk_device.register_attribute("foo", DataType.STRING, "bar")

        self.wolk_device.logger.warning.assert_called_once()
        self.wolk_device.message_queue.put.assert_called_once()

    def test_register_attribute_publishes(self):
        """Test registering attribute publishes."""
        self.wolk_device.logger.setLevel(logging.WARNING)
        self.wolk_device.logger.warning = MagicMock()
        self.wolk_device.message_queue.put = MagicMock()
        self.wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        self.wolk_device.connectivity_service.publish = MagicMock(
            return_value=True
        )
        self.wolk_device.message_factory.make_attribute_registration = (
            MagicMock(return_value=True)
        )

        self.wolk_device.register_attribute("foo", DataType.STRING, "bar")

        self.wolk_device.logger.warning.assert_not_called()
        self.wolk_device.message_queue.put.assert_not_called()
