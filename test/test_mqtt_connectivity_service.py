"""Tests for MQTTConnectivityService."""
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

from paho.mqtt import client as mqtt

sys.path.append("..")  # noqa

from wolk.model.device import Device
from wolk.model.message import Message
from wolk.mqtt_connectivity_service import MQTTConnectivityService


class MQTTConnectivityServiceTests(unittest.TestCase):
    """Tests for MQTT Connectivity Service."""

    def test_is_connected(self):
        """Test is connected method."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        self.assertFalse(mqtt_cs.is_connected())

    def test_set_inbound_message_listener(self):
        """Test setting inbound message listener."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        def listener():
            raise NotImplementedError

        mqtt_cs.set_inbound_message_listener(listener)

        self.assertEqual(listener, mqtt_cs.inbound_message_listener)

    def test_on_mqtt_message_no_message(self):
        """Test on mqtt message with no message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.inbound_message_listener = MagicMock()

        mqtt_cs.on_mqtt_message(None, None, None)
        mqtt_cs.inbound_message_listener.assert_not_called()

    def test_on_mqtt_message_binary_message(self):
        """Test on mqtt message with file chunk message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.inbound_message_listener = MagicMock()

        message = Message("binary", b"")
        mqtt_cs.on_mqtt_message(None, None, message)
        mqtt_cs.inbound_message_listener.assert_called_once_with(message)

    def test_on_mqtt_message_ordinary_message(self):
        """Test on mqtt message with ordinary message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.inbound_message_listener = MagicMock()
        message = Message("some_topic", "payload")
        mqtt_cs.on_mqtt_message(None, None, message)
        mqtt_cs.inbound_message_listener.assert_called_once_with(message)

    def test_on_mqtt_connect_rc_0_without_topics(self):
        """Test on mqtt connect with return code 0 without topics."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        mqtt_cs.client.subscribe = MagicMock()
        mqtt_cs.on_mqtt_connect(None, None, None, 0)
        mqtt_cs.client.subscribe.assert_not_called()

    def test_on_mqtt_connect_rc_0_with_topics(self):
        """Test on mqtt connect with return code 0 with topics."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = [1, 2, 3]
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        mqtt_cs.client.subscribe = MagicMock()

        mqtt_cs.on_mqtt_connect(None, None, None, 0)

        self.assertEqual(3, mqtt_cs.client.subscribe.call_count)

    def test_on_mqtt_connect_rc_1(self):
        """Test on mqtt connect with return code 1."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        mqtt_cs.on_mqtt_connect(None, None, None, 1)

        self.assertEqual(1, mqtt_cs.connected_rc)

    def test_on_mqtt_connect_rc_2(self):
        """Test on mqtt connect with return code 2."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        mqtt_cs.on_mqtt_connect(None, None, None, 2)

        self.assertEqual(2, mqtt_cs.connected_rc)

    def test_on_mqtt_connect_rc_3(self):
        """Test on mqtt connect with return code 3."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        mqtt_cs.on_mqtt_connect(None, None, None, 3)

        self.assertEqual(3, mqtt_cs.connected_rc)

    def test_on_mqtt_connect_rc_4(self):
        """Test on mqtt connect with return code 4."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        mqtt_cs.on_mqtt_connect(None, None, None, 4)

        self.assertEqual(4, mqtt_cs.connected_rc)

    def test_on_mqtt_connect_rc_5(self):
        """Test on mqtt connect with return code 5."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        mqtt_cs.on_mqtt_connect(None, None, None, 5)

        self.assertEqual(5, mqtt_cs.connected_rc)

    def test_on_mqtt_connect_rc_6(self):
        """Test on mqtt connect with invalid return code 6."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)

        mqtt_cs.on_mqtt_connect(None, None, None, 6)

        self.assertEqual(None, mqtt_cs.connected_rc)

    def test_on_mqtt_disconnect_expected(self):
        """Test on mqtt disconnect with return code 0."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.connect = MagicMock()

        mqtt_cs.on_mqtt_disconnect(None, None, 0)

        mqtt_cs.connect.assert_not_called()

    def test_on_mqtt_disconnect_unexpected(self):
        """Test on mqtt disconnect with return code not 0."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        mqtt_cs.connect = MagicMock()

        mqtt_cs.on_mqtt_disconnect(None, None, 1)

        mqtt_cs.connect.assert_called_once()

    def test_connect_already_connected(self):
        """Test calling connect when already connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.connected = True

        self.assertTrue(mqtt_cs.connect())

    def test_connect_bad_ca_cert(self):
        """Test calling connect with bad ca_cert."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.ca_cert = "some_certificate"
        mqtt_cs.logger.setLevel(logging.CRITICAL)

        self.assertFalse(mqtt_cs.connect())

    def test_connect_good_ca_cert(self):
        """Test calling connect with good ca_cert."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.warning = MagicMock()
        path_to_wolk = (
            os.path.dirname(__file__) + os.sep + ".." + os.sep + "wolk"
        )
        mqtt_cs.ca_cert = os.path.join(path_to_wolk, "ca.crt")
        mqtt_cs.on_mqtt_disconnect = MagicMock()

        self.assertFalse(mqtt_cs.connect())

    def test_connect_bad_host(self):
        """Test calling connect with bad host."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(
            device, topics, last_will_message, host="bad_host"
        )
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        path_to_wolk = (
            os.path.dirname(__file__) + os.sep + ".." + os.sep + "wolk"
        )
        mqtt_cs.ca_cert = os.path.join(path_to_wolk, "ca.crt")
        mqtt_cs.on_mqtt_disconnect = MagicMock()

        self.assertFalse(mqtt_cs.connect())

    def test_connect_timeout(self):
        """Test connect with timeout."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        mqtt_cs.on_mqtt_disconnect = MagicMock()
        mqtt_cs.client.connect = MagicMock()
        mqtt_cs.logger.warning = MagicMock()
        mqtt_cs.timeout_interval = -1
        mqtt_cs.client.subscribe = MagicMock()

        mqtt_cs.connect()
        mqtt_cs.logger.warning.assert_called_once()

    def test_connect_rc_0_with_topics(self):
        """Test connect with timeout."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = [1, 2, 3]
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        path_to_wolk = (
            os.path.dirname(__file__) + os.sep + ".." + os.sep + "wolk"
        )
        mqtt_cs.ca_cert = os.path.join(path_to_wolk, "ca.crt")
        mqtt_cs.on_mqtt_disconnect = MagicMock()
        mqtt_cs.client.connect = MagicMock()
        mqtt_cs.logger.warning = MagicMock()
        mqtt_cs.connected_rc = 0
        mqtt_cs.client.subscribe = MagicMock()
        mqtt_cs.connect()

        self.assertEqual(3, mqtt_cs.client.subscribe.call_count)

    def test_connect_rc_1(self):
        """Test connect with return code 1."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        path_to_wolk = (
            os.path.dirname(__file__) + os.sep + ".." + os.sep + "wolk"
        )
        mqtt_cs.ca_cert = os.path.join(path_to_wolk, "ca.crt")
        mqtt_cs.on_mqtt_disconnect = MagicMock()
        mqtt_cs.client.connect = MagicMock()
        mqtt_cs.logger.warning = MagicMock()
        mqtt_cs.connected_rc = 1
        mqtt_cs.connect()

        mqtt_cs.logger.warning.assert_called_once()

    def test_connect_rc_2(self):
        """Test connect with return code 2."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        path_to_wolk = (
            os.path.dirname(__file__) + os.sep + ".." + os.sep + "wolk"
        )
        mqtt_cs.ca_cert = os.path.join(path_to_wolk, "ca.crt")
        mqtt_cs.on_mqtt_disconnect = MagicMock()
        mqtt_cs.client.connect = MagicMock()
        mqtt_cs.logger.warning = MagicMock()
        mqtt_cs.connected_rc = 2
        mqtt_cs.connect()

        mqtt_cs.logger.warning.assert_called_once()

    def test_connect_rc_3(self):
        """Test connect with return code 3."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        path_to_wolk = (
            os.path.dirname(__file__) + os.sep + ".." + os.sep + "wolk"
        )
        mqtt_cs.ca_cert = os.path.join(path_to_wolk, "ca.crt")
        mqtt_cs.on_mqtt_disconnect = MagicMock()
        mqtt_cs.client.connect = MagicMock()
        mqtt_cs.logger.warning = MagicMock()
        mqtt_cs.connected_rc = 3
        mqtt_cs.connect()

        mqtt_cs.logger.warning.assert_called_once()

    def test_connect_rc_4(self):
        """Test connect with return code 4."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        path_to_wolk = (
            os.path.dirname(__file__) + os.sep + ".." + os.sep + "wolk"
        )
        mqtt_cs.ca_cert = os.path.join(path_to_wolk, "ca.crt")
        mqtt_cs.on_mqtt_disconnect = MagicMock()
        mqtt_cs.client.connect = MagicMock()
        mqtt_cs.logger.warning = MagicMock()
        mqtt_cs.connected_rc = 4
        mqtt_cs.connect()

        mqtt_cs.logger.warning.assert_called_once()

    def test_connect_rc_5(self):
        """Test connect with return code 5."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        path_to_wolk = (
            os.path.dirname(__file__) + os.sep + ".." + os.sep + "wolk"
        )
        mqtt_cs.ca_cert = os.path.join(path_to_wolk, "ca.crt")
        mqtt_cs.on_mqtt_disconnect = MagicMock()
        mqtt_cs.client.connect = MagicMock()
        mqtt_cs.logger.warning = MagicMock()
        mqtt_cs.connected_rc = 5
        mqtt_cs.connect()

        mqtt_cs.logger.warning.assert_called_once()

    def test_connect_rc_9_invalid(self):
        """Test connect with invalid return code 9."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        path_to_wolk = (
            os.path.dirname(__file__) + os.sep + ".." + os.sep + "wolk"
        )
        mqtt_cs.ca_cert = os.path.join(path_to_wolk, "ca.crt")
        mqtt_cs.on_mqtt_disconnect = MagicMock()
        mqtt_cs.client.connect = MagicMock()
        mqtt_cs.logger.warning = MagicMock()
        mqtt_cs.connected_rc = 9
        mqtt_cs.connect()

        mqtt_cs.logger.warning.assert_called_once()

    def test_disconnect(self):
        """Test disconnect."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)
        mqtt_cs.logger.debug = MagicMock()

        mqtt_cs.disconnect()
        mqtt_cs.logger.debug.assert_called_once()

    def test_publish_no_message(self):
        """Test publish with no message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)

        message = None
        self.assertFalse(mqtt_cs.publish(message))

    def test_publish_not_connected(self):
        """Test publish when not connected."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)

        message = Message("some_topic")
        self.assertFalse(mqtt_cs.publish(message))

    def test_publish_return_code_success(self):
        """Test publish with return code success."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)

        mqtt_cs.connected = True
        message_info = mqtt.MQTTMessageInfo(1)
        mqtt_cs.client.publish = MagicMock(return_value=message_info)

        message = Message("some_topic")
        self.assertTrue(mqtt_cs.publish(message))

    def test_publish_is_published(self):
        """Test publish with is published method."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)

        mqtt_cs.connected = True
        message_info = mqtt.MQTTMessageInfo(1)
        message_info.rc = 10
        message_info._published = True
        mqtt_cs.client.publish = MagicMock(return_value=message_info)

        message = Message("some_topic")
        self.assertTrue(mqtt_cs.publish(message))

    def test_publish_fail_to_publish(self):
        """Test publish failing to publish message."""
        device_key = "some_key"
        device_password = "some_password"
        actuator_references = []
        device = Device(device_key, device_password, actuator_references)
        last_will_message = Message("last_will")
        topics = []
        mqtt_cs = MQTTConnectivityService(device, topics, last_will_message)
        mqtt_cs.logger.setLevel(logging.CRITICAL)

        mqtt_cs.connected = True
        message_info = mqtt.MQTTMessageInfo(1)
        message_info.rc = 10
        mqtt_cs.client.publish = MagicMock(return_value=message_info)

        message = Message("some_topic")
        self.assertFalse(mqtt_cs.publish(message))
