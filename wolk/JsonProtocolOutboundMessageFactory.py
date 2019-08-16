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

"""JsonProtocolOutboundMessageFactory Module."""

from wolk.models.ActuatorState import ActuatorState
from wolk.models.FirmwareErrorType import FirmwareErrorType
from wolk.models.FirmwareStatusType import FirmwareStatusType
from wolk.models.OutboundMessage import OutboundMessage
from wolk.interfaces.OutboundMessageFactory import OutboundMessageFactory
from wolk import LoggerFactory


class JsonProtocolOutboundMessageFactory(OutboundMessageFactory):
    """
    Serialize messages to be sent to WolkAbout IoT Platform.

    :ivar device_key: Device key to use when serializing messages
    :vartype device_key: str
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    """

    def __init__(self, device_key):
        """
        Create a factory for serializing messages.

        :param device_key: Device key to use when serializing messages
        :type device_key: str
        """
        self.device_key = device_key
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug("Init - Device key: %s", device_key)

    def make_from_sensor_reading(self, reading):
        """
        Serialize the sensor reading to be sent to WolkAbout IoT Platform.

        :param reading: Sensor reading to be serialized
        :type reading: wolk.models.SensorReading.SensorReading
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        self.logger.debug("make_from_sensor_reading called")

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
            message = OutboundMessage(
                "d2p/sensor_reading/d/" + self.device_key + "/r/" + reading.reference,
                '{"data":"' + str(reading.value) + '"}',
            )
        else:
            message = OutboundMessage(
                "d2p/sensor_reading/d/" + self.device_key + "/r/" + reading.reference,
                '{"utc":"'
                + str(reading.timestamp)
                + '","data":"'
                + str(reading.value)
                + '"}',
            )

        self.logger.debug(
            "make_from_sensor_reading - Topic: %s ; Payload: %s",
            message.topic,
            message.payload,
        )
        return message

    def make_from_alarm(self, alarm):
        """
        Serialize the alarm to be sent to WolkAbout IoT Platform.

        :param alarm: Alarm event to be serialized
        :type alarm: wolk.models.Alarm.Alarm
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        self.logger.debug("make_from_alarm called")

        if alarm.active is True:
            alarm.active = "ON"
        elif alarm.active is False:
            alarm.active = "OFF"

        if alarm.timestamp is None:
            message = OutboundMessage(
                "d2p/events/d/" + self.device_key + "/r/" + alarm.reference,
                '{"data":"' + str(alarm.active) + '"}',
            )

        else:
            message = OutboundMessage(
                "d2p/events/d/" + self.device_key + "/r/" + alarm.reference,
                '{"utc":"'
                + str(alarm.timestamp)
                + '","data":"'
                + str(alarm.active)
                + '"}',
            )
        self.logger.debug(
            "make_from_alarm - Topic: %s ; Payload: %s",
            message.topic,
            message.payload,
        )
        return message

    def make_from_actuator_status(self, actuator):
        """
        Serialize the actuator status to be sent to WolkAbout IoT Platform.

        :param actuator: Actuator status to be serialized
        :type actuator: wolk.models.ActuatorStatus.ActuatorStatus
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        self.logger.debug("make_from_actuator_status called")
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

        message = OutboundMessage(
            "d2p/actuator_status/d/" + self.device_key + "/r/" + actuator.reference,
            '{"status":"' + actuator.state + '","value":"' + str(actuator.value) + '"}',
        )
        self.logger.debug(
            "make_from_actuator_status - Topic: %s ; Payload: %s",
            message.topic,
            message.payload,
        )
        return message

    def make_from_firmware_status(self, firmware_status):
        """
        Serialize the firmware status to be sent to WolkAbout IoT Platform.

        :param firmware_status: Firmware status to be serialized
        :type firmware_status: wolk.models.FirmwareStatus.FirmwareStatus
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    def make_from_chunk_request(self, file_name, chunk_index, chunk_size):
        """
        Request a firmware file chunk from WolkAbout IoT Platform.

        :param file_name: Name of the file to which the chunk belongs
        :type file_name: str
        :param chunk_index: Index of the requested chunk
        :type chunk_index: int
        :param chunk_size: Size of the requested chunk
        :type chunk_size: int
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    def make_from_firmware_version(self, version):
        """
        Report the current version of firmware to WolkAbout IoT Platform.

        :param version: Firmware version to report
        :type version: str
        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    def make_from_keep_alive_message(self):
        """
        Create a ping message.

        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        pass

    def make_from_configuration(self, configuration):
        """
        Report device's configuration to WolkAbout IoT Platform.

        :param configuration: Device's current configuration
        :type configuration: dict

        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage
        """
        self.logger.debug("make_from_configuration called")
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

        message = OutboundMessage(
            "d2p/configuration_get/d/" + self.device_key, '{"values":{' + values + "}}"
        )
        self.logger.debug(
            "make_from_configuration - Topic: %s ; Payload: %s",
            message.topic,
            message.payload,
        )
        return message
