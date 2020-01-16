"""Heart and soul of this library. Wraps in all functionality."""
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
import os
from inspect import signature
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

from wolk import logger_factory
from wolk.interface.connectivity_service import ConnectivityService
from wolk.interface.file_management import FileManagement
from wolk.interface.firmware_update import FirmwareUpdate
from wolk.interface.message_deserializer import MessageDeserializer
from wolk.interface.message_factory import MessageFactory
from wolk.interface.message_queue import MessageQueue
from wolk.message_deque import MessageDeque
from wolk.model.actuator_command import ActuatorCommandType
from wolk.model.actuator_state import ActuatorState
from wolk.model.actuator_status import ActuatorStatus
from wolk.model.alarm import Alarm
from wolk.model.configuration_command import ConfigurationCommandType
from wolk.model.device import Device
from wolk.model.file_management_error_type import FileManagementErrorType
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.firmware_update_error_type import FirmwareUpdateErrorType
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.firmware_update_status_type import FirmwareUpdateStatusType
from wolk.model.message import Message
from wolk.model.sensor_reading import SensorReading
from wolk.mqtt_connectivity_service import MQTTConnectivityService as MQTTCS
from wolk.wolkabout_protocol_message_deserializer import (
    WolkAboutProtocolMessageDeserializer as WAPMDeserializer,
)
from wolk.wolkabout_protocol_message_factory import (
    WolkAboutProtocolMessageFactory as WAPMFactory,
)

ConfigurationValue = Union[
    bool,
    int,
    Tuple[int, int],
    Tuple[int, int, int],
    float,
    Tuple[float, float],
    Tuple[float, float, float],
    str,
    Tuple[str, str],
    Tuple[str, str, str],
]


class WolkConnect:
    """
    Exchange data with WolkAbout IoT Platform.

    :ivar actuation_handler: Function for handling actuation commands
    :vartype actuation_handler: Callable[[str, Union[bool, int, float, str]], None] or None
    :ivar actuator_status_provider: Function for getting current actuator status
    :vartype actuator_status_provider: Callable[[str], Tuple[ActuatorState, Union[bool, int, float, str]]] or None
    :ivar configuration_handler: Function for handling configuration commands
    :vartype configuration_handler: Callable[[dict], None] or None
    :ivar configuration_provider: Function for getting current configuration options
    :vartype configuration_provider: Callable[[None], dict] or None
    :ivar connectivity_service: Means of sending/receiving data
    :vartype connectivity_service: ConnectivityService
    :ivar device: Contains device key and password, and actuator references
    :vartype device: Device
    :ivar firmware_update: Firmware update handler
    :vartype firmware_update: FirmwareUpdate or None
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar message_deserializer: Deserializer of inbound messages
    :vartype message_deserializer: MessageDeserializer
    :ivar message_factory: Create messages to send
    :vartype message_factory: MessageFactory
    :ivar message_queue: Store data before sending
    :vartype message_queue: MessageQueue
    """

    def __init__(
        self,
        device: Device,
        actuation_handler: Optional[
            Callable[[str, Union[bool, int, float, str]], None]
        ] = None,
        actuator_status_provider: Optional[
            Callable[
                [str],
                Tuple[ActuatorState, Optional[Union[bool, int, float, str]]],
            ]
        ] = None,
        configuration_handler: Optional[
            Callable[[Dict[str, ConfigurationValue]], None]
        ] = None,
        configuration_provider: Optional[
            Callable[[None], Dict[str, ConfigurationValue]]
        ] = None,
        file_management: Optional[FileManagement] = None,
        firmware_update: Optional[FirmwareUpdate] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        ca_cert: Optional[str] = None,
        message_queue: Optional[MessageQueue] = None,
        message_factory: Optional[MessageFactory] = None,
        message_deserializer: Optional[MessageDeserializer] = None,
        connectivity_service: Optional[ConnectivityService] = None,
    ):
        """
        Provide communication with WolkAbout IoT Platform.

        :param device: Contains key and password, and actuator references
        :type device: Device
        :param actuation_handler: Handle actuation commands
        :type actuation_handler: Callable[[str, Union[bool, int, float, str]], None], optional
        :param actuator_status_provider: Read actuator status
        :type actuator_status_provider: Callable[[str], Tuple[ActuatorState, Union[bool, int, float, str]]], optional
        :param configuration_handler: Handle configuration commands
        :type configuration_handler: Callable[[dict], None], optional
        :param configuration_provider: Read configuration options
        :type configuration_provider: Callable[[None], dict], optional
        :param file_management: File transfer, list files on device, delete files
        :type file_management: FileManagement, optional
        :param firmware_update: Firmware update support
        :type firmware_update: FirmwareUpdate, optional
        :param host: Host name or IP address of the remote broker
        :type host: str, optional
        :param port: Network port of the server host to connect to
        :type port: int, optional
        :param ca_cert: String path to Certificate Authority certificate file
        :type ca_cert: str, optional
        :param message_queue: Store messages before sending
        :type message_queue: MessageQueue, optional
        :param message_factory: Creator of messages to be sent
        :type message_factory: MessageFactory, optional
        :param message_deserializer: Deserializer of messages from the Platform
        :type message_deserializer: MessageDeserializer, optional
        :param connectivity_service: Provider of connection to Platform
        :type connectivity_service: ConnectivityService, optional
        """
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(
            f"Device: {device} ; "
            f"Actuation handler: {actuation_handler} ; "
            f"Actuator status provider: {actuator_status_provider} ; "
            f"Configuration handler: {configuration_handler} ; "
            f"Configuration provider: {configuration_provider} ; "
            f"Message queue: {message_queue} ; "
            f"Firmware update: {firmware_update} ; "
            f"File management: {file_management} ; "
            f"Host: {host} ; Port: {port} ; ca_cert: {ca_cert} "
            f"Message factory: {message_factory} ; "
            f"Message deserializer: {message_deserializer} ; "
            f"Connectivity Service: {connectivity_service}"
        )

        self.device = device

        if actuation_handler is None:
            self.actuation_handler = None
        else:
            if not callable(actuation_handler):
                raise RuntimeError(f"{actuation_handler} is not a callable!")
            if len(signature(actuation_handler).parameters) != 2:
                raise RuntimeError(f"{actuation_handler} invalid signature!")
            else:
                self.actuation_handler = actuation_handler

        if actuator_status_provider is None:
            self.actuator_status_provider = None
        else:
            if not callable(actuator_status_provider):
                raise RuntimeError(
                    f"{actuator_status_provider} is not a callable!"
                )
            if len(signature(actuator_status_provider).parameters) != 1:
                raise RuntimeError(
                    f"{actuator_status_provider} invalid signature!"
                )
            self.actuator_status_provider = actuator_status_provider

        if (
            self.actuation_handler is None
            and self.actuator_status_provider is not None
        ) or (
            self.actuation_handler is not None
            and self.actuator_status_provider is None
        ):
            raise RuntimeError(
                "Provide actuation_handler and actuator_status_provider"
                " to enable actuators on your device!"
            )

        if configuration_handler is not None:
            if not callable(configuration_handler):
                raise RuntimeError(
                    f"{configuration_handler} is not a callable!"
                )
            if len(signature(configuration_handler).parameters) != 1:
                raise RuntimeError(
                    f"{configuration_handler} invalid signature!"
                )
            self.configuration_handler: Optional[
                Callable[[Dict[str, ConfigurationValue]], None]
            ] = configuration_handler
        else:
            self.configuration_handler = None

        if configuration_provider is not None:
            if not callable(configuration_provider):
                raise RuntimeError(
                    f"{configuration_provider} is not a callable!"
                )
            if len(signature(configuration_provider).parameters) != 0:
                raise RuntimeError(
                    f"{configuration_provider} invalid signature!"
                )
            self.configuration_provider: Optional[
                Callable[[None], Dict[str, ConfigurationValue]]
            ] = configuration_provider
        else:
            self.configuration_provider = None

        if (
            self.configuration_handler is None
            and self.configuration_provider is not None
        ) or (
            self.configuration_handler is not None
            and self.configuration_provider is None
        ):
            raise RuntimeError(
                "Provide configuration_handler and configuration_provider"
                " to enable configuration options on your device!"
            )

        if message_queue is None:
            self.message_queue: MessageQueue = MessageDeque()
        else:
            if isinstance(message_queue, MessageQueue):
                self.message_queue = message_queue
            else:
                raise RuntimeError("Invalid message queue provided")

        if (message_factory is None and message_deserializer is not None) or (
            message_factory is not None and message_deserializer is None
        ):
            raise RuntimeError(
                "Both MessageFactory and "
                "MessageDeserializer must be provided"
            )

        if message_factory is None:
            self.message_factory: MessageFactory = WAPMFactory(device.key)
        else:
            if not isinstance(message_factory, MessageFactory):
                raise RuntimeError("Invalid message factory provided")
            else:
                self.message_factory = message_factory

        if message_deserializer is None:
            self.message_deserializer: MessageDeserializer = WAPMDeserializer(
                self.device
            )
        else:
            if not isinstance(message_deserializer, MessageDeserializer):
                raise RuntimeError("Invalid message deserializer provided")
            else:
                self.message_deserializer = message_deserializer

        wolk_ca_cert = os.path.join(os.path.dirname(__file__), "ca.crt")
        last_will_message = self.message_factory.make_last_will_message(
            self.device.key
        )

        if host and port and ca_cert:
            self.connectivity_service: ConnectivityService = MQTTCS(
                device,
                self.message_deserializer.get_inbound_topics(),
                last_will_message,
                host=host,
                port=int(port),
                ca_cert=ca_cert,
            )
        elif host and port:
            self.connectivity_service = MQTTCS(
                device,
                self.message_deserializer.get_inbound_topics(),
                last_will_message,
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
                self.connectivity_service = MQTTCS(
                    device,
                    self.message_deserializer.get_inbound_topics(),
                    last_will_message,
                    ca_cert=wolk_ca_cert,
                )

        self.connectivity_service.set_inbound_message_listener(
            self._on_inbound_message
        )

        if file_management is None:
            self.file_management = None
        else:
            if not isinstance(file_management, FileManagement):
                raise RuntimeError("Invalid file management module provided")
            else:
                self.file_management = file_management
                self.file_management._set_request_file_binary_callback(
                    self._on_package_request
                )
                self.file_management._set_file_upload_status_callback(
                    self._on_file_upload_status
                )
                self.file_management._set_file_url_download_status_callback(
                    self._on_file_url_status
                )

        if firmware_update is None:
            self.firmware_update = None
        else:
            if self.file_management is None:
                raise RuntimeError(
                    "File management must be enabled "
                    "in order for firmware update to work"
                )
            if not isinstance(firmware_update, FirmwareUpdate):
                raise RuntimeError("Invalid firmware update module provided")
            else:
                self.firmware_update = firmware_update
                self.firmware_update._set_on_status_callback(
                    self._on_firmware_update_status
                )

        if device.actuator_references and (
            actuation_handler is None or actuator_status_provider is None
        ):
            raise RuntimeError(
                "Both ActuatorStatusProvider and ActuationHandler "
                "must be provided for device with actuators."
            )

        if self.firmware_update:

            message = self.message_factory.make_from_firmware_version(
                self.firmware_update.get_current_version()
            )
            self.message_queue.put(message)
            self.firmware_update.report_result()

    def connect(self) -> None:
        """
        Connect the device to the WolkAbout IoT Platform.

        If the connection is made, then it also sends information
        regarding current actuator statuses, configuration option values,
        list of files present on device, current firmware version
        and the result of the firmware update process.
        """
        self.logger.debug("Connecting")

        if self.connectivity_service.is_connected():
            self.logger.info("Already connected")
            return

        else:
            try:
                self.connectivity_service.connect()
            except Exception as e:
                self.logger.exception(
                    f"Something went wrong when trying to connect: {e}"
                )
                return

        if self.connectivity_service.is_connected():

            for reference in self.device.actuator_references:
                self.publish_actuator_status(reference)
            if self.configuration_provider:
                self.publish_configuration()
            if self.file_management:
                file_list = self.file_management.get_file_list()
                message = self.message_factory.make_from_file_list_update(
                    file_list
                )
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)
            if self.firmware_update:
                version = self.firmware_update.get_current_version()
                message = self.message_factory.make_from_firmware_version(
                    version
                )
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)

                self.firmware_update.report_result()

    def disconnect(self) -> None:
        """Disconnect the device from WolkAbout IoT Platform."""
        if not self.connectivity_service.is_connected():
            return
        self.logger.debug("Disconnecting")
        self.connectivity_service.disconnect()

    def add_sensor_reading(
        self,
        reference: str,
        value: Union[bool, int, float, str],
        timestamp: Optional[int] = None,
    ) -> None:
        """
        Publish a sensor reading to WolkAbout IoT Platform.

        :param reference: The reference of the sensor
        :type reference: str
        :param value: The value of the sensor reading
        :type value: Union[bool, int, float, str]
        :param timestamp: Unix timestamp. If not provided, platform will assign
        :type timestamp: Optional[int]
        """
        self.logger.debug(
            f"Adding sensor reading: reference = '{reference}', "
            f"value = {value}, timestamp = {timestamp}"
        )
        reading = SensorReading(reference, value, timestamp)
        message = self.message_factory.make_from_sensor_reading(reading)
        self.message_queue.put(message)

    def add_alarm(
        self, reference: str, active: bool, timestamp: Optional[int] = None
    ) -> None:
        """
        Publish an alarm to WolkAbout IoT Platform.

        :param reference: Reference of the alarm
        :type reference: str
        :param active: Current state of the alarm
        :type active: bool
        :param timestamp: Unix timestamp. If not provided, platform will assign
        :type timestamp: Optional[int]
        """
        self.logger.debug(
            f"Add alarm event: reference = '{reference}', "
            f"active = {active}, timestamp = {timestamp}"
        )
        alarm = Alarm(reference, active, timestamp)
        message = self.message_factory.make_from_alarm(alarm)
        self.message_queue.put(message)

    def publish(self) -> None:
        """Publish all currently stored messages to WolkAbout IoT Platform."""
        self.logger.debug("Publishing")
        if not self.connectivity_service.is_connected():
            self.logger.warning("Not connected, unable to publish messages")
            return
        while True:
            message = self.message_queue.peek()
            if message is None:
                break

            if self.connectivity_service.publish(message):
                self.message_queue.get()
            else:
                self.logger.warning(f"Failed to publish message: {message}")
                break
        self.logger.debug("Publishing ended")

    def publish_actuator_status(self, reference: str) -> None:
        """
        Publish the current actuator status to WolkAbout IoT Platform.

        :param reference: reference of the actuator
        :type reference: str
        """
        if not self.connectivity_service.is_connected():
            self.logger.warning("Not connected, unable to publish message!")
            return
        self.logger.debug(
            f"Publishing actuator status for reference '{reference}'"
        )
        if not self.actuator_status_provider:
            self.logger.error("No actuator status provider is set!")
            return

        state, value = self.actuator_status_provider(reference)
        if state is None:
            self.logger.error(
                "Actuator status provider did not return "
                f"status for reference '{reference}'"
            )
            return

        message = self.message_factory.make_from_actuator_status(
            ActuatorStatus(reference, state, value)
        )

        if not self.connectivity_service.publish(message):
            self.logger.error(
                f"Failed to publish actuator status for reference {reference}!"
            )
            self.message_queue.put(message)

    def publish_configuration(self) -> None:
        """Publish current device configuration to WolkAbout IoT Platform."""
        if not self.connectivity_service.is_connected():
            self.logger.warning("Not connected, unable to publish message!")
            return
        self.logger.debug("Publishing configuration options")
        if not self.configuration_provider:
            self.logger.error("No configuration provider is set!")
            return

        message = self.message_factory.make_from_configuration(
            self.configuration_provider()  # type: ignore
        )

        if not self.connectivity_service.publish(message):
            self.logger.error("Failed to publish configuration options!")
            self.message_queue.put(message)

    def _on_inbound_message(self, message: Message) -> None:
        """
        Handle inbound messages.

        :param message: message received from the platform
        :type message: Message
        """
        if "binary" in message.topic:
            self.logger.debug(
                f"Received message: {message.topic} , "  # type: ignore
                f"{len(message.payload)}"
            )
        else:
            self.logger.debug(f"Received message: {message}")

        file_management_messages = [
            self.message_deserializer.is_file_purge_command,
            self.message_deserializer.is_file_delete_command,
            self.message_deserializer.is_file_binary_response,
            self.message_deserializer.is_file_upload_initiate,
            self.message_deserializer.is_file_upload_abort,
            self.message_deserializer.is_file_list_request,
            self.message_deserializer.is_file_list_confirm,
            self.message_deserializer.is_file_url_initiate,
            self.message_deserializer.is_file_url_abort,
        ]

        firmware_update_messages = [
            self.message_deserializer.is_firmware_install,
            self.message_deserializer.is_firmware_abort,
        ]

        if self.message_deserializer.is_actuation_command(message):
            if not self.actuation_handler or not self.actuator_status_provider:
                self.logger.warning(
                    f"Received unexpected actuation message: {message}"
                )
                return
            actuation = self.message_deserializer.parse_actuator_command(
                message
            )
            if actuation.command == ActuatorCommandType.SET:
                self.actuation_handler(
                    actuation.reference, actuation.value  # type: ignore
                )
                self.publish_actuator_status(actuation.reference)
            elif actuation.command == ActuatorCommandType.GET:
                self.publish_actuator_status(actuation.reference)
            return

        if self.message_deserializer.is_configuration_command(message):
            if (
                not self.configuration_provider
                or not self.configuration_handler
            ):
                self.logger.warning(
                    f"Received unexpected configuration message: {message}"
                )
                return
            configuration = self.message_deserializer.parse_configuration(
                message
            )
            if (
                configuration.command == ConfigurationCommandType.SET
                and configuration.value
            ):
                self.configuration_handler(configuration.value)  # type: ignore
                self.publish_configuration()
            elif configuration.command == ConfigurationCommandType.GET:
                self.publish_configuration()
            return

        if any(
            [is_message(message) for is_message in file_management_messages]
        ):
            self._on_file_management_message(message)
            return

        if any(
            [is_message(message) for is_message in firmware_update_messages]
        ):
            self._on_firmware_message(message)
            return

        self.logger.warning(f"Received unknown message: {message}")

    def _on_file_management_message(self, message: Message) -> None:

        if not self.file_management:
            self.logger.warning(
                f"Received unexpected file management message: {message}"
            )
            status = FileManagementStatus(
                FileManagementStatusType.ERROR,
                FileManagementErrorType.TRANSFER_PROTOCOL_DISABLED,
            )
            message = self.message_factory.make_from_file_management_status(
                status, ""
            )
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)
            return

        if self.message_deserializer.is_file_upload_initiate(message):
            name, size, fhash = self.message_deserializer.parse_file_initiate(
                message
            )
            if name != "":  # ignore invalid messages
                self.file_management.handle_upload_initiation(
                    name, size, fhash
                )
                return

        if self.message_deserializer.is_file_binary_response(message):
            package = self.message_deserializer.parse_file_binary(message)
            self.file_management.handle_file_binary_response(package)
            return

        if self.message_deserializer.is_file_upload_abort(message):
            self.file_management.handle_file_upload_abort()
            return

        if self.message_deserializer.is_file_url_abort(message):
            self.file_management.handle_file_upload_abort()
            return

        if self.message_deserializer.is_file_url_initiate(message):
            file_url = self.message_deserializer.parse_file_url(message)
            if file_url != "":  # ignore invalid messages
                self.file_management.handle_file_url_download_initiation(
                    file_url
                )
            return

        if self.message_deserializer.is_file_list_request(message):
            file_list = self.file_management.get_file_list()
            message = self.message_factory.make_from_file_list_request(
                file_list
            )
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)
            return

        if self.message_deserializer.is_file_delete_command(message):
            file_name = self.message_deserializer.parse_file_delete_command(
                message
            )
            if file_name != "":  # ignore invalid messages
                self.file_management.handle_file_delete(file_name)
                file_list = self.file_management.get_file_list()
                message = self.message_factory.make_from_file_list_update(
                    file_list
                )
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)
                return

        if self.message_deserializer.is_file_purge_command(message):
            self.file_management.handle_file_purge()
            file_list = self.file_management.get_file_list()
            message = self.message_factory.make_from_file_list_update(
                file_list
            )
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)
            return

        if self.message_deserializer.is_file_list_confirm(message):
            self.file_management.handle_file_list_confirm()
            return

    def _on_firmware_message(self, message: Message) -> None:
        if not self.firmware_update:
            self.logger.warning(
                f"Received unexpected firmware update message: {message}"
            )
            firmware_status = FirmwareUpdateStatus(
                FirmwareUpdateStatusType.ERROR,
                FirmwareUpdateErrorType.UNSPECIFIED_ERROR,
            )
            message = self.message_factory.make_from_firmware_update_status(
                firmware_status
            )
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)
            return

        if (
            self.message_deserializer.is_firmware_install(message)
            and self.file_management
        ):
            file_name = self.message_deserializer.parse_firmware_install(
                message
            )
            file_path = self.file_management.get_file_path(file_name)
            if not file_path:
                self.logger.error(
                    f"Specified file not found on device! Message: {message}"
                )
                firmware_status = FirmwareUpdateStatus(
                    FirmwareUpdateStatusType.ERROR,
                    FirmwareUpdateErrorType.FILE_NOT_PRESENT,
                )
                message = self.message_factory.make_from_firmware_update_status(
                    firmware_status
                )
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)
                return
            self.firmware_update.handle_install(file_path)
            return

        if self.message_deserializer.is_firmware_abort(message):
            self.firmware_update.handle_abort()
            return

    def _on_package_request(
        self, file_name: str, chunk_index: int, chunk_size: int
    ) -> None:
        """
        Handle file transfer package requests.

        :param file_name: The name of the file to which the chunk belongs
        :type file_name: str
        :param chunk_index: The index of the requested chunk
        :type chunk_index: int
        :param chunk_size: The size of the requested chunk
        :type chunk_size: int
        """
        message = self.message_factory.make_from_package_request(
            file_name, chunk_index, chunk_size
        )
        if not self.connectivity_service.publish(message):
            self.message_queue.put(message)

    def _on_firmware_update_status(self, status: FirmwareUpdateStatus) -> None:
        """
        Report firmware update status to WolkAbout IoT Platform.

        :param status: The status to be reported to the platform
        :type status: FirmwareUpdateStatus
        """
        message = self.message_factory.make_from_firmware_update_status(status)
        if not self.connectivity_service.publish(message):
            self.message_queue.put(message)
        if (
            status.status == FirmwareUpdateStatusType.COMPLETED
            and self.firmware_update
        ):
            version = self.firmware_update.get_current_version()
            message = self.message_factory.make_from_firmware_version(version)
            if self.connectivity_service.is_connected():
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)
            else:
                self.message_queue.put(message)

    def _on_file_upload_status(
        self, file_name: str, status: FileManagementStatus
    ) -> None:
        """
        Report file upload status to WolkAbout IoT Platform.

        :param file_name: File being transfered
        :type file_name: str
        :param status: Description of current status
        :type status: FileManagementStatus
        """
        message = self.message_factory.make_from_file_management_status(
            status, file_name
        )
        if not self.connectivity_service.publish(message):
            self.message_queue.put(message)
        if (
            status.status == FileManagementStatusType.FILE_READY
            and self.file_management
        ):
            file_list = self.file_management.get_file_list()
            message = self.message_factory.make_from_file_list_update(
                file_list
            )
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)

    def _on_file_url_status(
        self,
        file_url: str,
        status: FileManagementStatus,
        file_name: Optional[str] = None,
    ) -> None:
        """
        Report file URL transfer status to WolkAbout IoT Platform.

        :param file_url: URL from where to download file
        :type file_url: str
        :param status: Description of current status
        :type status: FileManagementStatus
        :param file_name: Name of downloaded file
        :type file_name: Optional[str]
        """
        message = self.message_factory.make_from_file_url_status(
            file_url, status, file_name
        )

        if not self.connectivity_service.publish(message):
            self.message_queue.put(message)

        if file_name and self.file_management:
            file_list = self.file_management.get_file_list()
            message = self.message_factory.make_from_file_list_update(
                file_list
            )
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)
