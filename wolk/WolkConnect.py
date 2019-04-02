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
"""
WolkConnect Module.
"""
import os

from wolk.OSOutboundMessageQueue import OSOutboundMessageQueue
from wolk.OSMQTTConnectivityService import OSMQTTConnectivityService
from wolk.OSOutboundMessageFactory import OSOutboundMessageFactory
from wolk.OSInboundMessageDeserializer import OSInboundMessageDeserializer
from wolk.OSFirmwareUpdate import OSFirmwareUpdate
from wolk.OSKeepAliveService import OSKeepAliveService
from wolk.LoggerFactory import logger_factory

from wolk.wolkcore import WolkCore


class WolkConnect:
    """
    Exchange data with WolkAbout IoT Platform.

    :ivar connectivity_service: Means of sending/receiving data
    :vartype connectivity_service: wolk.OSMQTTConnectivityService.OSMQTTConnectivityService
    :ivar deserializer: Deserializer of inbound messages
    :vartype deserializer: wolk.OSInboundMessageDeserializer.OSInboundMessageDeserializer
    :ivar device: Contains device key and password, and actuator references
    :vartype device: wolk.Device.Device
    :ivar firmware_update: Firmware update handler
    :vartype firmware_update: wolk.OSFirmwareUpdate.OSFirmwareUpdate
    :ivar keep_alive_service: Keep device connected when not sending data
    :vartype keep_alive_service: wolk.OSKeepAliveService.OSKeepAliveService
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar outbound_message_factory: Create messages to send
    :vartype outbound_message_factory: wolk.OSOutboundMessageFactory.OSOutboundMessageFactory
    :ivar outbound_message_queue: Store data before sending
    :vartype outbound_message_queue: wolk.wolkcore.OutboundMessageQueue.OutboundMessageQueue
    """

    def __init__(
        self,
        device,
        actuation_handler=None,
        actuator_status_provider=None,
        configuration_handler=None,
        configuration_provider=None,
        outbound_message_queue=None,
        keep_alive_enabled=True,
        firmware_handler=None,
        host=None,
        port=None,
        ca_cert=None,
    ):
        """
        Provide communication with WolkAbout IoT Platform.

        :param device: Contains key and password, and actuator references
        :type device:  wolk.Device.Device
        :param actuation_handler: Handle actuation commands
        :type actuation_handler: wolk.ActuationHandler.ActuationHandler or None
        :param actuator_status_provider: Read actuator status
        :type actuator_status_provider:  wolk.ActuatorStatusProvider.ActuatorStatusProvider or None
        :param outbound_message_queue: Store messages before sending
        :type outbound_message_queue: wolk.wolkcore.OutboundMessageQueue.OutboundMessageQueue or None
        :param keep_alive_enabled: Enable or disable the keep alive service
        :type keep_alive_enabled: bool
        :param firmware_handler: Firmware update support
        :type firmware_handler: wolk.FileSystemFirmwareHandler.FileSystemFirmwareHandler or None
        :param host: Host name or IP address of the remote broker
        :type host: str or None
        :param port: Network port of the server host to connect to
        :type port: int or None
        :param ca_cert: String path to Certificate Authority certificate file
        :type ca_cert: str or None
        """
        self.logger = logger_factory.get_logger(str(self.__class__.__name__))
        self.logger.debug(
            "Init:  Device: %s ; Actuation handler: %s ; "
            "Actuator status provider: %s ; "
            "Configuration handler: %s ; Configuration provider: %s ; "
            "Outbound message queue: %s ; Keep alive enabled: %s ;"
            " Firmware handler: %s"
            "Host: %s ; Port: %s ; ca_cert: %s",
            device,
            actuation_handler,
            actuator_status_provider,
            configuration_handler,
            configuration_provider,
            outbound_message_queue,
            keep_alive_enabled,
            firmware_handler,
            host,
            port,
            ca_cert,
        )
        self.device = device
        self.outbound_message_factory = OSOutboundMessageFactory(device.key)
        if outbound_message_queue is None:
            self.outbound_message_queue = OSOutboundMessageQueue()
        else:
            self.outbound_message_queue = outbound_message_queue

        wolk_ca_cert = os.path.join(os.path.dirname(__file__), "ca.crt")

        if host and port and ca_cert:
            self.connectivity_service = OSMQTTConnectivityService(
                device, host=host, port=int(port), ca_cert=ca_cert
            )
        elif host and port:
                self.connectivity_service = OSMQTTConnectivityService(
                    device, host=host, port=int(port)
                )
        else:
            self.connectivity_service = OSMQTTConnectivityService(
                device, ca_cert=wolk_ca_cert
            )
        self.deserializer = OSInboundMessageDeserializer()
        self.firmware_update = OSFirmwareUpdate(firmware_handler)

        self.keep_alive_service = None
        if keep_alive_enabled:
            keep_alive_interval_seconds = 600
            self.logger.debug(
                "Keep alive enabled, interval: %s", keep_alive_interval_seconds
            )
            self.keep_alive_service = OSKeepAliveService(
                self.connectivity_service,
                self.outbound_message_factory,
                keep_alive_interval_seconds,
            )

        if device.actuator_references and (
            actuation_handler is None or actuator_status_provider is None
        ):
            raise RuntimeError(
                "Both ActuatorStatusProvider and ActuationHandler "
                "must be provided for device with actuators."
            )

        self._wolk = WolkCore(
            self.outbound_message_factory,
            self.outbound_message_queue,
            self.connectivity_service,
            actuation_handler,
            actuator_status_provider,
            self.deserializer,
            configuration_handler,
            configuration_provider,
            self.keep_alive_service,
            self.firmware_update,
        )

        if firmware_handler:

            message = self.outbound_message_factory.make_from_firmware_version(
                firmware_handler.version
            )
            self.outbound_message_queue.put(message)

        self.firmware_update.report_result()

    def connect(self):
        """
        Connect the device to the WolkAbout IoT Platform.

        :raises e: Exception from MQTT client
        """
        try:

            self.logger.debug("connect started")
            self._wolk.connect()
            self.logger.debug("connect ended")

        except Exception as e:

            raise e

    def disconnect(self):
        """Disconnect the device from WolkAbout IoT Platform."""
        self.logger.debug("disconnect started")
        self._wolk.disconnect()
        self.logger.debug("disconnect ended")

    def add_sensor_reading(self, reference, value, timestamp=None):
        """
        Publish a sensor reading to WolkAbout IoT Platform.

        :param reference: The reference of the sensor
        :type reference: str
        :param value: The value of the sensor reading
        :type value: int or float or str
        :param timestamp: Unix timestamp. If not provided, platform will assign
        :type timestamp: int or None
        """
        self.logger.debug("add_sensor_reading started")
        self._wolk.add_sensor_reading(reference, value, timestamp)
        self.logger.debug("add_sensor_reading ended")

    def add_alarm(self, reference, active, timestamp=None):
        """
        Publish an alarm to WolkAbout IoT Platform.

        :param reference: Reference of the alarm
        :type reference: str
        :param active: Current state of the alarm
        :type active: bool
        :param timestamp: Unix timestamp. If not provided, platform will assign
        :type timestamp: int or None
        """
        self.logger.debug("add_alarm started")
        self._wolk.add_alarm(reference, active, timestamp)
        self.logger.debug("add_alarm ended")

    def publish(self):
        """Publish all currently stored messages to WolkAbout IoT Platform."""
        self.logger.debug("publish started")

        self._wolk.publish()
        self.logger.debug("publish ended")

    def publish_actuator_status(self, reference):
        """
        Publish the current actuator status to WolkAbout IoT Platform.

        :param reference: reference of the actuator
        :type reference: str
        """
        self.logger.debug("publish_actuator_status started")
        self._wolk.publish_actuator_status(reference)
        self.logger.debug("publish_actuator_status ended")

    def publish_configuration(self):
        """Publish current device configuration to WolkAbout IoT Platform."""
        self.logger.debug("publish_configuration started")
        self._wolk.publish_configuration()
        self.logger.debug("publish_configuration ended")

    def _on_inbound_message(self, message):
        """
        Handle inbound messages.

        :param message: message received from the platform
        :type message: wolk.wolkcore.InboundMessage.InboundMessage
        """
        self.logger.debug("_on_inbound_message started")
        self._wolk._on_inbound_message(message)
        self.logger.debug("_on_inbound_message ended")

    def _on_packet_request(self, file_name, chunk_index, chunk_size):
        """
        Handle firmware packet requests.

        :param file_name: The name of the file to which the chunk belongs
        :type file_name: str
        :param chunk_index: The index of the requested chunk
        :type chunk_index: int
        :param chunk_size: The size of the requested chunk
        :type chunk_size: int
        """
        self.logger.debug("_on_packet_request started")
        self._wolk._on_packet_request(file_name, chunk_index, chunk_size)
        self.logger.debug("_on_packet_request ended")

    def _on_status(self, status):
        """
        Report firmware update status to WolkAbout IoT Platform.

        :param status: The status to be reported to the platform
        :type status: wolk.wolkcore.FirmwareStatus.FirmwareStatus
        """
        self.logger.debug("_on_status started")
        self._wolk._on_status(status)
        self.logger.debug("_on_status ended")
