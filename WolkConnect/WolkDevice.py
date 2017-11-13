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
import WolkConnect.Sensor as Sensor
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
            responseHandler - Handler that accepts list of WolkMQTTSubscribeMessage objects
                                used for processing raw messages from MQTT broker.
                            If not specified default implementation self._mqttResponseHandler is used
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
        messageHandler = responseHandler if responseHandler else self._mqttResponseHandler
        clientConfig = WolkMQTT.WolkMQTTClientConfig(host, port, serial, password, mqttSerializer, subscriptionTopics, messageHandler, certificate_file_path, set_insecure, qos)
        self.mqttClient = WolkMQTT.WolkMQTTClient(clientConfig)

    def __str__(self):
        return "Device with serial:" + self.serial

    def getSensors(self):
        """ Get list of sensors
        """
        return list(self._sensors.values())

    def getActuators(self):
        """ Get list of actuators
        """
        return list(self._actuators.values())

    def getAlarms(self):
        """ Get list of alarms
        """
        return list(self._alarms.values())

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


    def publishReading(self, reading):
        """ Publish one reading
        """
        if not isinstance(reading, Sensor.Sensor):
            logger.warning("Could not publish reading %s", str(reading))
            return

        self._publishReadings([reading])

    def publishRawReading(self, rawReading):
        """ Publish raw reading
        """
        if not isinstance(rawReading, Sensor.RawReading):
            logger.warning("Could not publish raw reading %s", str(rawReading))
            return

        self._publishReadings([rawReading])

    def publishReadings(self, useCurrentTimestamp=False):
        """ Publish current values of all device's sensors

            If useCurrentTimestamp is True, each reading will be set the current timestamp,
            otherwise, timestamp from the reading will not be changed.
        """
        sensors = self.getSensors()

        if not sensors:
            logger.warning("Could not publish readings. %s does not have sensors", str(self))
            return

        if useCurrentTimestamp:
            timestamp = time.time()
            for sensor in sensors:
                sensor.setTimestamp(timestamp)

        self._publishReadings(sensors)

    def publishAlarm(self, alarm):
        """ Publish alarm to MQTT broker
        """
        self.mqttClient.publishAlarm(alarm)
        logger.info("%s published alarm %s", self.serial, alarm.alarmRef)

    def publishActuator(self, actuator):
        """ Publish actuator to MQTT broker
        """
        self.mqttClient.publishActuator(actuator)
        logger.info("%s published actuator %s", self.serial, actuator.actuatorRef)

    def publishAll(self):
        """ Publish all actuators and sensors
        """
        self.publishReadings()

        actuators = self.getActuators()
        if actuators:
            for actuator in actuators:
                self.publishActuator(actuator)

    def publishRandomReadings(self):
        """ Publish random values of all device's sensors
        """
        sensors = self.getSensors()

        if not sensors:
            logger.warning("Could not publish random readings. %s does not have sensors", str(self))
            return

        timestamp = time.time()
        for sensor in sensors:
            randomValues = sensor.generateRandomValues()
            sensor.setReadingValues(randomValues)
            sensor.setTimestamp(timestamp)

        self._publishReadings(sensors)

    def publishBufferedReadings(self, buffer):
        """ Publish readings from the buffer
        """
        if not isinstance(buffer, WolkBufferSerialization.WolkBuffer):
            logger.warning("Could not publish buffered readings. %s is not WolkBuffer", str(buffer))
            return

        readingsToPublish = buffer.getReadings()
        self._publishReadings(readingsToPublish)

    def publishBufferedAlarms(self, buffer):
        """ Publish alarms from the buffer
        """
        if not isinstance(buffer, WolkBufferSerialization.WolkBuffer):
            logger.warning("Could not publish buffered readings. %s is not WolkBuffer", str(buffer))
            return

        alarmsToPublish = buffer.getAlarms()
        self._publishReadings(alarmsToPublish)

    def _mqttResponseHandler(self, responses):
        """ Handle MQTT messages from broker
        """
        for message in responses:
            if message:
                self._mqttMessageHandler(message)

    def _mqttMessageHandler(self, message):
        """ Handle single MQTT message from broker
        """
        actuator = None
        try:
            actuator = self._actuators[message.ref]
        except:
            logger.warning("%s could not find actuator with ref %s", self.serial, message.ref)
            return

        logger.info("%s received message %s", self.serial, message)
        if message.wolkCommand == WolkMQTTSerializer.WolkCommand.SET:
            actuator.value = message.value
            self.publishActuator(actuator)
        elif message.wolkCommand == WolkMQTTSerializer.WolkCommand.STATUS:
            self.publishActuator(actuator)
        else:
            logger.warning("Unknown command %s", message.wolkCommand)

    def _publishReadings(self, readings):
        self.mqttClient.publishReadings(readings)
        logger.info("%s published readings", self.serial)
