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
from WolkConnect.Alarm import Alarm
from WolkConnect.Sensor import Sensor, ReadingsWithTimestamp, ReadingsCollection
from WolkConnect.Actuator import Actuator, ActuationException
from WolkConnect.ReadingType import RawReading, DataType

logger = logging.getLogger(__name__)
notNone = lambda x: not x is None


class WolkMQTTSerializer(abc.ABC):
    """ Abstract MQTT serializer class
    """
    @abc.abstractmethod
    def serializeToMQTTMessages(self, obj):
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
    JSON_SINGLE = "JSON_SINGLE"


def getSerializer(serializerType, serial):
    """ Get serializer for type and device serial number
    """
    if serializerType == WolkSerializerType.WOLKSENSE:
        return WolkSenseMQTTSerializer(serial)
    elif serializerType == WolkSerializerType.JSON_MULTI:
        return WolkJSONMQTTSerializer(serial)

    return WolkJSONSingleMQTTSerializer(serial)

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

    def serializeToMQTTMessages(self, obj):
        if isinstance(obj, Sensor):
            return [self._serializeReading(obj)]
        elif isinstance(obj, RawReading):
            return [self._serializeRawReading(obj)]
        elif isinstance(obj, ReadingsWithTimestamp):
            return [self._serializeReadingsWithTimestamp(obj)]
        elif isinstance(obj, ReadingsCollection):
            return [self._serializeReadingsCollection(obj)]
        elif isinstance(obj, Alarm):
            return [self._serializeAlarm(obj)]
        elif isinstance(obj, Actuator):
            return [self._serializeActuator(obj)]

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
        if not reading.readingValue:
            return None

        topic = self.rootReadingsTopic + self.serialNumber
        mqttString = self._serializeReadingToPayload(reading)
        mqttMessage = WolkMQTTPublishMessage(topic, mqttString)
        return mqttMessage

    def _serializeRawReading(self, reading):
        """ Serialize raw reading to mqtt message
        """
        if not reading.value:
            return None

        mqttString = self.READING_FORMAT.format(ref=reading.reference, value=reading.value)
        return mqttString

    def _serializeReadingToPayload(self, reading):
        """ Serialize reading to mqtt message payload
        """
        if isinstance(reading, RawReading):
            return self._serializeRawReading(reading)
        elif isinstance(reading, Sensor):
            return self._serializeRawReading(reading.getRawReading())
        elif isinstance(reading, Alarm):
            rawReading = reading.getRawReading()
            rawReading.value = 1 if reading.alarmValue == True else 0
            return self._serializeRawReading(rawReading)

        logger.warning("No reading to serialize")
        return None

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
            currentTimestamp = int(time.time())
            for item in collection.readings:
                if item.timestamp is None:
                    item.timestamp = currentTimestamp
            collection.readings.sort(key=lambda item:item.timestamp)

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
        alarmType = alarm.alarmRef
        alarmValue = "1" if alarm.alarmValue else "0"
        topic = self.rootReadingsTopic + self.serialNumber
        mqttString = self.ALARM_FORMAT.format(timestampString=timestampString, alarmType=alarmType, alarmValue=alarmValue)
        mqttMessage = WolkMQTTPublishMessage(topic, mqttString)
        return mqttMessage


    def _serializeActuator(self, actuator):
        """ Serialize Actuator to mqtt message
        """
        topic = self.rootActuatorsPublishTopic + self.serialNumber
        mqttString = self.ACTUATOR_STATUS_FORMAT.format(ref=actuator.actuatorRef, value=self._stringFromActuatorValue(actuator), state=actuator.actuatorState.value)
        mqttMessage = WolkMQTTPublishMessage(topic, mqttString)
        return mqttMessage


    @staticmethod
    def _stringFromActuatorValue(actuator):
        """ Check if value is possible for actuatorDataType
        """
        returnValue = ""
        # preconditions
        if not actuator.actuatorRef:
            raise ActuationException("Actuator type missing")
        elif actuator.value is None:
            raise ActuationException("Actuation value missing")

        # check if value and type match
        if actuator.dataType == DataType.BOOLEAN and WolkSenseMQTTSerializer._isValueBoolean(actuator):
            returnValue = WolkSenseMQTTSerializer._getStringFromBoolean(actuator)
        elif actuator.dataType == DataType.NUMERIC and WolkSenseMQTTSerializer._isValueNumeric(actuator):
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
            raise ActuationException("Actuation value is not numeric")

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
            raise ActuationException("Actuation value is not numeric")

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

    def serializeToMQTTMessages(self, obj):
        if isinstance(obj, Sensor):
            return [self._serializeReading(obj)]
        elif isinstance(obj, RawReading):
            return [self._serializeRawReading(obj)]
        elif isinstance(obj, ReadingsWithTimestamp):
            return [self._serializeReadingsWithTimestamp(obj)]
        elif isinstance(obj, ReadingsCollection):
            return [self._serializeReadingsCollection(obj)]
        elif isinstance(obj, Alarm):
            return [self._serializeAlarm(obj)]
        elif isinstance(obj, Actuator):
            return [self._serializeActuator(obj)]

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

            if isinstance(response, list):
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

    def extractSubscriptionTopics(self, device):
        if not device:
            return None

        topicPath = self.rootActuatorsSubscribeTopic + self.serialNumber + "/"
        return [topicPath + actuator.actuatorRef for actuator in device.getActuators()]

    def _serializeReading(self, reading):
        """ Serialize reading to mqtt message
        """
        if not reading.readingValue:
            return None

        topic = self.rootReadingsTopic + self.serialNumber
        mqttMessage = self._serialize(reading, _ReadingEncoder, topic)
        return mqttMessage

    def _serializeRawReading(self, reading):
        """ Serialize raw reading to mqtt message
        """
        if not reading.value:
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
            mqttMessage = self._serialize(collection, _ReadingsCollectionEncoder, topic)
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
        topic = self.rootActuatorsPublishTopic + self.serialNumber + "/" + actuator.actuatorRef
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
        if isinstance(o, Sensor):
            return _rawReadingToDict(o.getRawReading())
        elif isinstance(o, Alarm):
            return _rawReadingToDict(o.getRawReading())
        elif isinstance(o, RawReading):
            return _rawReadingToDict(o)

        return json.JSONEncoder.default(self, o)

def _rawReadingToDict(o):
    if not isinstance(o, RawReading):
        return None

    dct = {}
    if o.timestamp:
        dct["utc"] = int(o.timestamp)

    dct["data"] = o.value
    return dct


class _ReadingsArrayEncoder(json.JSONEncoder):
    """ Reading JSON encoder that returns
        dictionary with reading type and value
    """
    def default(self, o):
        if isinstance(o, ReadingsWithTimestamp):
            return _serializeReadingsWithTimestampToDictionary(o)
        return json.JSONEncoder.default(self, o)

def _serializeReadingsWithTimestampToDictionary(o):
    dct = {}
    if isinstance(o, ReadingsWithTimestamp):
        if o.timestamp:
            dct["utc"] = int(o.timestamp)
        else:
            dct["utc"] = int(time.time())

        for reading in o.readings:
            if isinstance(reading, RawReading):
                dct[reading.reference] = reading.value
            else:
                rawReading = reading.getRawReading()
                dct[rawReading.reference] = rawReading.value
    return dct

class _ReadingsCollectionEncoder(json.JSONEncoder):
    """ Reading collection JSON encoder that returns
        dictionary with reading type and value
    """
    def default(self, o):
        if isinstance(o, ReadingsCollection):
            readingLists = []
            for item in o.readings:
                itemDict = _serializeReadingsWithTimestampToDictionary(item)
                readingLists.append(itemDict)
            readingLists.sort(key=lambda item:item["utc"])
            return readingLists
        return json.JSONEncoder.default(self, o)

class _AlarmEncoder(json.JSONEncoder):
    """ Alarm JSON encoder that returns
        dictionary with data and reading value
    """
    def default(self, o):
        if isinstance(o, Alarm):
            dct = {}
            if o.timestamp:
                dct["utc"] = int(o.timestamp)

            dct[o.alarmRef] = o.alarmValue

            return dct
        return json.JSONEncoder.default(self, o)

class _ActuatorEncoder(json.JSONEncoder):
    """ Actuator JSON encoder that returns
        dictionary with status and value
    """
    def default(self, o):
        if isinstance(o, Actuator):
            dct = {}
            dct["status"] = o.actuatorState.value
            dct["value"] = o.value
            return dct

        return json.JSONEncoder.default(self, o)

# SINGLE
""" JSON Single Serialization
    for WolkConnect
"""
class WolkJSONSingleMQTTSerializer(WolkJSONMQTTSerializer):
    """ WolkJSON Single serializer
    """
    def __init__(self, serialNumber):
        super().__init__(serialNumber)

    def serializeToMQTTMessages(self, obj):
        if isinstance(obj, Sensor):
            return [self._serializeReading(obj)]
        elif isinstance(obj, RawReading):
            return [self._serializeRawReading(obj)]
        elif isinstance(obj, ReadingsWithTimestamp):
            return self._serializeReadingsWithTimestamp(obj)
        elif isinstance(obj, ReadingsCollection):
            return self._serializeReadingsCollection(obj)
        elif isinstance(obj, Alarm):
            return [self._serializeAlarm(obj)]
        elif isinstance(obj, Actuator):
            return [self._serializeActuator(obj)]

        raise TypeError("WolkJSONSingleMQTTSerializer can't serialize object {0}".format(repr(obj)))

    def _serializeReading(self, reading):
        """ Serialize reading to mqtt message
        """
        if not reading.readingValue:
            return None

        topic = self.rootReadingsTopic + self.serialNumber + "/" + reading.sensorRef
        mqttMessage = self._serialize(reading, _ReadingEncoder, topic)
        return mqttMessage

    def _serializeRawReading(self, reading):
        """ Serialize raw reading to mqtt message
        """
        if not reading.value:
            return None

        topic = self.rootReadingsTopic + self.serialNumber + "/" + reading.reference
        mqttMessage = self._serialize(reading, _ReadingEncoder, topic)
        return mqttMessage

    def _serializeReadingsWithTimestamp(self, readings):
        """ Serialize Readings to mqtt message
        """
        if readings.readings:
            mqttMessages = []
            for reading in readings.readings:
                topic = self.rootReadingsTopic + self.serialNumber + "/" + _getRefFromReading(reading)
                mqttMessages.append(self._serialize(reading, _ReadingEncoder, topic))
            return mqttMessages
        return None

    def _serializeReadingsCollection(self, collection):
        """ Serialize ReadingCollection to mqtt message
        """
        if collection.readings:
            mqttMessages = []
            for readings in collection.readings:
                messages = self._serializeReadingsWithTimestamp(readings)
                for message in messages:
                    mqttMessages.append(message)
            return mqttMessages
        return None

    def _serializeAlarm(self, alarm):
        """ Serialize Alarm to mqtt message
        """
        topic = self.rootEventsTopic + self.serialNumber + "/" + alarm.alarmRef
        mqttMessage = self._serialize(alarm, _AlarmJSONSingleEncoder, topic)
        return mqttMessage

    def _serializeActuator(self, actuator):
        """ Serialize Actuator to mqtt message
        """
        topic = self.rootActuatorsPublishTopic + self.serialNumber + "/" + actuator.actuatorRef
        mqttMessage = self._serialize(actuator, _ActuatorEncoder, topic)
        return mqttMessage

def _getRefFromReading(o):
    if isinstance(o, Sensor):
        return o.sensorRef
    elif isinstance(o, RawReading):
        return o.reference
    elif isinstance(o, Alarm):
        return o.alarmRef

    return None

class _AlarmJSONSingleEncoder(json.JSONEncoder):
    """ Alarm JSON encoder that returns
        dictionary with data and reading value
    """
    def default(self, o):
        if isinstance(o, Alarm):
            dct = {}
            if o.timestamp:
                dct["utc"] = int(o.timestamp)

            dct["data"] = o.alarmValue

            return dct
        return json.JSONEncoder.default(self, o)
