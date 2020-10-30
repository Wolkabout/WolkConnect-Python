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

sys.path.append("..")  # noqa

from wolk.wolk_connect import WolkConnect
from wolk.model.device import Device
from wolk.model.actuator_command import ActuatorCommand
from wolk.model.configuration_command import ConfigurationCommand
from wolk.model.state import State
from wolk.model.actuator_status import ActuatorStatus
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

    def test_init_default_server(self):
        """Test creating instance with default server parameters."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)

        wolk_device = WolkConnect(device)
        self.assertIsNotNone(wolk_device.connectivity_service.ca_cert)

    def test_init_custom_server_unsecure(self):
        """Test creating instance with server on unsecure port."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)

        wolk_device = WolkConnect(device, "some_host", 1883)
        self.assertIsNone(wolk_device.connectivity_service.ca_cert)

    def test_init_custom_server_secure(self):
        """Test creating instance with server on secure port."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)

        wolk_device = WolkConnect(device, "some_host", 1883, "some_cert")
        self.assertIsNotNone(wolk_device.connectivity_service.ca_cert)

    def test_with_actuators_handler_not_callable(self):
        """Test adding faulty actuator handler that is not callable."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(ValueError, wolk_device.with_actuators, 12, 34)

    def test_with_actuators_handler_invalid_signature(self):
        """Test adding faulty actuator handler with bad signature."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(
            ValueError, wolk_device.with_actuators, lambda a, b, c: a, 34
        )

    def test_with_actuators_provider_not_callable(self):
        """Test adding faulty actuator status provider that is not callable."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(
            ValueError, wolk_device.with_actuators, lambda a, b: a, 34
        )

    def test_with_actuators_provider_invalid_signature(self):
        """Test adding actuator status provider with invalid signature."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(
            ValueError,
            wolk_device.with_actuators,
            lambda a, b: a,
            lambda a, b, c: a,
        )

    def test_with_actuators_valid(self):
        """Test adding actuator with valid handler and provider."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device).with_actuators(
            lambda a, b: a,
            lambda a: a,
        )
        self.assertIsNotNone(wolk_device.actuation_handler)

    def test_with_configuration_handler_not_callable(self):
        """Test adding configurations with handler not callable."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(
            ValueError,
            wolk_device.with_configuration,
            13,
            lambda a, b, c: a,
        )

    def test_with_configuration_handler_invalid_signature(self):
        """Test adding configurations with invalid handler signature."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(
            ValueError,
            wolk_device.with_configuration,
            lambda a, b: a,
            lambda a, b, c: a,
        )

    def test_with_configuration_provider_not_callable(self):
        """Test adding configurations with provider not callable."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(
            ValueError,
            wolk_device.with_configuration,
            lambda a: a,
            13,
        )

    def test_with_configuration_provider_invalid_signature(self):
        """Test adding configurations with invalid provider signature."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(
            ValueError,
            wolk_device.with_configuration,
            lambda a: a,
            lambda a, b, c: a,
        )

    def test_with_configuration_valid(self):
        """Test adding configurations with valid handler and provider."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device).with_configuration(
            lambda a: a, lambda: 5
        )

        self.assertIsNotNone(wolk_device.configuration_handler)

    def test_with_file_management(self):
        """Test enabling file management module."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(  # noqa
            256, 1024, file_directory
        )
        self.assertTrue(os.path.exists(file_directory))
        os.rmdir(file_directory)

    def test_with_file_management_with_custom_url_download(self):
        """Test enabling file management module with custorm url download."""
        download = True
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(  # noqa
            256, 1024, file_directory, download
        )
        os.rmdir(file_directory)
        self.assertEqual(download, wolk_device.file_management.download_url)

    def test_with_firmware_update_no_file_management(self):
        """Test enabling firmware update module fails if no file management."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(RuntimeError, wolk_device.with_firmware_update, 12)

    def test_with_firmware_update_and_file_management(self):
        """Test enabling firmware update module with file management module."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")

        wolk_device.with_firmware_update(firmware_handler)

        firmware_handler.get_current_version.assert_called_once()

    def test_with_custom_message_queue_invalid_instance(self):
        """Test using custom message queue with passing bad message queue."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(ValueError, wolk_device.with_custom_message_queue, 1)

    def test_with_custom_message_queue_valid_instance(self):
        """Test using custom message queue with passing good message queue."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        class MockMessageQueue(MessageDeque):
            pass

        wolk_device.with_custom_message_queue(MockMessageQueue())

        self.assertIsInstance(wolk_device.message_queue, MockMessageQueue)

    def test_with_custom_protocol_bad_factory(self):
        """Test using custom protocol with bad message factory."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(ValueError, wolk_device.with_custom_protocol, 12, 34)

    def test_with_custom_protocol_bad_deserializer(self):
        """Test using custom protocol with bad message deserializer."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        class MockFactory(WAPMF):
            pass

        self.assertRaises(
            ValueError,
            wolk_device.with_custom_protocol,
            MockFactory(device_key),
            34,
        )

    def test_with_custom_protocol_valid(self):
        """Test using custom protocol with valid factory and deserializer."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        class MockFactory(WAPMF):
            pass

        class MockDeserializer(WAPMD):
            pass

        wolk_device.with_custom_protocol(
            MockFactory(device_key), MockDeserializer(device)
        )

        self.assertIsInstance(wolk_device.message_factory, MockFactory)

    def test_with_custom_connectivity_invalid_instance(self):
        """Test using custom connectivity with bad instance."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        self.assertRaises(ValueError, wolk_device.with_custom_connectivity, 1)

    def test_with_custom_connectivity_valid_instance(self):
        """Test using custom connectivity with valid instance."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        class MockCS(MQTTConnectivityService):
            pass

        mock_cs = MockCS(device, [], Message("lastwill"))
        mock_cs.set_inbound_message_listener = MagicMock()

        wolk_device.with_custom_connectivity(mock_cs)

        mock_cs.set_inbound_message_listener.assert_called_once_with(
            wolk_device._on_inbound_message
        )

    def test_connect_already_connected(self):
        """Test connecting when already connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.logger.info = MagicMock()

        wolk_device.connect()
        wolk_device.logger.info.assert_called_once()

    def test_connect_cs_raises_exception(self):
        """Test connecting with connectivity service failing."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        wolk_device.connectivity_service.connect = MagicMock(
            side_effect=Exception()
        )
        wolk_device.logger.exception = MagicMock()

        wolk_device.connect()
        wolk_device.logger.exception.assert_called_once()

    def test_connect_fail_to_connect(self):
        """Test connecting fails."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        wolk_device.connectivity_service.connect = MagicMock(
            return_value=False
        )
        wolk_device.logger.exception = MagicMock()

        wolk_device.connect()
        self.assertEqual(
            2, wolk_device.connectivity_service.is_connected.call_count
        )

    def test_connect_connects(self):
        """Test connecting passes."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        wolk_device.connectivity_service.is_connected = MagicMock()
        wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            False,
            True,
        ]
        wolk_device.connectivity_service.connect = MagicMock(return_value=True)
        wolk_device.connect()
        self.assertEqual(
            2, wolk_device.connectivity_service.is_connected.call_count
        )

    def test_connect_publishes_actuator(self):
        """Test connecting passes and publishes actuator."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = ["A"]
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.actuator_status_provider = True
        wolk_device.publish_actuator_status = MagicMock()
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.keep_alive_service_enabled = False

        wolk_device.connectivity_service.is_connected = MagicMock()
        wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        wolk_device.connectivity_service.connect = MagicMock(return_value=True)
        wolk_device.connect()
        wolk_device.publish_actuator_status.assert_called_once_with(
            actuator_references[0]
        )

    def test_connect_publishes_configuration(self):
        """Test connecting passes and publishes configuration."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.configuration_provider = True
        wolk_device.publish_configuration = MagicMock()
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.keep_alive_service_enabled = False

        wolk_device.connectivity_service.is_connected = MagicMock()
        wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        wolk_device.connectivity_service.connect = MagicMock(return_value=True)
        wolk_device.connect()
        wolk_device.publish_configuration.assert_called_once()

    def test_connect_publish_file_list_fails(self):
        """Test connecting passes and fails to publishes file list."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        file_directory = "files"
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        wolk_device.file_management.get_file_list = MagicMock(return_value=[])
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_queue.put = MagicMock()
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.keep_alive_service_enabled = False

        wolk_device.connectivity_service.is_connected = MagicMock()
        wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        wolk_device.connectivity_service.connect = MagicMock(return_value=True)
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.connect()
        wolk_device.message_queue.put.assert_called_once()
        os.rmdir(file_directory)

    def test_connect_publish_file_list(self):
        """Test connecting passes and publishes file list."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        file_directory = "files"
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        wolk_device.file_management.get_file_list = MagicMock(return_value=[])
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.keep_alive_service_enabled = False

        wolk_device.connectivity_service.is_connected = MagicMock()
        wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        wolk_device.connectivity_service.connect = MagicMock(return_value=True)
        wolk_device.connect()
        wolk_device.message_queue.put.assert_not_called()
        os.rmdir(file_directory)

    def test_connect_publish_firmware_version_fails(self):
        """Test connecting passes and firmware version fails to send."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        file_directory = "files"
        device = Device(device_key, device_password, actuator_references)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")

        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        wolk_device.with_firmware_update(firmware_handler)
        wolk_device.file_management = None
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_queue.put = MagicMock()
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.keep_alive_service_enabled = False

        wolk_device.connectivity_service.is_connected = MagicMock()
        wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        wolk_device.connectivity_service.connect = MagicMock(return_value=True)
        wolk_device.connect()
        wolk_device.message_queue.put.assert_called_once()
        os.rmdir(file_directory)

    def test_connect_publish_firmware_version_passes(self):
        """Test connecting passes and firmware version is sent."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        file_directory = "files"
        device = Device(device_key, device_password, actuator_references)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")

        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        wolk_device.with_firmware_update(firmware_handler)
        wolk_device.file_management = None
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.keep_alive_service_enabled = False

        wolk_device.connectivity_service.is_connected = MagicMock()
        wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        wolk_device.connectivity_service.connect = MagicMock(return_value=True)
        wolk_device.connect()
        wolk_device.message_queue.put.assert_not_called()
        os.rmdir(file_directory)

    def test_connect_keep_alive_enabled(self):
        """Test connecting with enabled keep alive service."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)

        wolk_device = WolkConnect(device)
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()
        wolk_device.logger.setLevel(logging.CRITICAL)

        wolk_device.connectivity_service.is_connected = MagicMock()
        wolk_device.connectivity_service.is_connected.side_effect = [
            False,
            True,
        ]
        wolk_device.connectivity_service.connect = MagicMock(return_value=True)
        wolk_device._send_keep_alive = MagicMock()
        wolk_device.connect()
        wolk_device._send_keep_alive.assert_called_once()
        wolk_device.keep_alive_service.cancel()

    def test_disconnect_not_connected(self):
        """Test calling disconnect when not connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.logger.debug = MagicMock()
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        wolk_device.disconnect()
        wolk_device.logger.debug.assert_not_called()

    def test_disconnect_when_connected(self):
        """Test calling disconnect when connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.logger.debug = MagicMock()
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.disconnect = MagicMock()
        wolk_device.disconnect()
        wolk_device.logger.debug.assert_called_once()

    def test_disconnect_when_connected_stops_keep_alive(self):
        """Test calling disconnect when connected stops keep alive service."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.disconnect = MagicMock()
        wolk_device.keep_alive_service = device
        wolk_device.keep_alive_service.cancel = MagicMock()
        wolk_device.disconnect()
        wolk_device.keep_alive_service.cancel.assert_called_once()

    def test_add_sensor_reading(self):
        """Test adding sensor reading to message queue."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.message_queue.put = MagicMock()
        wolk_device.add_sensor_reading("R", 1)
        wolk_device.message_queue.put.assert_called_once()

    def test_add_sensor_reading_historical(self):
        """Test adding sensor reading to message queue."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.message_queue.put = MagicMock()
        wolk_device.add_sensor_reading("R", [(1, 2), (3, 4)])
        wolk_device.message_queue.put.assert_called_once()

    def test_add_sensor_readings(self):
        """Test adding sensor readings to message queue."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.message_queue.put = MagicMock()
        wolk_device.add_sensor_readings({"R": 1})
        wolk_device.message_queue.put.assert_called_once()

    def test_add_alarm(self):
        """Test adding alarm to message queue."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.message_queue.put = MagicMock()
        wolk_device.add_alarm("R", True)
        wolk_device.message_queue.put.assert_called_once()

    def test_publish_not_connected(self):
        """Test publishing when not connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.logger.warning = MagicMock()
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        wolk_device.publish()
        wolk_device.logger.warning.assert_called_once()

    def test_publish_emtpy_queue(self):
        """Test publishing when queue is empty."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.message_queue.peek = MagicMock(return_value=None)
        wolk_device.publish()
        wolk_device.message_queue.peek.assert_called_once()

    def test_publish_fail_to_publish(self):
        """Test publishing and failing to publish message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.warning = MagicMock()
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.message_queue.peek = MagicMock(return_value=True)
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.publish()
        wolk_device.logger.warning.assert_called_once()

    def test_publish_success(self):
        """Test publishing successfully."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.warning = MagicMock()
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.message_queue.peek = MagicMock()
        wolk_device.message_queue.peek.side_effect = [True, None]
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.get = MagicMock()
        wolk_device.publish()
        wolk_device.message_queue.get.assert_called_once()

    def test_publish_actuator_status_not_connected(self):
        """Test publishing actuator status when not connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.logger.warning = MagicMock()
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        wolk_device.publish_actuator_status("R")
        wolk_device.logger.warning.assert_called_once()

    def test_publish_actuator_status_no_provider(self):
        """Test publishing actuator status with no actuator status provider."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.logger.error = MagicMock()
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.publish_actuator_status("R")
        wolk_device.logger.error.assert_called_once()

    def test_publish_actuator_status_no_value(self):
        """Test publishing actuator status with no value from provider."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.logger.error = MagicMock()
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.actuator_status_provider = MagicMock(return_value=None)
        wolk_device.publish_actuator_status("R")
        wolk_device.logger.error.assert_called_once()

    def test_publish_actuator_status_no_timestamp(self):
        """Test publishing actuator status with no timestamp from provider."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        reference = "R"
        state = State.ERROR
        value = None
        actuator_status = ActuatorStatus(reference, state, value)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.actuator_status_provider = MagicMock(
            return_value=(state, value)
        )
        wolk_device.message_factory.make_from_actuator_status = MagicMock()
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)

        wolk_device.publish_actuator_status(reference)
        wolk_device.message_factory.make_from_actuator_status.assert_called_once_with(
            actuator_status
        )

    def test_publish_actuator_status_fail_to_publish(self):
        """Test publishing actuator status fails."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        reference = "R"
        state = State.ERROR
        value = None
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.actuator_status_provider = MagicMock(
            return_value=(state, value)
        )
        wolk_device.message_factory.make_from_actuator_status = MagicMock()
        wolk_device.message_queue.put = MagicMock()
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )

        wolk_device.publish_actuator_status(reference)
        wolk_device.message_queue.put.assert_called_once()

    def test_publish_configuration_not_connected(self):
        """Test publishing configuration when not connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        wolk_device.logger.warning = MagicMock()
        wolk_device.publish_configuration()
        wolk_device.logger.warning.assert_called_once()

    def test_publish_configuration_no_provider(self):
        """Test publishing configuration with no configuration provider."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.logger.error = MagicMock()
        wolk_device.publish_configuration()
        wolk_device.logger.error.assert_called_once()

    def test_publish_configuration_fail_to_publish(self):
        """Test publishing configuration fails."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.configuration_provider = MagicMock()
        wolk_device.message_factory.make_from_configuration = MagicMock()
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_queue.put = MagicMock()
        wolk_device.publish_configuration()
        wolk_device.message_queue.put.assert_called_once()

    def test_publish_configuration_publishes(self):
        """Test publishing configuration passes."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.configuration_provider = MagicMock()
        wolk_device.message_factory.make_from_configuration = MagicMock()
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()
        wolk_device.publish_configuration()
        wolk_device.message_queue.put.assert_not_called()

    def test_on_inbound_message_binary_topic(self):
        """Test on inbound message with 'binary' in topic."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("binary", "payload")
        wolk_device.logger.warning = MagicMock()

        wolk_device._on_inbound_message(message)
        wolk_device.logger.warning.assert_called_once()

    def test_on_inbound_message_unknown(self):
        """Test on inbound message for unknown message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.logger.warning = MagicMock()

        wolk_device._on_inbound_message(message)
        wolk_device.logger.warning.assert_called_once()

    def test_on_inbound_message_actuation_no_handlers(self):
        """Test on inbound actuation message but no actuation handler set."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.logger.warning = MagicMock()
        wolk_device.message_deserializer.is_actuation_command = MagicMock(
            return_value=True
        )

        wolk_device._on_inbound_message(message)
        wolk_device.logger.warning.assert_called_once()

    def test_on_inbound_message_actuation_set(self):
        """Test on inbound actuation message set message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        reference = "R"
        value = 1
        actuation_command = ActuatorCommand(reference, value)
        wolk_device.actuation_handler = MagicMock()
        wolk_device.actuator_status_provider = MagicMock()
        wolk_device.message_deserializer.parse_actuator_command = MagicMock(
            return_value=actuation_command
        )
        wolk_device.message_deserializer.is_actuation_command = MagicMock(
            return_value=True
        )
        wolk_device._on_inbound_message(message)
        wolk_device.actuation_handler.assert_called_once_with(reference, value)

    def test_on_inbound_message_configuration_no_handlers(self):
        """Test on inbound configuration message but no handler set."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.logger.warning = MagicMock()
        wolk_device.message_deserializer.is_configuration_command = MagicMock(
            return_value=True
        )
        wolk_device._on_inbound_message(message)
        wolk_device.logger.warning.assert_called_once()

    def test_on_inbound_message_configuration_set(self):
        """Test on inbound configuration message set message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        value = {"R": 1}
        configuration_command = ConfigurationCommand(value)
        wolk_device.configuration_handler = MagicMock()
        wolk_device.configuration_provider = MagicMock()
        wolk_device.message_deserializer.parse_configuration = MagicMock(
            return_value=configuration_command
        )
        wolk_device.message_deserializer.is_configuration_command = MagicMock(
            return_value=True
        )
        wolk_device._on_inbound_message(message)
        wolk_device.configuration_handler.assert_called_once_with(value)

    def test_on_inbound_message_keep_alive_response(self):
        """Test on inbound keep alive response message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        timestamp = 1

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.parse_keep_alive_response = MagicMock(
            return_value=timestamp
        )
        wolk_device.message_deserializer.is_keep_alive_response = MagicMock(
            return_value=True
        )
        wolk_device._on_inbound_message(message)
        self.assertEqual(timestamp, wolk_device.last_platform_timestamp)

    def test_on_inbound_message_file_management_message(self):
        """Test on inbound file management message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device._on_file_management_message = MagicMock()
        wolk_device.message_deserializer.is_file_delete_command = MagicMock(
            return_value=True
        )
        wolk_device._on_inbound_message(message)
        wolk_device._on_file_management_message.assert_called_once()

    def test_on_inbound_message_firmware_message(self):
        """Test on inbound firmware message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device._on_firmware_message = MagicMock()
        wolk_device.message_deserializer.is_firmware_install = MagicMock(
            return_value=True
        )
        wolk_device._on_inbound_message(message)
        wolk_device._on_firmware_message.assert_called_once()

    def test_on_file_management_message_no_module_fail_to_send(self):
        """Test on file management message with no module."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_factory.make_from_file_management_status = (
            MagicMock()
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_management_message(message)
        wolk_device.message_queue.put.assert_called_once()

    def test_on_file_management_message_no_module_sends_error(self):
        """Test on file management message with no module, sends message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_factory.make_from_file_management_status = (
            MagicMock()
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_management_message(message)
        wolk_device.message_queue.put.assert_not_called()

    def test_on_file_management_message_invalid_file_upload_init(self):
        """Test on file management message - invalid file upload initiate."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_upload_initiate = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_file_initiate = MagicMock(
            return_value=("", 0, b"")
        )
        wolk_device.file_management.handle_upload_initiation = MagicMock()
        wolk_device._on_file_management_message(message)
        wolk_device.file_management.handle_upload_initiation.assert_not_called()

    def test_on_file_management_message_file_upload_init(self):
        """Test on file management message file upload initiate."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_upload_initiate = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_file_initiate = MagicMock(
            return_value=("file", 0, b"")
        )
        wolk_device.file_management.handle_upload_initiation = MagicMock()
        wolk_device._on_file_management_message(message)
        wolk_device.file_management.handle_upload_initiation.assert_called_once_with(
            "file", 0, b""
        )

    def test_on_file_management_message_file_binary_response(self):
        """Test on file management message file binary response."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_binary_response = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_file_binary = MagicMock(
            return_value=True
        )
        wolk_device.file_management.handle_file_binary_response = MagicMock()
        wolk_device._on_file_management_message(message)
        wolk_device.file_management.handle_file_binary_response.assert_called_once_with(
            True
        )

    def test_on_file_management_message_file_upload_abort(self):
        """Test on file management message file upload abort."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_upload_abort = MagicMock(
            return_value=True
        )
        wolk_device.file_management.handle_file_upload_abort = MagicMock()
        wolk_device._on_file_management_message(message)
        wolk_device.file_management.handle_file_upload_abort.assert_called_once()

    def test_on_file_management_message_file_url_abort(self):
        """Test on file management message file url abort."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_url_abort = MagicMock(
            return_value=True
        )
        wolk_device.file_management.handle_file_upload_abort = MagicMock()
        wolk_device._on_file_management_message(message)
        wolk_device.file_management.handle_file_upload_abort.assert_called_once()

    def test_on_file_management_message_invalid_file_url_init(self):
        """Test on file management message - invalid file url initiate."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_url_initiate = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_file_url = MagicMock(
            return_value=""
        )
        wolk_device.file_management.handle_url_initiation = MagicMock()
        wolk_device._on_file_management_message(message)
        wolk_device.file_management.handle_url_initiation.assert_not_called()

    def test_on_file_management_message_file_url_init(self):
        """Test on file management message file url initiate."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_url_initiate = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_file_url = MagicMock(
            return_value="url"
        )
        wolk_device.file_management.handle_file_url_download_initiation = (
            MagicMock()
        )
        wolk_device._on_file_management_message(message)
        wolk_device.file_management.handle_file_url_download_initiation.assert_called_once_with(
            "url"
        )

    def test_on_file_management_message_file_list_request_fail_to_publish(
        self,
    ):
        """Test on file list request fails to publish and puts in queue."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_list_request = MagicMock(
            return_value=True
        )
        wolk_device.file_management.get_file_list = MagicMock(return_value=[])
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_management_message(message)

        wolk_device.message_queue.put.assert_called_once()

    def test_on_file_management_message_file_list_request_publishes(self):
        """Test on file list request fails to publish and puts in queue."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_list_request = MagicMock(
            return_value=True
        )
        wolk_device.file_management.get_file_list = MagicMock(return_value=[])
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_management_message(message)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_file_management_message_file_delete_invalid_name(self):
        """Test receiving invalid file delete command."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_delete_command = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_file_delete_command = MagicMock(
            return_value=""
        )
        wolk_device.file_management.handle_file_delete = MagicMock()

        wolk_device._on_file_management_message(message)

        wolk_device.file_management.handle_file_delete.assert_not_called()

    def test_on_file_management_message_file_delete_fail_to_publish(self):
        """Test receiving file delete command and fail to publish file list."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_delete_command = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_file_delete_command = MagicMock(
            return_value="file"
        )
        wolk_device.file_management.handle_file_delete = MagicMock()
        wolk_device.file_management.get_file_list = MagicMock(return_value=[])
        wolk_device.message_factory.make_from_file_list_update = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_management_message(message)

        wolk_device.message_queue.put.assert_called_once()

    def test_on_file_management_message_file_delete_publishes(self):
        """Test receiving file delete command and send file list."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_delete_command = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_file_delete_command = MagicMock(
            return_value="file"
        )
        wolk_device.file_management.handle_file_delete = MagicMock()
        wolk_device.file_management.get_file_list = MagicMock(return_value=[])
        wolk_device.message_factory.make_from_file_list_update = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_management_message(message)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_file_management_message_file_purge_fail_to_publish(self):
        """Test receiving file purge command and fail to publish file list."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_purge_command = MagicMock(
            return_value=True
        )
        wolk_device.file_management.handle_file_purge = MagicMock()
        wolk_device.file_management.get_file_list = MagicMock(return_value=[])
        wolk_device.message_factory.make_from_file_list_update = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_management_message(message)

        wolk_device.message_queue.put.assert_called_once()

    def test_on_file_management_message_file_purge_publishes(self):
        """Test receiving file purge command and send file list."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_purge_command = MagicMock(
            return_value=True
        )
        wolk_device.file_management.handle_file_purge = MagicMock()
        wolk_device.file_management.get_file_list = MagicMock(return_value=[])
        wolk_device.message_factory.make_from_file_list_update = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_management_message(message)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_file_management_message_file_list_confirm(self):
        """Test receiving file list confirm message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_file_list_confirm = MagicMock(
            return_value=True
        )
        wolk_device.file_management.handle_file_list_confirm = MagicMock()

        wolk_device._on_file_management_message(message)

        wolk_device.file_management.handle_file_list_confirm.assert_called_once()

    def test_on_file_management_message_unkown(self):
        """Test receiving unknown file management message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic", "payload")
        wolk_device.logger.warning = MagicMock()

        wolk_device._on_file_management_message(message)

        wolk_device.logger.warning.assert_called_once()

    def test_on_firmware_message_no_module_fail_to_publish(self):
        """Test receiving firmware message with no module and fail to publish."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        message = Message("some_topic", "payload")

        wolk_device.message_queue.put = MagicMock()
        wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )

        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device._on_firmware_message(message)
        wolk_device.message_queue.put.assert_called_once()

    def test_on_firmware_message_no_module_fail_publishes(self):
        """Test receiving firmware message with no module and fail to publish."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        message = Message("some_topic", "payload")
        wolk_device.logger.warning = MagicMock()

        wolk_device.message_queue.put = MagicMock()
        wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )

        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device._on_firmware_message(message)
        wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_message_firmware_install_no_path_fail_to_publish(
        self,
    ):
        """Test install command non-present file and fail to publish status."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)
        wolk_device.logger.setLevel(logging.CRITICAL)
        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_firmware_install = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_firmware_install = MagicMock(
            return_value=None
        )
        wolk_device.file_management.get_file_path = MagicMock(
            return_value=None
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_firmware_message(message)

        wolk_device.message_queue.put.assert_called_once()

    def test_on_firmware_message_firmware_install_no_path_publishes(
        self,
    ):
        """Test install command non-present file and publishes status."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)
        wolk_device.logger.setLevel(logging.CRITICAL)
        message = Message("some_topic", "payload")
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_deserializer.is_firmware_install = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_firmware_install = MagicMock(
            return_value=None
        )
        wolk_device.file_management.get_file_path = MagicMock(
            return_value=None
        )
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_firmware_message(message)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_message_firmware_install_with_path_calls_intsall(
        self,
    ):
        """Test install command present file calls handle install."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)
        wolk_device.logger.setLevel(logging.CRITICAL)
        message = Message("some_topic", "payload")
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_deserializer.is_firmware_install = MagicMock(
            return_value=True
        )
        wolk_device.message_deserializer.parse_firmware_install = MagicMock(
            return_value=None
        )
        wolk_device.file_management.get_file_path = MagicMock(
            return_value="file"
        )
        wolk_device.firmware_update.handle_install = MagicMock()
        wolk_device._on_firmware_message(message)

        wolk_device.firmware_update.handle_install.assert_called_once_with(
            "file"
        )

    def test_on_firmware_message_firmware_abort(self):
        """Test abort command calls handle abort."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)
        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_firmware_abort = MagicMock(
            return_value=True
        )
        wolk_device.firmware_update.handle_abort = MagicMock()
        wolk_device._on_firmware_message(message)

        wolk_device.firmware_update.handle_abort.assert_called_once_with()

    def test_on_firmware_message_firmware_version_request_pulishes(self):
        """Test receiving version request and publishes response."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)
        message = Message("some_topic", "payload")
        wolk_device.message_deserializer.is_firmware_version_request = (
            MagicMock(return_value=True)
        )
        wolk_device.message_factory.make_from_firmware_version_response = (
            MagicMock(return_value="1.0")
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_firmware_message(message)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_message_unknown(
        self,
    ):
        """Test receiving unknown firmware message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)
        message = Message("some_topic", "payload")
        wolk_device.logger.warning = MagicMock()

        wolk_device._on_firmware_message(message)

        wolk_device.logger.warning.assert_called_once()

    def test_on_package_request_fails_to_publish(self):
        """Test making package request and failing to send it."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.message_factory.make_from_package_request = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_package_request("file", 0, 64)

        wolk_device.message_queue.put.assert_called_once()

    def test_on_package_request_publishes(self):
        """Test making package request and publishing it."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        wolk_device.message_factory.make_from_package_request = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_package_request("file", 0, 64)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_update_status_not_connected(self):
        """Test on firmware update status call when not connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.INSTALLING)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        wolk_device.connectivity_service.publish = MagicMock()
        wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        wolk_device._on_firmware_update_status(status)

        wolk_device.connectivity_service.publish.assert_not_called()

    def test_on_firmware_update_status_fail_to_publish(self):
        """Test on firmware update status and fail to publish."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.INSTALLING)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        wolk_device.message_queue.put = MagicMock()
        wolk_device._on_firmware_update_status(status)

        wolk_device.message_queue.put.assert_called_once()

    def test_on_firmware_update_status_publishes(self):
        """Test on firmware update status and publishes the message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.INSTALLING)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        wolk_device.message_queue.put = MagicMock()
        wolk_device._on_firmware_update_status(status)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_firmware_update_status_completed_not_connected(self):
        """Test on firmware status completed and not connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.COMPLETED)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        wolk_device.connectivity_service.publish = MagicMock()
        wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        wolk_device.message_factory.make_from_firmware_version_update = (
            MagicMock(return_value=True)
        )
        wolk_device._on_firmware_update_status(status)

        wolk_device.connectivity_service.publish.assert_not_called()

    def test_on_firmware_update_status_completed_fail_to_publish(self):
        """Test on firmware status completed and fail to publish."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.COMPLETED)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        wolk_device.message_factory.make_from_firmware_version_update = (
            MagicMock(return_value=True)
        )
        wolk_device.message_queue.put = MagicMock()
        wolk_device._on_firmware_update_status(status)

        self.assertEqual(2, wolk_device.message_queue.put.call_count)

    def test_on_firmware_update_status_completed_publishes(self):
        """Test on firmware status completed and publishes message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)
        firmware_handler = self.MockFirmwareHandler()
        firmware_handler.get_current_version = MagicMock(return_value="1.0")
        wolk_device.with_firmware_update(firmware_handler)

        status = FirmwareUpdateStatus(FirmwareUpdateStatusType.COMPLETED)
        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_factory.make_from_firmware_update_status = (
            MagicMock(return_value=True)
        )
        wolk_device.message_factory.make_from_firmware_version_update = (
            MagicMock(return_value=True)
        )
        wolk_device.message_queue.put = MagicMock()
        wolk_device._on_firmware_update_status(status)
        wolk_device.message_queue.put.assert_not_called()

    def test_on_file_upload_status_fail_to_publish(self):
        """Test on file upload status and fail to publish message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)

        wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_TRANSFER)
        file_name = "file"
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_upload_status(file_name, status)

        wolk_device.message_queue.put.assert_called_once()

    def test_on_file_upload_status_publishes(self):
        """Test on file upload status and publishes message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)

        wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        status = FileManagementStatus(FileManagementStatusType.FILE_TRANSFER)
        file_name = "file"
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_upload_status(file_name, status)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_file_upload_status_file_ready_fail_to_publish(self):
        """Test on file upload status and fail to publish message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)

        wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_factory.make_from_file_list_update = MagicMock(
            return_value=True
        )
        wolk_device.file_management.get_file_list = MagicMock()
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        file_name = "file"
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_upload_status(file_name, status)

        self.assertEqual(2, wolk_device.message_queue.put.call_count)

    def test_on_file_upload_status_file_ready_published(self):
        """Test on file upload status and publishes message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)

        wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_factory.make_from_file_list_update = MagicMock(
            return_value=True
        )
        wolk_device.file_management.get_file_list = MagicMock()
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        file_name = "file"
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_upload_status(file_name, status)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_file_url_status_fail_to_publish(self):
        """Test on file url status and fail to publish update."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)

        wolk_device.message_factory.make_from_file_url_status = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        status = FileManagementStatus(FileManagementStatusType.FILE_TRANSFER)
        file_url = "file_url"
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_url_status(file_url, status)

        wolk_device.message_queue.put.assert_called_once()

    def test_on_file_url_status_publishes(self):
        """Test on file url status and publishes update."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)

        wolk_device.message_factory.make_from_file_url_status = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        status = FileManagementStatus(FileManagementStatusType.FILE_TRANSFER)
        file_url = "file_url"
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_url_status(file_url, status)

        wolk_device.message_queue.put.assert_not_called()

    def test_on_file_url_status_with_file_name_fail_to_publish(self):
        """Test on url upload status and fail to publish message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)

        wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        wolk_device.connectivity_service.publish = MagicMock(
            return_value=False
        )
        wolk_device.message_factory.make_from_file_url_status = MagicMock(
            return_value=True
        )
        wolk_device.file_management.get_file_list = MagicMock()
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        file_name = "file"
        file_url = "file_url"
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_url_status(file_url, status, file_name)

        self.assertEqual(2, wolk_device.message_queue.put.call_count)

    def test_on_file_url_status_with_file_name_publishes(self):
        """Test on url upload status and publishes message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        file_directory = "files"
        wolk_device = WolkConnect(device).with_file_management(
            256, 1024, file_directory
        )
        os.rmdir(file_directory)

        wolk_device.message_factory.make_from_file_management_status = (
            MagicMock(return_value=True)
        )
        wolk_device.connectivity_service.publish = MagicMock(return_value=True)
        wolk_device.message_factory.make_from_file_url_status = MagicMock(
            return_value=True
        )
        wolk_device.file_management.get_file_list = MagicMock()
        status = FileManagementStatus(FileManagementStatusType.FILE_READY)
        file_name = "file"
        file_url = "file_url"
        wolk_device.message_queue.put = MagicMock()

        wolk_device._on_file_url_status(file_url, status, file_name)

        wolk_device.message_queue.put.assert_not_called()

    def test_keep_alive_service_disabled(self):
        """Test keep alive service is disabled."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)

        wolk_device = WolkConnect(device).with_keep_alive_service(False)

        self.assertFalse(wolk_device.keep_alive_service_enabled)
        self.assertIsNone(wolk_device.keep_alive_service)

    def test_keep_alive_service_custom_interval(self):
        """Test on url upload status and publishes message.."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        interval = 15

        wolk_device = WolkConnect(device).with_keep_alive_service(
            True, interval
        )

        self.assertTrue(wolk_device.keep_alive_service_enabled)
        self.assertEqual(interval, wolk_device.keep_alive_interval)

    def test_send_keep_alive_not_connected(self):
        """Test seding keep alive message when not connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=False
        )
        wolk_device.message_factory.make_keep_alive_message = MagicMock()

        wolk_device._send_keep_alive()

        wolk_device.message_factory.make_keep_alive_message.assert_not_called()

    def test_send_keep_alive_connected(self):
        """Test seding keep alive message when connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)

        wolk_device.connectivity_service.is_connected = MagicMock(
            return_value=True
        )
        wolk_device.connectivity_service.publish = MagicMock()

        wolk_device._send_keep_alive()

        wolk_device.connectivity_service.publish.assert_called_once()

    def test_request_timestamp_when_none(self):
        """Test request timestamp returns none."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)

        self.assertIsNone(wolk_device.request_timestamp())

    def test_request_timestamp_when_not_none(self):
        """Test request timestamp returns value."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        wolk_device = WolkConnect(device)
        wolk_device.logger.setLevel(logging.CRITICAL)
        wolk_device.last_platform_timestamp = 1

        self.assertIsNotNone(wolk_device.request_timestamp())
