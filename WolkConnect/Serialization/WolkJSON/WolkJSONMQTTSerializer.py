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

""" JSON Serializer for WolkConnect
"""

import logging
import json
import WolkConnect.Alarm as Alarm
import WolkConnect.Sensor as Sensor
import WolkConnect.Actuator as Actuator
import WolkConnect.Serialization.WolkMQTTSerializer as serializer

logger = logging.getLogger(__name__)

class WolkJSONMQTTSerializer(serializer.WolkMQTTSerializer):
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
                parseOneResponse = lambda x:self._parseResponse(topic, reference, x)
                responses = list(map(parseOneResponse, response))
                return responses
            else:
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
            if not serializer.WolkCommand.isCommandRecognized(responseCommand):
                logger.warning("Command %s not recognized", responseCommand)
                return None

            command = serializer.WolkCommand[responseCommand]

            if command == serializer.WolkCommand.SET:
                try:
                    value = payloadDictionary["value"]
                    return serializer.WolkMQTTSubscribeMessage(topic, ref, command, value)
                except KeyError:
                    logger.error("Could not get value from payload %s", payloadDictionary)
                    return None
            elif command == serializer.WolkCommand.STATUS:
                return serializer.WolkMQTTSubscribeMessage(topic, ref, command)

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
        mqttMessage = serializer.WolkMQTTPublishMessage(topic, mqttPayload)
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
