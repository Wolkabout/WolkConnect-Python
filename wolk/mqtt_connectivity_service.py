"""Connectivity service based on MQTT protocol."""
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
from time import sleep
from time import time
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from paho.mqtt import client as mqtt  # type: ignore

from wolk import logger_factory
from wolk.interface.connectivity_service import ConnectivityService
from wolk.model.device import Device
from wolk.model.message import Message


class MQTTConnectivityService(ConnectivityService):
    """Handle sending and receiving MQTT messages."""

    def __init__(
        self,
        device: Device,
        topics: List[str],
        last_will_message: Message,
        qos: Optional[int] = 0,
        host: Optional[str] = "api-demo.wolkabout.com",
        port: Optional[int] = 8883,
        ca_cert: Optional[str] = None,
    ) -> None:
        """
        Provide the connection to the WolkAbout IoT Platform.

        :param device: Contains device key, password and actuator references
        :type device: Device
        :param topics: List of topics to subscribe to
        :type topics: List[str]
        :param last_will_message: Message in case of unexpected disconnects
        :type last_will_message: Message
        :param qos: Quality of Service for MQTT connection (0, 1, 2)
        :type qos: int or None
        :param host: Address of the MQTT broker
        :type host: str or None
        :param port: Port to which to send messages
        :type port: int or None
        :param ca_cert: Path to certificate file used to encrypt the connection
        :type ca_cert: str or None
        """
        self.device = device
        self.last_will_message = last_will_message
        self.qos = qos
        self.host = host
        self.port = port
        self.connected = False
        self.connected_rc: Optional[int] = None
        self.topics = topics
        self.ca_cert = ca_cert
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(
            f"Device key: {self.device.key} ; "
            f"Device password: {self.device.password} ;"
            f"Actuator references: {self.device.actuator_references} ; "
            f"Last will message: {self.last_will_message} ; "
            f"QoS: {self.qos} ; "
            f"Host: {self.host} ; "
            f"Port: {self.port} ; "
            f"CA certificate: {self.ca_cert}"
        )

    def is_connected(self) -> bool:
        """
        Return current connection state.

        :returns: connected
        :rtype: bool
        """
        return self.connected

    def set_inbound_message_listener(
        self, on_inbound_message: Callable[[Message], None]
    ) -> None:
        """
        Set the callback function to handle inbound messages.

        :param on_inbound_message: Function that handles inbound messages
        :type on_inbound_message: Callable[[Message], None]
        """
        self.logger.debug(f"Message listener set to: {on_inbound_message}")
        self.inbound_message_listener = on_inbound_message

    def on_mqtt_message(
        self, client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage
    ) -> None:
        """
        Serialize inbound messages and pass them to inbound message listener.

        :param client: Client that received the message
        :type client: paho.mqtt.Client
        :param userdata: Private user data set in Client()
        :type userdata: str
        :param message: Class with members: topic, payload, qos, retain.
        :type message: paho.mqtt.MQTTMessage
        """
        if not message:
            return
        received_message = Message(message.topic, message.payload)
        if "binary" in received_message.topic:  # To skip printing file binary
            self.logger.debug(
                "Received MQTT message: "  # type: ignore
                f"{received_message.topic} , "
                f"size: {len(received_message.payload)} bytes"
            )
        else:
            self.logger.debug(f"Received MQTT message: {received_message}")
        self.inbound_message_listener(received_message)

    def on_mqtt_connect(
        self, client: mqtt.Client, userdata: Any, flags: int, rc: int
    ) -> None:
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
        self.logger.debug(f"Return code: {rc}")
        if rc == 0:  # Connection successful

            self.connected = True
            self.connected_rc = 0
            # Subscribing in on_mqtt_connect() means if we lose the connection
            # and reconnect then subscriptions will be renewed.
            if self.topics:
                for topic in self.topics:
                    self.client.subscribe(topic, 2)
            self.logger.debug(f"Connected : {self.connected}")
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

    def on_mqtt_disconnect(
        self, client: mqtt.Client, userdata: Any, rc: int
    ) -> None:
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
        self.connected = False
        self.connected_rc = None
        self.logger.debug(f"Connected : {self.connected}")
        if rc != 0:
            self.logger.error("Unexpected disconnect!")
            self.logger.info("Attempting to reconnect..")
            self.connect()

    def connect(self) -> bool:
        """
        Establish the connection to the WolkAbout IoT platform.

        Subscribes to all topics defined by device communication protocol.
        Starts a loop to handle inbound messages.

        :returns: Connection state, True if connected, False otherwise
        :rtype: bool
        """
        if self.connected:
            return True

        self.client = mqtt.Client(
            client_id=self.device.key, clean_session=True
        )
        self.client.on_connect = self.on_mqtt_connect
        self.client.on_disconnect = self.on_mqtt_disconnect
        self.client.on_message = self.on_mqtt_message
        if self.ca_cert:
            self.client.tls_set(self.ca_cert)
            self.client.tls_insecure_set(True)
        self.client.username_pw_set(self.device.key, self.device.password)
        self.client.will_set(
            self.last_will_message.topic,
            self.last_will_message.payload,
            2,
            False,
        )

        self.logger.debug(
            f"Connecting with parameters: host='{self.host}', "
            f"port={self.port}, ca_cert='{self.ca_cert}', "
            f"username='{self.device.key}', "
            f"password='{self.device.password}'"
        )
        try:
            self.client.connect(self.host, self.port)
        except Exception as e:
            self.logger.error(f"Something went wrong while connecting: {e}")
            return False

        self.client.loop_start()

        timeout = round(time()) + 10

        while True:

            if round(time()) > timeout:
                self.logger.warning("Connection timed out!")
                return False

            if self.connected_rc is None:
                sleep(0.1)
                continue

            if self.connected_rc == 0:
                self.logger.info("Connected!")
                return True

            elif self.connected_rc == 1:
                self.logger.warning(
                    "Connection refused - incorrect protocol version"
                )
                return False

            elif self.connected_rc == 2:
                self.logger.warning(
                    "Connection refused - invalid client identifier"
                )
                return False

            elif self.connected_rc == 3:
                self.logger.warning("Connection refused - server unavailable")
                return False

            elif self.connected_rc == 4:
                self.logger.warning(
                    "Connection refused - bad username or password"
                )
                return False

            elif self.connected_rc == 5:
                self.logger.warning("Connection refused - not authorised")
                return False

        self.logger.debug(f"Subscribing to topics: {self.topics}")
        for topic in self.topics:
            self.client.subscribe(topic, 2)

    def disconnect(self) -> None:
        """Disconnects the device from the WolkAbout IoT Platform."""
        self.logger.debug("Disconnecting")
        self.client.publish("lastwill/" + self.device.key, "Gone offline")
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, message: Message) -> bool:
        """
        Publish serialized data to WolkAbout IoT Platform.

        :param message: Message to be published
        :type message: Message

        :returns: result
        :rtype: bool
        """
        if message is None:
            self.logger.warning("No message to publish!")
            return False

        if not self.connected:
            self.logger.warning(
                f"Not connected, unable to publish message: {message}"
            )
            return False

        info = self.client.publish(message.topic, message.payload, self.qos)

        if info.rc == mqtt.MQTT_ERR_SUCCESS:

            self.logger.debug(f"Published message: {message}")
            return True

        elif info.is_published():

            self.logger.debug(f"Published message: {message}")
            return True

        else:

            self.logger.warning(f"Failed to publish message: {message}")
            return False
