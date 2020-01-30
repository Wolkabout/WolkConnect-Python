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

from wolk.model.actuator_state import ActuatorState
from wolk.model.actuator_status import ActuatorStatus
from wolk.model.alarm import Alarm
from wolk.model.message import Message
from wolk.model.sensor_reading import SensorReading
from wolk.wolkabout_protocol_message_factory import (
    WolkAboutProtocolMessageFactory as WAPMF,
)

sys.path.append("..")  # noqa


class WolkAboutProtocolMessageFactoryTests(unittest.TestCase):
    """Tests for serializing messages using WolkAbout Protocol."""

    def test_init(self):
        """Test that object is created with correct device key."""
        device_key = "some_key"

        factory = WAPMF(device_key)

        self.assertEqual(device_key, factory.device_key)

    def test_sensor_bool(self):
        """Test that valid message is created for bool sensor reading."""
        # Set up
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
        # Set up
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "SNL"
        value = "string\nin\na\ncouple\nof\nrows"
        expected_value = value.replace("\n", "\\n")

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
        # Set up
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
        # Set up
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
        # Set up
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "MVF"
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
        # Set up
        device_key = "some_key"
        factory = WAPMF(device_key)
        reference = "MVF"
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
