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

"""OSMQTTConnectivityService Module."""

from paho.mqtt import client as mqtt

from wolk.interfaces.ConnectivityService import ConnectivityService
from wolk.models.InboundMessage import InboundMessage
from wolk import LoggerFactory


class OSMQTTConnectivityService(ConnectivityService):
    """Handle sending and receiving MQTT messages.

    :ivar ca_cert: Path to ca.crt file used for TLS
    :vartype ca_cert: str
    :ivar client: MQTT client used to send/receive data
    :vartype client: paho.mqtt.Client
    :ivar connected: State of the connection
    :vartype connected: bool
    :ivar connected_rc: return code of the connection
    :vartype connected_rc: int
    :ivar device: Holds authentication information and actuator references
    :vartype device: wolk.models.Device.Device
    :ivar host: Address of the MQTT broker
    :vartype host: str
    :ivar inbound_message_listener: Callback function for inbound messages
    :vartype inbound_message_listener: function
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar port: Port to which to send messages
    :vartype port: int
    :ivar qos: Quality of Service for the MQTT connection
    :vartype qos: int
    :ivar topics: List of topics to subscribe to
    :vartype topics: list
    """

    def __init__(
        self,
        device,
        topics,
        qos=2,
        host="api-demo.wolkabout.com",
        port=8883,
        ca_cert=None,
    ):
        """Provide the connection to the WolkAbout IoT Platform.

        :param device: Contains device key, password and actuator references
        :type device: wolk.models.Device.Device
        :param topics: List of topics to subscribe to
        :type topics: list
        :param qos: Quality of Service for MQTT connection
        :type qos: int or None
        :param host: Address of the MQTT broker
        :type host: str or None
        :param port: Port to which to send messages
        :type port: int or None
        :param ca_cert: Certificate file used to encrypt the connection
        :type ca_cert: str or None
        """
        self.device = device
        self.qos = qos
        self.host = host
        self.port = port
        self.connected = False
        self.connected_rc = None
        self.inbound_message_listener = None
        self.client = None
        self.topics = topics
        self.ca_cert = ca_cert
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(
            "Init:  Device key: %s ; Device password: %s ;"
            " Actuator references: %s ;"
            " QoS: %s ; Host: %s ; Port: %s ; CA certificate: %s ",
            self.device.key,
            self.device.password,
            self.device.actuator_references,
            self.qos,
            self.host,
            self.port,
            self.ca_cert,
        )

    def set_inbound_message_listener(self, on_inbound_message):
        """
        Set the callback function to handle inbound messages.

        :param on_inbound_message: Function that handles inbound messages
        :type on_inbound_message: function
        """
        self.logger.debug(
            "set_inbound_message_listener called - "
            "inbound_message_listener set to: %s",
            on_inbound_message,
        )
        self.inbound_message_listener = on_inbound_message

    def on_mqtt_message(self, client, userdata, message):
        """
        Serialize inbound messages and pass them to inbound message listener.

        :param client: Client that received the message
        :type client: paho.mqtt.Client
        :param userdata: Private user data set in Client()
        :type userdata: str
        :param message: Class with members: topic, payload, qos, retain.
        :type message: paho.mqtt.MQTTMessage
        """
        self.logger.debug("on_mqtt_message called")
        if not message:
            return

        self.inbound_message_listener(InboundMessage(message.topic, message.payload))
        self.logger.debug(
            "Received from topic: %s ; Payload: %s",
            message.topic,
            str(message.payload),
        )

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """
        Handle when the client receives a CONNACK response from the server.

        :param client: Client that received the message
        :type client: paho.mqtt.Client
        :param userdata: private user data set in Client()
        :type userdata: str
        :param flags: Response flags sent by the broker
        :type flags: int
        :param rc: Connection result
        :type rc: int
        """
        self.logger.debug("on_mqtt_connect called with rc: %s", rc)
        if rc == 0:  # Connection successful

            self.connected = True
            self.connected_rc = 0
            # Subscribing in on_mqtt_connect() means if we lose the connection
            # and reconnect then subscriptions will be renewed.
            if self.topics:
                for topic in self.topics:
                    self.client.subscribe(topic, 2)
            self.logger.debug("on_mqtt_connect - self.connected : %s", self.connected)
        elif rc == 1:  # Connection refused - incorrect protocol version
            self.connected_rc = 1
        elif rc == 2:  # Connection refused - invalid client identifier
            self.connected_rc = 2
        elif rc == 3:  # Connection refused - server unavailable
            self.connected_rc = 3
        elif rc == 4:  # Connection refused - bad username or password
            self.connected_rc = 4
        elif rc == 5:  # Connection refused - not authorised
            self.connected_rc = 5

    def on_mqtt_disconnect(self, client, userdata, rc):
        """
        Handle when the client disconnects from the broker.

        :param client: Client that received the message
        :type client: paho.mqtt.Client
        :param userdata: private user data set in Client()
        :type userdata: str
        :param rc: Disconnection result
        :type rc: int

        :raises RuntimeError: Unexpected disconnection
        """
        if rc != 0:
            raise RuntimeError("Unexpected disconnection.")
        self.connected = False
        self.connected_rc = None
        self.logger.debug("on_mqtt_disconnect - self.connected : %s", self.connected)

    def connect(self):
        """
        Establish the connection to the WolkAbout IoT platform.

        If there are actuators it will subscribe to topics
        that will contain actuator commands.
        Subscribes to firmware update related topics.
        Starts a loop to handle inbound messages.

        :raises RuntimeError: Reason for connection being refused
        """
        if self.connected:

            return

        self.logger.debug("connect started")
        self.client = mqtt.Client(client_id=self.device.key, clean_session=True)
        self.client.on_connect = self.on_mqtt_connect
        self.client.on_disconnect = self.on_mqtt_disconnect
        self.client.on_message = self.on_mqtt_message
        if self.ca_cert:
            self.client.tls_set(self.ca_cert)
            self.client.tls_insecure_set(True)
        self.client.username_pw_set(self.device.key, self.device.password)
        self.client.will_set("lastwill/" + self.device.key, "Gone offline", 2, False)

        self.logger.debug(
            "client.connect called : host: %s ; port:%s, ca_cert:%s "
            "; username:%s ; password:%s",
            self.host,
            self.port,
            self.ca_cert,
            self.device.key,
            self.device.password,
        )
        self.client.connect(self.host, self.port)

        self.client.loop_start()

        while True:

            if self.connected_rc is None:
                continue

            if self.connected_rc == 0:
                break

            elif self.connected_rc == 1:
                raise RuntimeError("Connection refused - incorrect protocol version")
                break

            elif self.connected_rc == 2:
                raise RuntimeError("Connection refused - invalid client identifier")
                break

            elif self.connected_rc == 3:
                raise RuntimeError("Connection refused - server unavailable")
                break

            elif self.connected_rc == 4:
                raise RuntimeError("Connection refused - bad username or password")
                break

            elif self.connected_rc == 5:
                raise RuntimeError("Connection refused - not authorised")
                break

        self.logger.debug("calling subscribe with topics: %s", self.topics)
        for topic in self.topics:
            self.client.subscribe(topic, 2)
        self.logger.debug("connect ended")

    def disconnect(self):
        """Disconnects the device from the WolkAbout IoT Platform."""
        self.logger.debug("disconnect")
        self.client.publish("lastwill/" + self.device.key, "Gone offline")
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, outbound_message):
        """
        Publish serialized data to WolkAbout IoT Platform.

        :param outbound_message: Message to be published
        :type outbound_message: wolk.models.OutboundMessage.OutboundMessage

        :returns: result
        :rtype: bool
        """
        if outbound_message is None:
            self.logger.warning("No message to publish!")
            return False

        if not self.connected:
            self.logger.warning(
                "Not connected, unable to publish. Topic: %s ; Payload: %s",
                outbound_message.topic,
                outbound_message.payload,
            )
            return False

        info = self.client.publish(
            outbound_message.topic, outbound_message.payload, self.qos
        )

        if info.rc == mqtt.MQTT_ERR_SUCCESS:

            self.logger.debug(
                "Published to topic: %s ; Payload: %s",
                outbound_message.topic,
                outbound_message.payload,
            )
            return True

        elif info.is_published():

            self.logger.debug(
                "Published to topic: %s ; Payload: %s",
                outbound_message.topic,
                outbound_message.payload,
            )
            return True

        else:

            self.logger.warning(
                "Publishing failed! Topic: %s ; Payload: %s",
                outbound_message.topic,
                outbound_message.payload,
            )
            return False
