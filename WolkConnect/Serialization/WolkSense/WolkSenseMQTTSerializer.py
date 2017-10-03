#   Copyright 2017 WolkAbout Technology s.r.o.
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

""" WolkSense Serializer for WolkConnect
"""

import logging
import time
import WolkConnect.Alarm as Alarm
import WolkConnect.Sensor as Sensor
import WolkConnect.Actuator as Actuator
import WolkConnect.Serialization.WolkMQTTSerializer as serializer
import WolkConnect.WolkDevice as WolkDevice

logger = logging.getLogger(__name__)
notNone = lambda x: not x is None


class WolkSenseMQTTSerializer(serializer.WolkMQTTSerializer):
    """ WolkSense serializer
    """
    VALUE_SEPARATOR = ":"
    READING_SEPARATOR = ","
    READINGS_SEPARATOR = "|"
    COMMAND_TERMINATOR = ";"
    ACTUATOR_STATUS_FORMAT = "STATUS {ref}:{value}:{state};"
    READING_FORMAT = "{ref}:{value}"
    READING_LIST_FORMAT = "R:{timestampString},{readingsList}"
    READING_LISTS_FORMAT = "RTC {timestampString};READINGS {readingsList};"
    ALARM_FORMAT = "READINGS R:{timestampString},{alarmType}:{alarmValue};"

    def __init__(self, serialNumber):
        rootReadings = "sensors/"
        rootEvents = "config/"
        rootActuatorsPub = "sensors/"
        rootActuatorsSub = "config/"
        super().__init__(serialNumber, rootReadings, rootEvents, rootActuatorsPub, rootActuatorsSub)

    def serializeToMQTTMessage(self, obj):
        if isinstance(obj, Sensor.Reading):
            return self._serializeReading(obj)
        elif isinstance(obj, Sensor.ReadingsWithTimestamp):
            return self._serializeReadingsWithTimestamp(obj)
        elif isinstance(obj, Sensor.ReadingsCollection):
            return self._serializeReadingsCollection(obj)
        elif isinstance(obj, Alarm.Alarm):
            return self._serializeAlarm(obj)
        elif isinstance(obj, Actuator.Actuator):
            return self._serializeActuator(obj)

        raise TypeError("WolkSenseMQTTSerializer can't serialize object {0}".format(repr(obj)))

    def deserializeFromMQTTPayload(self, topic, payload):
        if not payload:
            return None

        isNotEmpty = lambda x: bool(x and x.strip())
        splittedPayload = list(filter(isNotEmpty,payload.split(self.COMMAND_TERMINATOR)))
        parseOneResponse = lambda x:self._parseResponse(topic, x)
        responses = list(map(parseOneResponse, splittedPayload))
        return responses

    def extractSubscriptionTopics(self, device):
        if not device:
            return None

        if not isinstance(device, WolkDevice.WolkDevice):
            raise TypeError("device must be WolkDevice instance")

        return [self.rootActuatorsSubscribeTopic + self.serialNumber]

    def _parseResponse(self, topic, mqttResponse):
        """ Parse mqtt response and return WolkMQTTSubscribeMessage or None
        """
        delimiter = " "
        responseTokens = mqttResponse.split(delimiter)

        if responseTokens is None:
            logger.warning("No response")
            return None

        responseCommand = responseTokens[0]
        if not serializer.WolkCommand.isCommandRecognized(responseCommand):
            logger.warning("Command %s not recognized", responseCommand)
            return None

        command = serializer.WolkCommand[responseCommand]
        if command == serializer.WolkCommand.SET:
            return self._parseCommandSET(responseTokens, topic, mqttResponse)
        elif command == serializer.WolkCommand.STATUS:
            return self._parseCommandSTATUS(responseTokens, topic, mqttResponse)

        return None

    def _parseCommandSET(self, responseTokens, topic, mqttResponse):
        if len(responseTokens) < 2:
            logger.warning("Invalid response %s; expected 2 tokens", mqttResponse)
            return None

        value = responseTokens[1]
        valueSplitted = value.split(self.VALUE_SEPARATOR)
        if valueSplitted is None or len(valueSplitted) < 2:
            logger.warning("Invalid response %s expected 2 elements in %s", mqttResponse, value)
            return None

        ref = valueSplitted[0]
        refValue = valueSplitted[1]
        return serializer.WolkMQTTSubscribeMessage(topic, ref, serializer.WolkCommand.SET, refValue)

    @staticmethod
    def _parseCommandSTATUS(responseTokens, topic, mqttResponse):
        if len(responseTokens) < 2:
            logger.warning("Invalid response %s; expected 2 tokens", mqttResponse)
            return None

        ref = responseTokens[1]
        return serializer.WolkMQTTSubscribeMessage(topic, ref, serializer.WolkCommand.STATUS)

    def _serializeReading(self, reading):
        """ Serialize reading to mqtt message
        """
        if not reading.readingValues:
            return None

        topic = self.rootReadingsTopic + self.serialNumber
        mqttString = self._serializeReadingToPayload(reading)
        mqttMessage = serializer.WolkMQTTPublishMessage(topic, mqttString)
        return mqttMessage

    def _serializeReadingToPayload(self, reading):
        """ Serialize reading to mqtt message payload
        """
        if not reading.readingValues:
            logger.warning("No reading values to serialize")
            return None

        if reading.sensorType.dataType == Sensor.ReadingType.DataType.STRING:
            return reading.sensorType.ref + self.VALUE_SEPARATOR + "".join(reading.readingValues)

        listOfInt = filter(notNone, [int(r * reading.times) for r in reading.readingValues if r])
        listOfStrings = []
        for i in listOfInt:
            if i >= 10:
                listOfStrings.append("{:+.0f}".format(i))
            else: # pad one digit numbers with leading 0 and keep sign prefix
                listOfStrings.append("{:+.0f}".format(i).zfill(3))

        correctedValues = "".join(listOfStrings)
        mqttString = self.READING_FORMAT.format(ref=reading.sensorType.ref, value=correctedValues)
        return mqttString

    def _serializeReadingsWithTimestamp(self, readings):
        """ Serialize Readings to mqtt message
        """
        if readings.readings:
            topic = self.rootReadingsTopic + self.serialNumber
            mqttString = self._serializeReadingsWithTimestampToPayload(readings)
            mqttMessage = serializer.WolkMQTTPublishMessage(topic, mqttString)
            return mqttMessage

        return None

    def _serializeReadingsWithTimestampToPayload(self, readings):
        """ Serialize Readings to mqtt message payload
        """
        if readings.readings:
            lst = filter(notNone, [self._serializeReadingToPayload(r) for r in readings.readings if r])
            logger.info(lst)
            readingsList = self.READING_SEPARATOR.join(lst)
            timestamp = ""
            if readings.timestamp is None:
                timestamp = str(int(time.time()))
            else:
                timestamp = str(int(readings.timestamp))

            mqttString = self.READING_LIST_FORMAT.format(timestampString=timestamp, readingsList=readingsList)
            return mqttString

        return None

    def _serializeReadingsCollection(self, collection):
        """ Serialize ReadingCollection to mqtt message
        """
        if collection.readings:
            lst = filter(notNone, [self._serializeReadingsWithTimestampToPayload(r) for r in collection.readings if r])
            readingsList = self.READINGS_SEPARATOR.join(lst)
            timestampString = str(int(time.time()))
            topic = self.rootReadingsTopic + self.serialNumber
            mqttString = self.READING_LISTS_FORMAT.format(timestampString=timestampString, readingsList=readingsList)
            mqttMessage = serializer.WolkMQTTPublishMessage(topic, mqttString)
            return mqttMessage

        return None

    def _serializeAlarm(self, alarm):
        """ Serialize Alarm to mqtt message
        """
        timestampString = str(int(time.time()))
        alarmType = alarm.alarmType.ref
        alarmValue = "1" if alarm.alarmValue else "0"
        topic = self.rootReadingsTopic + self.serialNumber
        mqttString = self.ALARM_FORMAT.format(timestampString=timestampString, alarmType=alarmType, alarmValue=alarmValue)
        mqttMessage = serializer.WolkMQTTPublishMessage(topic, mqttString)
        return mqttMessage


    def _serializeActuator(self, actuator):
        """ Serialize Actuator to mqtt message
        """
        topic = self.rootActuatorsPublishTopic + self.serialNumber
        mqttString = self.ACTUATOR_STATUS_FORMAT.format(ref=actuator.actuatorType.ref, value=self._stringFromActuatorValue(actuator), state=actuator.actuatorType.state.value)
        mqttMessage = serializer.WolkMQTTPublishMessage(topic, mqttString)
        return mqttMessage


    @staticmethod
    def _stringFromActuatorValue(actuator):
        """ Check if value is possible for actuatorDataType
        """
        returnValue = ""
        # preconditions
        if not actuator.actuatorType:
            raise Actuator.ActuationException("Actuator type missing")
        elif actuator.value is None:
            raise Actuator.ActuationException("Actuation value missing")

        # check if value and type match
        if actuator.actuatorType.dataType == Sensor.ReadingType.DataType.BOOLEAN and WolkSenseMQTTSerializer._isValueBoolean(actuator):
            returnValue = WolkSenseMQTTSerializer._getStringFromBoolean(actuator)
        elif actuator.actuatorType.dataType == Sensor.ReadingType.DataType.NUMERIC and WolkSenseMQTTSerializer._isValueNumeric(actuator):
            returnValue = WolkSenseMQTTSerializer._getStringFromNumeric(actuator)
        else:
            returnValue = str(actuator.value)

        return returnValue

    @staticmethod
    def _isValueBoolean(actuator):
        """ Helper to check if actuator value is boolean
        """
        return actuator.value == 0 or \
                actuator.value == 1 or \
                actuator.value.upper == "TRUE" or \
                actuator.value.upper == "FALSE"

    @staticmethod
    def _isValueNumeric(actuator):
        """ Helper to check if actuator value is float
        """
        try:
            float(actuator.value)
            return True
        except ValueError:
            raise Actuator.ActuationException("Actuation value is not numeric")

    @staticmethod
    def _getStringFromBoolean(actuator):
        """ Helper to convert boolean to string
        """
        if actuator.value == 1 or str(actuator.value).upper == "TRUE":
            return "true"
        elif actuator.value == 0 or str(actuator.value).upper == "FALSE":
            return "false"

        return "false"

    @staticmethod
    def _getStringFromNumeric(actuator):
        """ Helper to convert float to string
        """
        try:
            fl = float(actuator.value)
            if fl >= 10.0:
                return "{:+.0f}".format(fl)

            # pad one digit numbers with leading 0 and keep sign prefix
            return "{:+.0f}".format(fl).zfill(3)
        except ValueError:
            raise Actuator.ActuationException("Actuation value is not numeric")
