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
    WolkDevice with sensors, actuators and alarms
"""

import logging
import time
import WolkConnect.WolkMQTT as WolkMQTT
import WolkConnect.Serialization.WolkMQTTSerializer as WolkMQTTSerializer
import WolkConnect.ReadingType as ReadingType
from WolkConnect.Sensor import Sensor
import WolkConnect.Serialization.WolkBufferSerialization as WolkBufferSerialization

logger = logging.getLogger(__name__)

class WolkDevice:
    """ WolkDevice class
    """
    def __init__(self, serial="", password="", host="api-demo.wolkabout.com", port=8883, certificate_file_path="WolkConnect/ca.crt", set_insecure=False, serializer=WolkMQTTSerializer.WolkSerializerType.JSON_MULTI, responseHandler=None, sensors=None, actuators=None, alarms=None, qos=0):
        """
            serial - Device serial used to connect to MQTT broker
            password - Device serial used to connect to MQTT broker
            host - MQTT broker host
            port - MQTT broker port
            certificate_file_path - path to Certificate Authority certificate file (neccessary when SSL is used for MQTT connection)
            set_insecure - if set to True, server hostname, in ca_cert, will be automatically verified (i.e. trusted)
            serializer - WolkMQTTSerializer. By default is is JSON_MULTI
            responseHandler - Handler that accepts WolkDevice and WolkMQTTSubscribeMessage object
                                used for processing raw messages from MQTT broker.
            sensors - List of Sensor objects
            actuators - List of Actuator objects
            alarms - List of Alarm objects
            qos - MQTT quality of service
        """

        self.serial = serial
        self.password = password

        self._sensors = {}
        if sensors:
            for sensor in sensors:
                self._sensors[sensor.sensorRef] = sensor

        self._actuators = {}
        if actuators:
            for actuator in actuators:
                self._actuators[actuator.actuatorRef] = actuator

        self._alarms = {}
        if alarms:
            for alarm in alarms:
                self._alarms[alarm.alarmRef] = alarm

        mqttSerializer = WolkMQTTSerializer.getSerializer(serializer, serial)
        subscriptionTopics = mqttSerializer.extractSubscriptionTopics(self)
        self.responseHandler = responseHandler
        clientConfig = WolkMQTT.WolkMQTTClientConfig(host, port, serial, password, mqttSerializer, subscriptionTopics, self._mqttResponseHandler, certificate_file_path, set_insecure, qos)
        
        self.mqttClient = WolkMQTT.WolkMQTTClient(clientConfig)

    def __str__(self):
        return "Device with serial:" + self.serial

    def getSensors(self):
        """ Get list of sensors
        """
        return list(self._sensors.values())

    def getSensor(self, ref):
        """ Get sensor by reference
        """
        return self._sensors[ref]

    def getActuators(self):
        """ Get list of actuators
        """
        return list(self._actuators.values())

    def getActuator(self, ref):
        """ Get actuator by reference
        """
        return self._actuators[ref]

    def getAlarms(self):
        """ Get list of alarms
        """
        return list(self._alarms.values())

    def getAlarm(self, ref):
        """ Get alarm by reference
        """
        return self._alarms[ref]

    def connect(self):
        """ Connect WolkDevice to MQTT broker
        """
        logger.info("Connecting %s to mqtt broker...", self.serial)
        self.mqttClient.connect()

    def disconnect(self):
        """ Disconnect WolkDevice from MQTT broker
        """
        logger.info("Disconnecting %s from mqtt broker...", self.serial)
        self.mqttClient.disconnect()


    def publishSensor(self, sensor):
        """ Publish one sensor
        """
        if not isinstance(sensor, Sensor):
            message = "Provided object is not a Sensor"
            logger.warning(message)
            return (False, message)

        return self._publishReadings([sensor])

    def publishRawReading(self, rawReading):
        """ Publish raw reading
        """
        if not isinstance(rawReading, ReadingType.RawReading):
            message = "Provided object is not a RawReading"
            logger.warning(message)
            return (False, message)

        return self._publishReadings([rawReading])

    def publishSensors(self, useCurrentTimestamp=False):
        """ Publish current values of all device's sensors

            If useCurrentTimestamp is True, each reading will be set the current timestamp,
            otherwise, timestamp from the reading will not be changed.
        """
        sensors = self.getSensors()

        if not sensors:
            message = "Could not publish readings. {0} does not have sensors".format(str(self))
            logger.warning(message)
            return (False, message)

        if useCurrentTimestamp:
            timestamp = time.time()
            for sensor in sensors:
                sensor.setTimestamp(timestamp)

        return self._publishReadings(sensors)

    def publishAlarm(self, alarm):
        """ Publish alarm to MQTT broker
        """
        result = self.mqttClient.publishAlarm(alarm)
        if result[0]:
            logger.info("%s published alarm %s", self.serial, alarm.alarmRef)
        else:
            logger.error("%s failed publishing alarm %s with error: %s", self.serial, alarm.alarmRef, str(result[1]))
        return result

    def publishActuator(self, actuator):
        """ Publish actuator to MQTT broker
        """
        result = self.mqttClient.publishActuator(actuator)
        if result[0]:
            logger.info("%s published actuator %s", self.serial, actuator.actuatorRef)
        else:
            logger.error("%s failed publishing actuator %s with error: %s", self.serial, actuator.actuatorRef, str(result[1]))
        return result


    def publishAll(self):
        """ Publish all actuators and sensors
        """
        result = self.publishSensors()
        if not result[0]:
            return result

        actuators = self.getActuators()
        if actuators:
            for actuator in actuators:
                result = self.publishActuator(actuator)
                if not result[0]:
                    return result
        
        return result

    def publishRandomReadings(self):
        """ Publish random values of all device's sensors
        """
        sensors = self.getSensors()

        if not sensors:
            message = "Could not publish random readings. {0} does not have sensors".format(str(self))
            logger.warning(message)
            return (False, message)

        timestamp = time.time()
        for sensor in sensors:
            randomValues = sensor.generateRandomValues()
            sensor.setReadingValues(randomValues)
            sensor.setTimestamp(timestamp)

        return self._publishReadings(sensors)

    def publishBufferedReadings(self, buffer, clearOnSuccess=False):
        """ Publish readings from the buffer
            clearOnSuccess - if True, the buffer will be cleared if readings are successfully published
        """
        if not isinstance(buffer, WolkBufferSerialization.WolkBuffer):
            message = "Could not publish buffered readings. {0} is not WolkBuffer".format(str(buffer))
            logger.warning(message)
            return (False, message)

        readingsToPublish = buffer.getReadings()
        result = self._publishReadings(readingsToPublish)
        if result[0] and clearOnSuccess:
            buffer.clear()

        return result

    def publishBufferedAlarms(self, buffer, clearOnSuccess=False):
        """ Publish alarms from the buffer
            clearOnSuccess - if True, the buffer will be cleared if alarms are successfully published
        """
        if not isinstance(buffer, WolkBufferSerialization.WolkBuffer):
            message = "Could not publish buffered alarms. {0} is not WolkBuffer".format(str(buffer))
            logger.warning(message)
            return (False, message)

        alarmsToPublish = buffer.getAlarms()
        result = (True, "")
        for alarm in alarmsToPublish:
            logger.debug("Serialized one alarm %s", alarm)
            result = self.publishAlarm(alarm)
            if result[0] == False:
                return result

        if result[0] and clearOnSuccess:
            buffer.clear()

        return result


    def _mqttResponseHandler(self, responses):
        """ Handle MQTT messages from MQTT broker
            Each message contains: 
                - ref, which is actuator reference
                - wolkCommand, which may be SET or STATUS
                - value, if wolkCommand is SET
            responseHandler, provided in WolkDevice.__init__, will be invoked for each message 
        """
        for message in responses:
            if message:
                self.responseHandler(self, message)

    def _publishReadings(self, readings):
        logger.info("%s publishing readings", self.serial)
        result = self.mqttClient.publishReadings(readings)
        if result[0]:
            logger.info("%s published readings", self.serial)
        else:
            logger.error("%s failed publishing readings with error: %s", self.serial, str(result[1]))
        return result
