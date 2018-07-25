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
"""
OS Outbound Message Factory module.

Contains OSOutboundMessageFactory class used to create serialized messages
that are ready to be sent to the WolkAbout IoT Platform.
"""


from wolk.wolkcore import ActuatorState
from wolk.wolkcore import FirmwareErrorType
from wolk.wolkcore import FirmwareStatusType
from wolk.wolkcore import OutboundMessage
from wolk.wolkcore import OutboundMessageFactory
from wolk import LoggerFactory


class OSOutboundMessageFactory(OutboundMessageFactory):
    """
    Serializes messages to be sent to the WolkAbout IoT Platform.

    :ivar device_key: The key to use when serializing messages
    :vartype device_key: str
    :ivar logger: Logger instance issued from the LoggerFactory class
    :vartype logger: logger
    """

    def __init__(self, device_key):
        """Create a factory for serializing messages.

        :param device_key: The device key to use when serializing messages
        :type device_key: str
        """
        self.device_key = device_key
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug("Init - Device key: %s", device_key)

    def make_from_sensor_reading(self, reading):
        """
        Serialize the sensor reading to be sent to the WolkAbout IoT Platform.

        :param reading: sensor reading to be serialized
        :type reading: SensorReading
        :returns: message
        :rtype: OutboundMessage
        """
        self.logger.debug("make_from_sensor_reading called")
        if reading.timestamp is None:

            if isinstance(reading.value, tuple):

                delimiter = ","

                values_list = list()

                for value in reading.value:
                    values_list.append(value)
                    values_list.append(delimiter)

                values_list.pop()

                reading.value = "".join(map(str, values_list))

            message = OutboundMessage(
                "readings/" + self.device_key + "/" + reading.reference,
                '{ "data" : "' + str(reading.value) + '" }',
            )
            self.logger.debug(
                "make_from_sensor_reading - Channel: %s ; Payload: %s",
                message.channel,
                message.payload,
            )
            return message

        else:

            if isinstance(reading.value, tuple):

                delimiter = ","

                values_list = list()

                for value in reading.value:
                    values_list.append(value)
                    values_list.append(delimiter)

                values_list.pop()

                reading.value = "".join(map(str, values_list))

            message = OutboundMessage(
                "readings/" + self.device_key + "/" + reading.reference,
                '{ "utc" : "'
                + str(reading.timestamp)
                + '", "data" : "'
                + str(reading.value)
                + '" }',
            )
            self.logger.debug(
                "make_from_sensor_reading - Channel: %s ; Payload: %s",
                message.channel,
                message.payload,
            )
            return message

    def make_from_alarm(self, alarm):
        """
        Serialize the alarm to be sent to the WolkAbout IoT Platform.

        :param alarm: Alarm event to be serialized
        :type alarm: Alarm
        :returns: message
        :rtype: OutboundMessage
        """
        self.logger.debug("make_from_alarm called")
        if alarm.timestamp is None:

            if alarm.message is True:
                alarm.message = "ON"
            elif alarm.message is False:
                alarm.message = "OFF"

            message = OutboundMessage(
                "events/" + self.device_key + "/" + alarm.reference,
                '{ "data" : "' + str(alarm.message) + '" }',
            )
            self.logger.debug(
                "make_from_alarm - Channel: %s ; Payload: %s",
                message.channel,
                message.payload,
            )
            return message

        else:

            if alarm.message is True:
                alarm.message = "ON"
            elif alarm.message is False:
                alarm.message = "OFF"

            message = OutboundMessage(
                "events/" + self.device_key + "/" + alarm.reference,
                '{ "utc" : "'
                + str(alarm.timestamp)
                + '", "data" : "'
                + str(alarm.message)
                + '" }',
            )
            self.logger.debug(
                "make_from_alarm - Channel: %s ; Payload: %s",
                message.channel,
                message.payload,
            )
            return message

    def make_from_actuator_status(self, actuator):
        """
        Serialize the actuator status to be sent to the WolkAbout IoT Platform.

        :param actuator: actuator status to be serialized
        :type actuator: ActuatorStatus
        :returns: message
        :rtype: OutboundMessage
        """
        self.logger.debug("make_from_actuator_status called")
        if actuator.state == ActuatorState.ACTUATOR_STATE_READY:
            actuator.state = "READY"

        elif actuator.state == ActuatorState.ACTUATOR_STATE_BUSY:
            actuator.state = "BUSY"

        elif actuator.state == ActuatorState.ACTUATOR_STATE_ERROR:
            actuator.state = "ERROR"

        message = OutboundMessage(
            "actuators/status/" + self.device_key + "/" + actuator.reference,
            '{ "status" : "'
            + actuator.state
            + '" , "value" : "'
            + str(actuator.value).lower()
            + '" }',
        )
        self.logger.debug(
            "make_from_actuator_status - Channel: %s ; Payload: %s",
            message.channel,
            message.payload,
        )
        return message

    def make_from_firmware_status(self, firmware_status):
        """
        Serialize the firmware status to be sent to the WolkAbout IoT Platform.

        :param firmware_status: firmware status to be serialized
        :type firmware_status: FirmwareStatus
        :returns: message
        :rtype: OutboundMessage
        """
        self.logger.debug("make_from_firmware_status called")
        if (
            firmware_status.status
            == FirmwareStatusType.FIRMWARE_STATUS_FILE_TRANSFER
        ):
            firmware_status.status = "FILE_TRANSFER"

        elif (
            firmware_status.status
            == FirmwareStatusType.FIRMWARE_STATUS_FILE_READY
        ):
            firmware_status.status = "FILE_READY"

        elif (
            firmware_status.status
            == FirmwareStatusType.FIRMWARE_STATUS_INSTALLATION
        ):
            firmware_status.status = "INSTALLATION"

        elif (
            firmware_status.status
            == FirmwareStatusType.FIRMWARE_STATUS_COMPLETED
        ):
            firmware_status.status = "COMPLETED"

        elif (
            firmware_status.status
            == FirmwareStatusType.FIRMWARE_STATUS_ABORTED
        ):
            firmware_status.status = "ABORTED"

        elif (
            firmware_status.status == FirmwareStatusType.FIRMWARE_STATUS_ERROR
        ):
            firmware_status.status = "ERROR"

        if firmware_status.status == "ERROR":

            if (
                firmware_status.error
                == FirmwareErrorType.FIRMWARE_ERROR_UNSPECIFIED_ERROR
            ):
                firmware_status.error = "0"

            elif (
                firmware_status.error
                == FirmwareErrorType.FIRMWARE_ERROR_FILE_UPLOAD_DISABLED
            ):
                firmware_status.error = "1"

            elif (
                firmware_status.error
                == FirmwareErrorType.FIRMWARE_ERROR_UNSUPPORTED_FILE_SIZE
            ):
                firmware_status.error = "2"

            elif (
                firmware_status.error
                == FirmwareErrorType.FIRMWARE_ERROR_INSTALLATION_FAILED
            ):
                firmware_status.error = "3"

            elif (
                firmware_status.error
                == FirmwareErrorType.FIRMWARE_ERROR_MALFORMED_URL
            ):
                firmware_status.error = "4"

            elif (
                firmware_status.error
                == FirmwareErrorType.FIRMWARE_ERROR_FILE_SYSTEM_ERROR
            ):
                firmware_status.error = "5"

            elif (
                firmware_status.error
                == FirmwareErrorType.FIRMWARE_ERROR_RETRY_COUNT_EXCEEDED
            ):
                firmware_status.error = "10"

        if firmware_status.error:

            message = OutboundMessage(
                "service/status/firmware/" + self.device_key,
                '{"status" : "'
                + firmware_status.status
                + '", "error" : '
                + firmware_status.error
                + "}",
            )
            self.logger.debug(
                "make_from_firmware_status - Channel: %s ; Payload: %s",
                message.channel,
                message.payload,
            )
            return message
        else:

            message = OutboundMessage(
                "service/status/firmware/" + self.device_key,
                '{"status" : "' + firmware_status.status + '"}',
            )
            self.logger.debug(
                "make_from_firmware_status - Channel: %s ; Payload: %s",
                message.channel,
                message.payload,
            )
            return message

    def make_from_chunk_request(self, file_name, chunk_index, chunk_size):
        """
        Request a firmware chunk from the WolkAbout IoT Platform.

        :param file_name: name of the file to which the chunk belongs
        :type file_name: str
        :param chunk_index: index of the requested chunk
        :type chunk_index: int
        :param chunk_size: size of the requested chunk
        :type chunk_size: int
        :returns: message
        :rtype: OutboundMessage
        """
        self.logger.debug("make_from_chunk_request called")
        message = OutboundMessage(
            "service/status/file/" + self.device_key,
            '{ "fileName" : "'
            + file_name
            + '", "chunkIndex" : '
            + str(chunk_index)
            + ', "chunkSize" : '
            + str(chunk_size)
            + " }",
        )
        self.logger.debug(
            "make_from_chunk_request - Channel: %s ; Payload: %s",
            message.channel,
            message.payload,
        )
        return message

    def make_from_firmware_version(self, version):
        """
        Report the current version of firmware to the WolkAbout IoT Platform.

        :param version: firmware version to report
        :type version: str
        :returns: message
        :rtype: OutboundMessage
        """
        self.logger.debug("make_from_firmware_version called")
        message = OutboundMessage(
            "firmware/version/" + self.device_key, str(version)
        )
        self.logger.debug(
            "make_from_firmware_version - Channel: %s ; Payload: %s",
            message.channel,
            message.payload,
        )
        return message

    def make_from_keep_alive_message(self):
        """
        Create a ping message.

        :returns: message
        :rtype: OutboundMessage
        """
        self.logger.debug("make_from_keep_alive_message called")
        message = OutboundMessage("ping/" + self.device_key, None)
        self.logger.debug(
            "make_from_keep_alive_message - Channel: %s ; Payload: %s",
            message.channel,
            message.payload,
        )
        return message

    def make_from_configuration(self, configuration):
        """
        Report device's configuration to WolkAbout IoT Platform.

        :param configuration: device's current configuration
        :type configuration: dict

        :returns: message
        :rtype: OutboundMessage
        """
        self.logger.debug("make_from_configuration called")
        values = str()

        for reference, value in configuration.items():

            if isinstance(value, tuple):

                delimiter = ","

                values_list = list()

                for single_value in value:
                    values_list.append(single_value)
                    values_list.append(delimiter)

                values_list.pop()
                value = "".join(map(str, values_list))

            values += '"' + reference + '":"' + str(value) + '",'

        values = values[:-1]

        message = OutboundMessage(
            "configurations/current/" + self.device_key,
            '{"values":{' + values + "}}",
        )
        self.logger.debug(
            "make_from_configuration - Channel: %s ; Payload: %s",
            message.channel,
            message.payload,
        )
        return message
