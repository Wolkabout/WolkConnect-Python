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

"""
    WolkMQTT serialization
"""

import abc
from enum import Enum, unique

import json
import logging
import time
import Alarm
import Sensor
import Actuator

logger = logging.getLogger(__name__)
notNone = lambda x: not x is None


class WolkMQTTSerializer(abc.ABC):
    """ Abstract MQTT serializer class
    """
    @abc.abstractmethod
    def serializeToMQTTMessage(self, obj):
        """ Abstract method to serialize obj
        """
        raise NotImplementedError

    @abc.abstractmethod
    def deserializeFromMQTTPayload(self, topic, payload):
        """ Abstract method to deserialize mqtt payload
            to protocol commands
        """
        raise NotImplementedError

    @abc.abstractmethod
    def extractSubscriptionTopics(self, device):
        """ Abstract method to extract subscription topics
            used in mqtt client to subscribe to mqtt broker
        """
        raise NotImplementedError


    def __init__(self, serialNumber, rootReadingsTopic, rootEventsTopic, rootActuatorsPublishTopic, rootActuatorsSubscribeTopic):
        super().__init__()
        self.serialNumber = serialNumber
        self.rootReadingsTopic = rootReadingsTopic
        self.rootEventsTopic = rootEventsTopic
        self.rootActuatorsPublishTopic = rootActuatorsPublishTopic
        self.rootActuatorsSubscribeTopic = rootActuatorsSubscribeTopic

@unique
class WolkCommand(Enum):
    """ WolkCommands
    """
    SET = "SET"
    STATUS = "STATUS"

    @classmethod
    def isCommandRecognized(cls, command):
        """ True if command is any of WolkCommand
        """
        try:
            return cls[command] is not None
        except KeyError:
            return False

class WolkMQTTMessage():
    """ Base WolkMQTTMessage
    """
    def __init__(self, topic):
        self.topic = topic

    def __str__(self):
        return "WolkMQTTMessage topic={0}".format(self.topic)



class WolkMQTTSubscribeMessage(WolkMQTTMessage):
    """ WolkMQTTMessage received from mqtt broker
    """
    def __init__(self, topic, ref, wolkCommand, value=None):
        super().__init__(topic)
        self.ref = ref
        self.wolkCommand = wolkCommand
        self.value = value

    def __str__(self):
        return "WolkMQTTMessage topic={0} ref={1} wolkCommand={2} value={3}".format(self.topic, self.ref, self.wolkCommand, self.value)

class WolkMQTTPublishMessage(WolkMQTTMessage):
    """ WolkMQTTMessage published to mqtt broker
    """
    def __init__(self, topic, payload):
        super().__init__(topic)
        self.payload = payload

    def __str__(self):
        return "WolkMQTTMessage topic={0} payload={1}".format(self.topic, self.payload)

@unique
class WolkSerializerType(Enum):
    """ Types of serializers
    """
    WOLKSENSE = "WOLKSENSE"
    JSON_MULTI = "JSON_MULTI"


def getSerializer(serializerType, serial):
    """ Get serializer for type and device serial number
    """
    if serializerType == WolkSerializerType.WOLKSENSE:
        return WolkSenseMQTTSerializer(serial)

    return WolkJSONMQTTSerializer(serial)


""" WolkSense Serializer for WolkConnect
"""
class WolkSenseMQTTSerializer(WolkMQTTSerializer):
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
        splittedPayload = list(filter(isNotEmpty, payload.split(self.COMMAND_TERMINATOR)))
        parseOneResponse = lambda x: self._parseResponse(topic, x)
        responses = list(map(parseOneResponse, splittedPayload))
        return responses

    def extractSubscriptionTopics(self, device):
        if not device:
            return None

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
        if not WolkCommand.isCommandRecognized(responseCommand):
            logger.warning("Command %s not recognized", responseCommand)
            return None

        command = WolkCommand[responseCommand]
        if command == WolkCommand.SET:
            return self._parseCommandSET(responseTokens, topic, mqttResponse)
        elif command == WolkCommand.STATUS:
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
        return WolkMQTTSubscribeMessage(topic, ref, WolkCommand.SET, refValue)

    @staticmethod
    def _parseCommandSTATUS(responseTokens, topic, mqttResponse):
        if len(responseTokens) < 2:
            logger.warning("Invalid response %s; expected 2 tokens", mqttResponse)
            return None

        ref = responseTokens[1]
        return WolkMQTTSubscribeMessage(topic, ref, WolkCommand.STATUS)

    def _serializeReading(self, reading):
        """ Serialize reading to mqtt message
        """
        if not reading.readingValues:
            return None

        topic = self.rootReadingsTopic + self.serialNumber
        mqttString = self._serializeReadingToPayload(reading)
        mqttMessage = WolkMQTTPublishMessage(topic, mqttString)
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
            mqttMessage = WolkMQTTPublishMessage(topic, mqttString)
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
            mqttMessage = WolkMQTTPublishMessage(topic, mqttString)
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
        mqttMessage = WolkMQTTPublishMessage(topic, mqttString)
        return mqttMessage


    def _serializeActuator(self, actuator):
        """ Serialize Actuator to mqtt message
        """
        topic = self.rootActuatorsPublishTopic + self.serialNumber
        mqttString = self.ACTUATOR_STATUS_FORMAT.format(ref=actuator.actuatorType.ref, value=self._stringFromActuatorValue(actuator), state=actuator.actuatorType.state.value)
        mqttMessage = WolkMQTTPublishMessage(topic, mqttString)
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

""" JSON Serializer for WolkConnect
"""
class WolkJSONMQTTSerializer(WolkMQTTSerializer):
    """ WolkJSON serializer
    """
    def __init__(self, serialNumber):
        rootReadings = "readings/"
        rootEvents = "events/"
        rootActuatorsPub = "actuators/status/"
        rootActuatorsSub = "actuators/commands/"
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

        raise TypeError("WolkJSONMQTTSerializer can't serialize object {0}".format(repr(obj)))


    def deserializeFromMQTTPayload(self, topic, payload):
        if not payload:
            return None

        try:
            response = json.loads(payload)
            reference = self._getRefFromTopic(topic)
            if reference is None:
                logger.warning("Could not get reference from topic %s", topic)
                return None

            if type(response) is list:
                parseOneResponse = lambda x: self._parseResponse(topic, reference, x)
                responses = list(map(parseOneResponse, response))
                return responses

            return [self._parseResponse(topic, reference, response)]

        except json.decoder.JSONDecodeError as e:
            logger.error("Error deserializing JSON payload with error: %s", e)
            return None

    @staticmethod
    def _getRefFromTopic(topic):
        pathItems = topic.split("/")
        if pathItems:
            return pathItems[len(pathItems)-1]

        return None

    @staticmethod
    def _parseResponse(topic, ref, payloadDictionary):
        try:
            responseCommand = payloadDictionary["command"]
            if not WolkCommand.isCommandRecognized(responseCommand):
                logger.warning("Command %s not recognized", responseCommand)
                return None

            command = WolkCommand[responseCommand]

            if command == WolkCommand.SET:
                try:
                    value = payloadDictionary["value"]
                    return WolkMQTTSubscribeMessage(topic, ref, command, value)
                except KeyError:
                    logger.error("Could not get value from payload %s", payloadDictionary)
                    return None
            elif command == WolkCommand.STATUS:
                return WolkMQTTSubscribeMessage(topic, ref, command)

            return None

        except KeyError:
            logger.error("Could not get command from payload %s", payloadDictionary)
            return None

    @staticmethod
    def roundFloat(floatValue):
        """ Helper to round float values to one decimal
        """
        return round(floatValue, 1)

    def extractSubscriptionTopics(self, device):
        if not device:
            return None

        topicPath = self.rootActuatorsSubscribeTopic + self.serialNumber + "/"
        return [topicPath + actuator.actuatorType.ref for actuator in device.actuators.values()]

    def _serializeReading(self, reading):
        """ Serialize reading to mqtt message
        """
        if not reading.readingValues:
            return None

        topic = self.rootReadingsTopic + self.serialNumber
        mqttMessage = self._serialize(reading, _ReadingEncoder, topic)
        return mqttMessage

    def _serializeReadingsWithTimestamp(self, readings):
        """ Serialize Readings to mqtt message
        """
        if readings.readings:
            topic = self.rootReadingsTopic + self.serialNumber
            mqttMessage = self._serialize(readings, _ReadingsArrayEncoder, topic)
            return mqttMessage

        return None

    def _serializeReadingsCollection(self, collection):
        """ Serialize ReadingCollection to mqtt message
        """
        if collection.readings:
            topic = self.rootReadingsTopic + self.serialNumber
            mqttMessage = self._serialize(collection.readings, _ReadingsArrayEncoder, topic)
            return mqttMessage

        return None

    def _serializeAlarm(self, alarm):
        """ Serialize Alarm to mqtt message
        """
        topic = self.rootEventsTopic + self.serialNumber
        mqttMessage = self._serialize(alarm, _AlarmEncoder, topic)
        return mqttMessage

    def _serializeActuator(self, actuator):
        """ Serialize Actuator to mqtt message
        """
        topic = self.rootActuatorsPublishTopic + self.serialNumber + "/" + actuator.actuatorType.ref
        mqttMessage = self._serialize(actuator, _ActuatorEncoder, topic)
        return mqttMessage

    @staticmethod
    def _serialize(obj, encoder, topic):
        mqttPayload = json.dumps(obj, cls=encoder)
        mqttMessage = WolkMQTTPublishMessage(topic, mqttPayload)
        return mqttMessage

class _ReadingEncoder(json.JSONEncoder):
    """ Reading JSON encoder that returns
        dictionary with data and reading value
    """
    def default(self, o):
        if isinstance(o, Sensor.Reading):
            dct = {}
            if o.timestamp:
                dct["utc"] = o.timestamp

            if o.sensorType.isScalar:
                dct["data"] = WolkJSONMQTTSerializer.roundFloat(o.readingValues[0])
            else:
                dct["data"] = list(map(WolkJSONMQTTSerializer.roundFloat, o.readingValues))

            return dct
        return json.JSONEncoder.default(self, o)

class _ReadingsArrayEncoder(json.JSONEncoder):
    """ Reading JSON encoder that returns
        dictionary with reading type and value
    """
    def default(self, o):
        if isinstance(o, Sensor.ReadingsWithTimestamp):
            dct = {}
            if o.timestamp:
                dct["utc"] = int(o.timestamp)

            for reading in o.readings:
                if reading.sensorType.isScalar:
                    dct[reading.sensorType.ref] = WolkJSONMQTTSerializer.roundFloat(reading.readingValues[0])
                else:
                    dct[reading.sensorType.ref] = list(map(WolkJSONMQTTSerializer.roundFloat, reading.readingValues))

            return dct
        return json.JSONEncoder.default(self, o)

class _AlarmEncoder(json.JSONEncoder):
    """ Alarm JSON encoder that returns
        dictionary with data and reading value
    """
    def default(self, o):
        if isinstance(o, Alarm.Alarm):
            dct = {}
            if o.timestamp:
                dct["utc"] = o.timestamp

            dct[o.alarmType.ref] = o.alarmValue

            return dct
        return json.JSONEncoder.default(self, o)

class _ActuatorEncoder(json.JSONEncoder):
    """ Actuator JSON encoder that returns
        dictionary with status and value
    """
    def default(self, o):
        if isinstance(o, Actuator.Actuator):
            dct = {}
            dct["status"] = o.actuatorType.state.value
            dct["value"] = o.value
            return dct

        return json.JSONEncoder.default(self, o)
