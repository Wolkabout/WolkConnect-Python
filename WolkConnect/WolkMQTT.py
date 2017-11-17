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
    MQTT Client for communication with WolkAbout platform
"""
import logging
import paho.mqtt.client as mqtt
from WolkConnect.Sensor import ReadingsCollection

logger = logging.getLogger(__name__)

class WolkMQTTClientException(Exception):
    """ WolkMQTTClientException raised whenever there is an error in
        communication with WolkAbout mqtt broker
    """
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class WolkMQTTClientConfig:
    """ WolkMQTTClient configuration for WolkAbout MQTT broker
    """
    def __init__(self, host, port, username, password, serializer, topics, messagesHandler, ca_cert=None, set_insecure=None, qos=0, wolkClientId=None):
        """
            host - broker host
            port - broker port
            username - MQTT client's username
            password - MQTT client's password
            serializer - WolkMQTTSerializer
            topics - subscription topics to subscribe on broker
            messagesHandler - callback for handling WolkMQTTSubscribeMessages received from broker
            ca_cert - path to Certificate Authority certificate file
            set_insecure - if set to True, server hostname, in ca_cert, will be automatically verified (i.e. trusted)
            qos - MQTT quality of service
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.serializer = serializer
        self.topics = topics
        self.wolkClientId = wolkClientId
        self.messagesHandler = messagesHandler
        self.ca_cert = ca_cert
        self.set_insecure = set_insecure
        self.qos = qos

class WolkMQTTClient:
    """ WolkMQTTClient for publishing readings to WolkAbout MQTT broker
    """
    def __init__(self, wolkMQTTClientConfig):
        self.clientConfig = wolkMQTTClientConfig
        # Setup MQTT client
        self.client = mqtt.Client(self.clientConfig.wolkClientId, True)
        self.client.on_connect = self._on_mqtt_connect
        self.client.on_disconnect = self._on_mqtt_disconnect
        self.client.on_message = self._on_mqtt_message

        if self.clientConfig.ca_cert:
            self.client.tls_set(self.clientConfig.ca_cert)

        if self.clientConfig.set_insecure:
            self.client.tls_insecure_set(self.clientConfig.set_insecure)

        self.client.username_pw_set(self.clientConfig.username, self.clientConfig.password)
        self.host = self.clientConfig.host
        self.port = self.clientConfig.port
        lastWillTopic = "lastwill/" + self.clientConfig.username
        lastWillPayloyad = "Last will of serial:" + self.clientConfig.username
        self.client.will_set(lastWillTopic, lastWillPayloyad, self.clientConfig.qos, False)
        self.client.on_log = self._on_log

    def publishReadings(self, readings):
        """ Publish readings to MQTT broker
        """
        readingsCollection = ReadingsCollection.collectionFromReadingsList(readings)
        mqttMessage = self.clientConfig.serializer.serializeToMQTTMessage(readingsCollection)
        logger.debug("Serialized readings collection to mqttMessage %s", mqttMessage)
        return self._publish(mqttMessage)

    def publishActuator(self, actuator):
        """ Publish actuator to MQTT broker
        """
        mqttMessage = self.clientConfig.serializer.serializeToMQTTMessage(actuator)
        return self._publish(mqttMessage)

    def publishAlarm(self, alarm):
        """ Publish alarm to MQTT broker
        """
        mqttMessage = self.clientConfig.serializer.serializeToMQTTMessage(alarm)
        return self._publish(mqttMessage)

    def connect(self):
        """ Connect to MQTT broker
        """
        self.client.connect(self.host, self.port)
        self.client.loop_start()

    def disconnect(self):
        """ Disconnect from MQTT broker
        """
        self.client.loop_stop()
        self.client.disconnect()

    # Setup MQTT callback handlers
    def _on_mqtt_connect(self, _, __, ___, result):
        if result:
            errorMessage = "Error connecting to mqtt broker: " + mqtt.connack_string(result)
            logger.error(errorMessage)
            raise WolkMQTTClientException(errorMessage)
        else:
            logger.info("Connected %s to mqtt broker", self.clientConfig.username)

        for topic in self.clientConfig.topics:
            (res, ____) = self.client.subscribe(topic, self.clientConfig.qos)
            if res == 0:
                logger.info("Subscribed to topic: %s", topic)
            else:
                logger.error("Failed subscribing to topic: %s reason: %s", topic, mqtt.error_string(res))

    def _on_mqtt_disconnect(self, _, __, result):
        if result:
            errorMessage = "Disconnected " + self.clientConfig.username + " with error code " + str(result)
            logger.error(errorMessage)
            raise WolkMQTTClientException(errorMessage)
        else:
            logger.info("Disconnected %s from mqtt broker", self.clientConfig.username)


    def _on_mqtt_message(self, _, __, msg):
        mqttMessage = str(msg.payload, "utf-8")
        logger.debug("Message received from: " + msg.topic + " " + str(msg.qos) + " " + mqttMessage)
        self._mqttMessageHandler(msg.topic, mqttMessage)

    def _on_log(self, _, __, level, buf):
        devStr = str(self.clientConfig.username)
        lvlStr = str(level)
        bufStr = str(buf)
        logger.debug("device: %s level:%s -- %s", devStr, lvlStr, bufStr)

    def _mqttMessageHandler(self, topic, payload):
        responses = self.clientConfig.serializer.deserializeFromMQTTPayload(topic, payload)
        self.clientConfig.messagesHandler(responses)

    def _publish(self, message):
        """ publish WolkMQTTPublishMessage
        """
        logger.info("Publish %s", message)

        if not self.client:
            raise WolkMQTTClientException("No mqtt client")

        if not message:
            logger.warning("No message to publish")
            return(False, "No message to publish")

        info = self.client.publish(message.topic, message.payload, self.clientConfig.qos)
        if info.rc == mqtt.MQTT_ERR_SUCCESS:
            return(True, "")
        elif info.is_published:
            return(True, "")
        else:
            return(False, mqtt.error_string(info.rc))
