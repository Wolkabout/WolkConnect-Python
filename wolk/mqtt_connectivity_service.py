"""Connectivity service based on MQTT protocol."""
#   Copyright 2020 WolkAbout Technology s.r.o.
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
from threading import Lock
from time import sleep
from time import time
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from paho.mqtt import client as mqtt

from wolk import logger_factory
from wolk.interface.connectivity_service import ConnectivityService
from wolk.model.device import Device
from wolk.model.message import Message

MQTT_KEEP_ALIVE_INTERVAL = 90


class MQTTConnectivityService(ConnectivityService):
    """Handle sending and receiving MQTT messages."""

    def __init__(
        self,
        device: Device,
        topics: List[str],
        qos: int = 2,
        host: str = "insert_host",
        port: int = 80, # TODO: insert port
        max_retries: int = 3,
        ca_cert: Optional[str] = None,
    ) -> None:
        """
        Provide the connection to the WolkAbout IoT Platform.

        :param device: Contains device key and password used for authentication
        :type device: Device
        :param topics: List of topics to subscribe to
        :type topics: List[str]
        :param max_retries: Number of retries when unexpected disconnect occurs
        :type max_retries: int
        :param qos: Quality of Service for MQTT connection (0, 1, 2)
        :type qos: int
        :param host: Address of the MQTT broker
        :type host: str
        :param port: Port to which to send messages
        :type port: int
        :param ca_cert: Path to certificate file used to encrypt the connection
        :type ca_cert: str or None
        """
        self.device = device
        self.qos = qos
        self.host = host
        self.port = port
        self.max_retries = max_retries
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
            f"QoS: {self.qos} ; "
            f"Host: {self.host} ; "
            f"Port: {self.port} ; "
            f"CA certificate: {self.ca_cert}"
        )
        self.client = mqtt.Client(
            client_id=self.device.key, clean_session=True
        )
        self.inbound_message_listener: Callable[
            [Message], None
        ] = lambda message: print("\n\nNo inbound message listener set!\n\n")
        self.timeout: Optional[int] = None
        self.timeout_interval = 10
        self.mutex = Lock()

    def is_connected(self) -> bool:
        """
        Return current connection state.

        :returns: connected
        :rtype: bool
        """
        return self.connected

    def set_inbound_message_listener(
        self, listener: Callable[[Message], None]
    ) -> None:
        """
        Set the callback function to handle inbound messages.

        :param listener: Function that handles inbound messages
        :type listener: Callable[[Message], None]
        """
        self.logger.debug(f"Message listener set to: {listener}")
        self.inbound_message_listener = listener

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

        self.mutex.acquire()

        self.client.on_connect = self._on_mqtt_connect
        self.client.on_disconnect = self._on_mqtt_disconnect
        self.client.on_message = self._on_mqtt_message
        if self.ca_cert:
            try:
                self.client.tls_set(self.ca_cert)
                self.client.tls_insecure_set(True)
            except ValueError:
                pass  # Ignore previously set TLS error
            except Exception as exception:
                self.logger.exception(
                    f"Something went wrong when setting TLS: {exception}"
                )
                self.mutex.release()
                return False
        self.client.username_pw_set(self.device.key, self.device.password)

        self.logger.debug(
            f"Connecting with parameters: host='{self.host}', "
            f"port={self.port}, ca_cert='{self.ca_cert}', "
            f"username='{self.device.key}', "
            f"password='{self.device.password}'"
        )
        try:
            self.client.connect(
                self.host, self.port, keepalive=MQTT_KEEP_ALIVE_INTERVAL
            )
        except Exception as exception:
            self.logger.exception(
                f"Something went wrong while connecting: {exception}"
            )
            self.mutex.release()
            return False

        self.client.loop_start()

        self.timeout = round(time()) + self.timeout_interval

        while True:

            if round(time()) > self.timeout:
                self.logger.warning("Connection timed out!")
                self.timeout = None
                self.mutex.release()
                return False

            if self.connected_rc is None:
                sleep(0.1)
                continue

            if self.connected_rc == 0:
                self.logger.info("Connected!")
                self.timeout = None
                self.connected_rc = None
                break

            if self.connected_rc == 1:
                self.logger.warning(
                    "Connection refused - incorrect protocol version"
                )
                self.connected_rc = None
                self.timeout = None
                self.mutex.release()
                return False

            if self.connected_rc == 2:
                self.logger.warning(
                    "Connection refused - invalid client identifier"
                )
                self.connected_rc = None
                self.timeout = None
                self.mutex.release()
                return False

            if self.connected_rc == 3:
                self.logger.warning("Connection refused - server unavailable")
                self.timeout = None
                self.connected_rc = None
                self.mutex.release()
                return False

            if self.connected_rc == 4:
                self.logger.warning(
                    "Connection refused - bad username or password"
                )
                self.connected_rc = None
                self.timeout = None
                self.mutex.release()
                return False

            if self.connected_rc == 5:
                self.logger.warning("Connection refused - not authorised")
                self.connected_rc = None
                self.timeout = None
                self.mutex.release()
                return False

            if self.connected_rc not in list(range(6)):
                self.logger.warning("Unknown retun code")
                self.connected_rc = None
                self.timeout = None
                self.mutex.release()
                return False

        self.logger.debug(f"Subscribing to topics: {self.topics}")
        for topic in self.topics:
            self.client.subscribe(topic, 2)
        self.mutex.release()
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnects the device from the WolkAbout IoT Platform."""
        self.logger.info("Disconnecting")
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
        if not self.connected:
            self.logger.warning(
                f"Not connected, unable to publish message: {message}"
            )
            return False
        self.mutex.acquire()

        info = self.client.publish(message.topic, message.payload, self.qos)

        if info.rc == mqtt.MQTT_ERR_SUCCESS:
            self.logger.debug(f"Published message: {message}")
            self.mutex.release()
            return True

        if info.is_published():
            self.logger.debug(f"Published message: {message}")
            self.mutex.release()
            return True

        self.logger.warning(f"Failed to publish message: {message}")
        self.mutex.release()
        return False

    def _on_mqtt_message(
        self, _client: mqtt.Client, _userdata: Any, message: mqtt.MQTTMessage
    ) -> None:
        """
        Serialize inbound messages and pass them to inbound message listener.

        :param _client: Client that received the message
        :type _client: paho.mqtt.Client
        :param _userdata: Private user data set in Client()
        :type _userdata: str
        :param message: Class with members: topic, payload, qos, retain.
        :type message: paho.mqtt.MQTTMessage
        """
        if not message:
            return
        received_message = Message(message.topic, message.payload)
        if "binary" in received_message.topic:  # To skip printing file binary
            self.logger.debug(
                "Received MQTT message: "
                f"{received_message.topic} , "
                f"size: {len(received_message.payload)} bytes"
            )
        else:
            self.logger.debug(f"Received MQTT message: {received_message}")
        self.inbound_message_listener(received_message)

    def _on_mqtt_connect(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        _flags: int,
        return_code: int,
    ) -> None:
        """
        Handle when the client receives a CONNACK response from the server.

        :param _client: Client that received the message
        :type _client: paho.mqtt.Client
        :param _userdata: private user data set in Client()
        :type _userdata: str
        :param _flags: Response flags sent by the broker
        :type _flags: int
        :param return_code: Connection result
        :type return_code: int
        """
        self.logger.debug(f"Return code: {return_code}")
        if return_code == 0:  # Connection successful

            self.connected = True
            self.connected_rc = 0
            # Subscribing in on_mqtt_connect() means if we lose the connection
            # and reconnect then subscriptions will be renewed.
            if self.topics:
                for topic in self.topics:
                    self.client.subscribe(topic, 2)
            self.logger.debug(f"Connected : {self.connected}")
        elif (
            return_code == 1
        ):  # Connection refused - incorrect protocol version
            self.connected_rc = 1
        elif (
            return_code == 2
        ):  # Connection refused - invalid client identifier
            self.connected_rc = 2
        elif return_code == 3:  # Connection refused - server unavailable
            self.connected_rc = 3
        elif return_code == 4:  # Connection refused - bad username or password
            self.connected_rc = 4
        elif return_code == 5:  # Connection refused - not authorised
            self.connected_rc = 5

    def _on_mqtt_disconnect(
        self, _client: mqtt.Client, _userdata: Any, return_code: int
    ) -> None:
        """
        Handle when the client disconnects from the broker.

        :param _client: Client that received the message
        :type _client: paho.mqtt.Client
        :param _userdata: private user data set in Client()
        :type _userdata: str
        :param return_code: Disconnection result
        :type return_code: int
        """
        self.connected = False
        self.connected_rc = return_code
        self.logger.debug(
            f"Connected : {self.connected} ;" + f" Return code : {return_code}"
        )
        if return_code not in [0, 5]:
            self.logger.warning("Unexpected disconnect!")
            retries = 0
            while retries < self.max_retries:
                try:
                    self.logger.info("Attempting to reconnect..")
                    self.client.reconnect()
                    return
                except Exception as e:
                    retries += 1
                    self.logger.exception(f"Reconnect failed: {e}")
                    self.logger.info("Retrying in 5 seconds..")
                    sleep(5)
            self.logger.warning("Failed to reconnect")
