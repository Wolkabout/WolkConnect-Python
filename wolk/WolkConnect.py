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
from wolk.JsonSingleOutboundMessageFactory import JsonSingleOutboundMessageFactory
from wolk.JsonSingleInboundMessageDeserializer import (
    JsonSingleInboundMessageDeserializer
)
from wolk.JsonProtocolOutboundMessageFactory import JsonProtocolOutboundMessageFactory
from wolk.JsonProtocolInboundMessageDeserializer import (
    JsonProtocolInboundMessageDeserializer
)
from wolk.OSFirmwareUpdate import OSFirmwareUpdate
from wolk.OSKeepAliveService import OSKeepAliveService
from wolk.LoggerFactory import logger_factory
from wolk.models.SensorReading import SensorReading
from wolk.models.Alarm import Alarm
from wolk.models.ActuatorCommandType import ActuatorCommandType
from wolk.models.ActuatorStatus import ActuatorStatus
from wolk.models.ConfigurationCommandType import ConfigurationCommandType
from wolk.models.FirmwareCommandType import FirmwareCommandType
from wolk.models.FirmwareStatus import FirmwareStatus
from wolk.models.FirmwareStatusType import FirmwareStatusType
from wolk.models.FirmwareErrorType import FirmwareErrorType
from wolk.models.Protocol import Protocol
from wolk.interfaces.ActuationHandler import ActuationHandler
from wolk.interfaces.ActuatorStatusProvider import ActuatorStatusProvider
from wolk.interfaces.ConfigurationHandler import ConfigurationHandler
from wolk.interfaces.ConfigurationProvider import ConfigurationProvider
from wolk.interfaces.OutboundMessageFactory import OutboundMessageFactory
from wolk.interfaces.OutboundMessageQueue import OutboundMessageQueue
from wolk.interfaces.InboundMessageDeserializer import InboundMessageDeserializer
from wolk.interfaces.ConnectivityService import ConnectivityService


class WolkConnect:
    """
    Exchange data with WolkAbout IoT Platform.

    :ivar connectivity_service: Means of sending/receiving data
    :vartype connectivity_service: wolk.OSMQTTConnectivityService.OSMQTTConnectivityService
    :ivar inbound_message_deserializer: Deserializer of inbound messages
    :vartype inbound_message_deserializer: wolk.JsonSingleInboundMessageDeserializer.JsonSingleInboundMessageDeserializer
    :ivar device: Contains device key and password, and actuator references
    :vartype device: wolk.models.Device.Device
    :ivar firmware_update: Firmware update handler
    :vartype firmware_update: wolk.OSFirmwareUpdate.OSFirmwareUpdate
    :ivar keep_alive_service: Keep device connected when not sending data
    :vartype keep_alive_service: wolk.OSKeepAliveService.OSKeepAliveService
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar outbound_message_factory: Create messages to send
    :vartype outbound_message_factory: wolk.JsonSingleOutboundMessageFactory.JsonSingleOutboundMessageFactory
    :ivar outbound_message_queue: Store data before sending
    :vartype outbound_message_queue: wolk.interfaces.OutboundMessageQueue.OutboundMessageQueue
    """

    def __init__(
        self,
        device,
        protocol=Protocol.JSON_SINGLE,
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
        outbound_message_factory=None,
        inbound_message_deserializer=None,
        connectivity_service=None,
    ):
        """
        Provide communication with WolkAbout IoT Platform.

        :param device: Contains key and password, and actuator references
        :type device:  wolk.models.Device.Device
        :param actuation_handler: Handle actuation commands
        :type actuation_handler: wolk.interfaces.ActuationHandler.ActuationHandler or None
        :param actuator_status_provider: Read actuator status
        :type actuator_status_provider:  wolk.interfaces.ActuatorStatusProvider.ActuatorStatusProvider or None
        :param outbound_message_queue: Store messages before sending
        :type outbound_message_queue: wolk.interfaces.OutboundMessageQueue.OutboundMessageQueue or None
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
        :param outbound_message_factory: Creator of messages to be sent
        :type outbound_message_factory: wolk.interfaces.OutboundMessageFactory.OutboundMessageFactory or None
        :param inbound_message_deserializer: Deserializer of messages from the Platform
        :type inbound_message_deserializer: wolk.interfaces.InboundMessageDeserializer.InboundMessageDeserializer or None
        :param connectivity_service: Provider of connection to Platform
        :type connectivity_service: wolk.interfaces.ConnectivityService.ConnectivityService or None
        """
        self.logger = logger_factory.get_logger(str(self.__class__.__name__))
        self.logger.debug(
            "Init:  Device: %s ; Actuation handler: %s ; "
            "Actuator status provider: %s ; "
            "Configuration handler: %s ; Configuration provider: %s ; "
            "Outbound message queue: %s ; Keep alive enabled: %s ;"
            " Firmware handler: %s"
            "Host: %s ; Port: %s ; ca_cert: %s "
            "Outbound message factory: %s ; "
            "Inbound message deserializer: %s ; "
            "Connectivity Service: %s",
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
            outbound_message_factory,
            inbound_message_deserializer,
            connectivity_service,
        )

        self.device = device

        if actuation_handler is None:
            self.actuation_handler = None
        else:
            if not isinstance(actuation_handler, ActuationHandler):
                raise RuntimeError("Invalid actuation handler provided")
            else:
                self.actuation_handler = actuation_handler

        if actuator_status_provider is None:
            self.actuator_status_provider = None
        else:
            if not isinstance(actuator_status_provider, ActuatorStatusProvider):
                raise RuntimeError("Invalid actuator status provider provided")
            else:
                self.actuator_status_provider = actuator_status_provider

        if configuration_handler is None:
            self.configuration_handler = None
        else:
            if not isinstance(configuration_handler, ConfigurationHandler):
                raise RuntimeError("Invalid configuration handler provided")
            else:
                self.configuration_handler = configuration_handler

        if configuration_provider is None:
            self.configuration_provider = None
        else:
            if not isinstance(configuration_provider, ConfigurationProvider):
                raise RuntimeError("Invalid configuration provider provided")
            else:
                self.configuration_provider = configuration_provider

        if outbound_message_queue is None:
            self.outbound_message_queue = OSOutboundMessageQueue()
        else:
            if not isinstance(outbound_message_queue, OutboundMessageQueue):
                raise RuntimeError("Invalid outbound message queue provided")
            else:
                self.outbound_message_queue = outbound_message_queue

        if (
            outbound_message_factory is None
            and inbound_message_deserializer is not None
        ) or (
            outbound_message_factory is not None
            and inbound_message_deserializer is None
        ):
            raise RuntimeError(
                "Both OutboundMessageFactory and "
                "InboundMessageDeserializer must be provided"
            )

        if protocol == Protocol.JSON_SINGLE:
            if outbound_message_factory is None:
                self.outbound_message_factory = JsonSingleOutboundMessageFactory(
                    device.key
                )
            else:
                if not isinstance(outbound_message_factory, OutboundMessageFactory):
                    raise RuntimeError("Invalid outbound message factory provided")
                else:
                    self.outbound_message_factory = outbound_message_factory

            if inbound_message_deserializer is None:
                self.inbound_message_deserializer = JsonSingleInboundMessageDeserializer(
                    self.device
                )
            else:
                if not isinstance(
                    inbound_message_deserializer, InboundMessageDeserializer
                ):
                    raise RuntimeError("Invalid inbound message deserializer provided")
                else:
                    self.inbound_message_deserializer = inbound_message_deserializer

        elif protocol == Protocol.JSON_PROTOCOL:
            if outbound_message_factory is None:
                self.outbound_message_factory = JsonProtocolOutboundMessageFactory(
                    device.key
                )
            else:
                if not isinstance(outbound_message_factory, OutboundMessageFactory):
                    raise RuntimeError("Invalid outbound message factory provided")
                else:
                    self.outbound_message_factory = outbound_message_factory

            if inbound_message_deserializer is None:
                self.inbound_message_deserializer = JsonProtocolInboundMessageDeserializer(
                    self.device
                )
            else:
                if not isinstance(
                    inbound_message_deserializer, InboundMessageDeserializer
                ):
                    raise RuntimeError("Invalid inbound message deserializer provided")
                else:
                    self.inbound_message_deserializer = inbound_message_deserializer
        else:
            raise RuntimeError("Unknown protocol specified - ", protocol)

        wolk_ca_cert = os.path.join(os.path.dirname(__file__), "ca.crt")

        if host and port and ca_cert:
            self.connectivity_service = OSMQTTConnectivityService(
                device,
                self.inbound_message_deserializer.inbound_topics,
                host=host,
                port=int(port),
                ca_cert=ca_cert,
            )
        elif host and port:
            self.connectivity_service = OSMQTTConnectivityService(
                device,
                self.inbound_message_deserializer.inbound_topics,
                host=host,
                port=int(port),
            )
        else:
            if connectivity_service is not None:
                if not isinstance(connectivity_service, ConnectivityService):
                    raise RuntimeError("Invalid connectivity service provided")
                else:
                    self.connectivity_service = connectivity_service
            else:
                self.connectivity_service = OSMQTTConnectivityService(
                    device,
                    self.inbound_message_deserializer.inbound_topics,
                    ca_cert=wolk_ca_cert,
                )

        self.connectivity_service.set_inbound_message_listener(self._on_inbound_message)

        if keep_alive_enabled and protocol == Protocol.JSON_SINGLE:
            keep_alive_interval_seconds = 600
            self.logger.debug(
                "Keep alive enabled, interval: %s", keep_alive_interval_seconds
            )
            self.keep_alive_service = OSKeepAliveService(
                self.connectivity_service,
                self.outbound_message_factory,
                keep_alive_interval_seconds,
            )
        else:
            self.keep_alive_service = None

        self.firmware_update = OSFirmwareUpdate(firmware_handler)

        self.firmware_update.set_on_file_packet_request_callback(
            self._on_packet_request
        )
        self.firmware_update.set_on_status_callback(self._on_status)

        if device.actuator_references and (
            actuation_handler is None or actuator_status_provider is None
        ):
            raise RuntimeError(
                "Both ActuatorStatusProvider and ActuationHandler "
                "must be provided for device with actuators."
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
            self.connectivity_service.connect()
            if self.keep_alive_service:
                self.keep_alive_service.start()
            self.logger.debug("connect ended")

        except Exception as e:

            raise e

    def disconnect(self):
        """Disconnect the device from WolkAbout IoT Platform."""
        self.logger.debug("disconnect started")
        self.connectivity_service.disconnect()
        if self.keep_alive_service:
            self.keep_alive_service.stop()
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
        reading = SensorReading(reference, value, timestamp)
        outbound_message = self.outbound_message_factory.make_from_sensor_reading(
            reading
        )
        self.outbound_message_queue.put(outbound_message)
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
        alarm = Alarm(reference, active, timestamp)
        outbound_message = self.outbound_message_factory.make_from_alarm(alarm)
        self.outbound_message_queue.put(outbound_message)
        self.logger.debug("add_alarm ended")

    def publish(self):
        """Publish all currently stored messages to WolkAbout IoT Platform."""
        self.logger.debug("publish started")
        while True:
            outbound_message = self.outbound_message_queue.peek()

            if outbound_message is None:
                break

            if self.connectivity_service.publish(outbound_message) is True:
                self.outbound_message_queue.get()
            else:
                self.logger.warning(
                    "Failed to publish message: ",
                    outbound_message.topic,
                    outbound_message.payload,
                )
                break
        self.logger.debug("publish ended")

    def publish_actuator_status(self, reference):
        """
        Publish the current actuator status to WolkAbout IoT Platform.

        :param reference: reference of the actuator
        :type reference: str
        """
        self.logger.debug("publish_actuator_status started")
        state, value = self.actuator_status_provider.get_actuator_status(reference)
        actuator_status = ActuatorStatus(reference, state, value)
        outbound_message = self.outbound_message_factory.make_from_actuator_status(
            actuator_status
        )

        if not self.connectivity_service.publish(outbound_message):
            self.outbound_message_queue.put(outbound_message)
        self.logger.debug("publish_actuator_status ended")

    def publish_configuration(self):
        """Publish current device configuration to WolkAbout IoT Platform."""
        self.logger.debug("publish_configuration started")
        configuration = self.configuration_provider.get_configuration()
        outbound_message = self.outbound_message_factory.make_from_configuration(
            configuration
        )

        if not self.connectivity_service.publish(outbound_message):
            self.outbound_message_queue.put(outbound_message)
        self.logger.debug("publish_configuration ended")

    def _on_inbound_message(self, message):
        """
        Handle inbound messages.

        :param message: message received from the platform
        :type message: wolk.models.InboundMessage.InboundMessage
        """
        self.logger.debug("_on_inbound_message started")

        if self.inbound_message_deserializer.is_actuation_command(message):

            if not self.actuation_handler or not self.actuator_status_provider:
                return

            actuation = self.inbound_message_deserializer.deserialize_actuator_command(
                message
            )

            if actuation.command == ActuatorCommandType.SET:

                self.actuation_handler.handle_actuation(
                    actuation.reference, actuation.value
                )

                self.publish_actuator_status(actuation.reference)

            elif actuation.command == ActuatorCommandType.STATUS:

                self.publish_actuator_status(actuation.reference)

        elif self.inbound_message_deserializer.is_configuration(message):

            if not self.configuration_provider or not self.configuration_handler:
                return

            configuration = self.inbound_message_deserializer.deserialize_configuration_command(
                message
            )

            if configuration.command == ConfigurationCommandType.SET:
                self.configuration_handler.handle_configuration(configuration.values)
                self.publish_configuration()

            elif configuration.command == ConfigurationCommandType.CURRENT:
                self.publish_configuration()

        elif self.inbound_message_deserializer.is_firmware_command(message):

            if not self.firmware_update:
                # Firmware update disabled
                firmware_status = FirmwareStatus(
                    FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
                )
                outbound_message = self.outbound_message_factory.make_from_firmware_status(
                    firmware_status
                )
                if not self.connectivity_service.publish(outbound_message):
                    self.outbound_message_queue.put(outbound_message)
                return

            firmware_command = self.inbound_message_deserializer.deserialize_firmware_command(
                message
            )

            if firmware_command.command == FirmwareCommandType.FILE_UPLOAD:

                self.firmware_update.handle_file_upload(firmware_command)

            elif firmware_command.command == FirmwareCommandType.URL_DOWNLOAD:

                self.firmware_update.handle_url_download(firmware_command)

            elif firmware_command.command == FirmwareCommandType.INSTALL:

                self.firmware_update.handle_install()

            elif firmware_command.command == FirmwareCommandType.ABORT:

                self.firmware_update.handle_abort()

            elif firmware_command.command == FirmwareCommandType.UNKNOWN:
                pass

        elif self.inbound_message_deserializer.is_file_chunk(message):

            if not self.firmware_update:
                # Firmware update disabled
                firmware_status = FirmwareStatus(
                    FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
                )
                outbound_message = self.outbound_message_factory.make_from_firmware_status(
                    firmware_status
                )
                if not self.connectivity_service.publish(outbound_message):
                    self.outbound_message_queue.put(outbound_message)
                return

            packet = self.inbound_message_deserializer.deserialize_firmware_chunk(
                message
            )
            self.firmware_update.handle_packet(packet)

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
        message = self.outbound_message_factory.make_from_chunk_request(
            file_name, chunk_index, chunk_size
        )
        if not self.connectivity_service.publish(message):
            self.outbound_message_queue.put(message)
        self.logger.debug("_on_packet_request ended")

    def _on_status(self, status):
        """
        Report firmware update status to WolkAbout IoT Platform.

        :param status: The status to be reported to the platform
        :type status: wolk.models.FirmwareStatus.FirmwareStatus
        """
        self.logger.debug("_on_status started")
        message = self.outbound_message_factory.make_from_firmware_status(status)
        if not self.connectivity_service.publish(message):
            self.outbound_message_queue.put(message)
        self.logger.debug("_on_status ended")
