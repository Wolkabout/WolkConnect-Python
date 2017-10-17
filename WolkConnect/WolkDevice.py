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
import WolkConnect.WolkMQTT as WolkMQTT
import WolkConnect.Serialization.WolkMQTTSerializer as WolkMQTTSerializer
import WolkConnect.Sensor as Sensor

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

        self.sensors = {}
        for sensor in sensors:
            self.sensors[sensor.sensorType.ref] = sensor

        self.actuators = {}
        for actuator in actuators:
            self.actuators[actuator.actuatorType.ref] = actuator

        self.alarms = {}
        for alarm in alarms:
            self.alarms[alarm.alarmType.ref] = alarm

        mqttSerializer = WolkMQTTSerializer.getSerializer(serializer, serial)
        subscriptionTopics = mqttSerializer.extractSubscriptionTopics(self)
        messageHandler = responseHandler if responseHandler else self._mqttResponseHandler
        clientConfig = WolkMQTT.WolkMQTTClientConfig(host, port, serial, password, mqttSerializer, subscriptionTopics, messageHandler, certificate_file_path, set_insecure, qos)
        self.mqttClient = WolkMQTT.WolkMQTTClient(clientConfig)

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
        if isinstance(reading, Sensor.Reading):
            self.mqttClient.publishReadings([reading])


    def publishReadings(self, readings):
        self.mqttClient.publishReadings(readings)
        logger.info("%s published readings", self.serial)

    def publishAllReadings(self):
        """ Publish readings to MQTT broker
        """
        if not self.sensors:
            return

        readings = self.sensors.values()
        for feed in readings:
            randomValues = feed.sensorType.generateRandomValues()
            feed.setReadingValues(randomValues)

        self.publishReadings(readings)

    def publishAlarm(self, alarm):
        """ Publish alarm to MQTT broker
        """        
        self.mqttClient.publishAlarm(alarm)
        logger.info("%s published alarm %s", self.serial, alarm.alarmType.ref)

    def publishActuator(self, actuator):
        """ Publish actuator to MQTT broker
        """
        self.mqttClient.publishActuator(actuator)
        logger.info("%s published actuator %s", self.serial, actuator.actuatorType.ref)

    def _mqttResponseHandler(self, responses):
        """ Handle MQTT messages from broker
        """
        for message in responses:
            self._mqttMessageHandler(message)

    def _mqttMessageHandler(self, message):
        """ Handle single MQTT message from broker
        """
        actuator = None
        try:
            actuator = self.actuators[message.ref]
        except KeyError:
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

    def publishAll(self):
        self.publishAllReadings()

        for actuator in self.actuators.values():
            self.publishActuator(actuator)
