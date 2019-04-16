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

from abc import ABC, abstractmethod

"""
OutboundMessageFactory Module.
"""


class OutboundMessageFactory(ABC):
    """Serialize messages to be sent to WolkAbout IoT Platform."""

    @abstractmethod
    def make_from_sensor_reading(self, reading):
        """
        Serialize a sensor reading to be sent to WolkAbout IoT Platform.

        :param reading: Reading to be serialized
        :type reading: wolk.models.SensorReading.SensorReading
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    @abstractmethod
    def make_from_alarm(self, alarm):
        """
        Serialize an alarm event to be sent to WolkAbout IoT Platform.

        :param alarm: Alarm to be serialized
        :type alarm: wolk.models.Alarm.Alarm
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    @abstractmethod
    def make_from_actuator_status(self, actuator):
        """
        Serialize an actuator status to be sent to WolkAbout IoT Platform.

        :param actuator: Actuator status to be serialized
        :type actuator: wolk.models.ActuatorStatus.ActuatorStatus
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    @abstractmethod
    def make_from_firmware_status(self, firmware_status):
        """
        Report the current status of the firmware update process.

        :param firmware_status: Current status of the firmware update process
        :type firmware_status: wolk.models.FirmwareStatus.FirmwareStatus
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    @abstractmethod
    def make_from_chunk_request(self, file_name, chunk_index, chunk_size):
        """
        Request a chunk of the firmware file from WolkAbout IoT Platform.

        :param file_name: Name of the file that contains the requested chunk
        :type file_name: str
        :param chunk_index: Index of the requested chunk
        :type chunk_index: int
        :param chunk_size: Size of the requested chunk
        :type chunk_size: int
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    @abstractmethod
    def make_from_firmware_version(self, version):
        """
        Report the current firmware version to WolkAbout IoT Platform.

        :param version: Current firmware version
        :type version: str
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    @abstractmethod
    def make_from_keep_alive_message(self):
        """
        Make a ping message to be sent to WolkAbout IoT Platform.

        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    @abstractmethod
    def make_from_configuration(self, configuration):
        """
        Serialize device's configuration to be sent to WolkAbout IoT Platform.

        :param configuration: Device's current configuration
        :type configuration: dict
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass
