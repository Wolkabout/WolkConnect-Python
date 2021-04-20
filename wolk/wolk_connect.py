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
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from wolk import logger_factory
from wolk.interface.connectivity_service import ConnectivityService
from wolk.interface.file_management import FileManagement
from wolk.interface.firmware_handler import FirmwareHandler
from wolk.interface.firmware_update import FirmwareUpdate
from wolk.interface.message_deserializer import MessageDeserializer
from wolk.interface.message_factory import MessageFactory
from wolk.interface.message_queue import MessageQueue
from wolk.message_deque import MessageDeque
from wolk.model.actuator_status import ActuatorStatus
from wolk.model.alarm import Alarm
from wolk.model.device import Device
from wolk.model.file_management_error_type import FileManagementErrorType
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.firmware_update_error_type import FirmwareUpdateErrorType
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.firmware_update_status_type import FirmwareUpdateStatusType
from wolk.model.message import Message
from wolk.model.sensor_reading import SensorReading
from wolk.model.state import State
from wolk.mqtt_connectivity_service import MQTTConnectivityService as MQTTCS
from wolk.os_file_management import OSFileManagement
from wolk.os_firmware_update import OSFirmwareUpdate
from wolk.repeating_timer import RepeatingTimer
from wolk.wolkabout_protocol_message_deserializer import (
    WolkAboutProtocolMessageDeserializer as WAPMDeserializer,
)
from wolk.wolkabout_protocol_message_factory import (
    WolkAboutProtocolMessageFactory as WAPMFactory,
)

ConfigurationValue = Union[
    bool,
    int,
    float,
    str,
]

ActuatorValue = Tuple[State, Optional[Union[bool, int, float, str]]]

ReadingValue = Union[
    bool,
    int,
    Tuple[int, ...],
    float,
    Tuple[float, ...],
    str,
]


class WolkConnect:
    """
    Exchange data with WolkAbout IoT Platform.

    :ivar actuation_handler: Function for handling actuation commands
    :vartype actuation_handler: Callable[[str, Union[bool, int, float, str]], None] or None
    :ivar actuator_status_provider: Function for getting current actuator status
    :vartype actuator_status_provider: Callable[[str], ActuatorValue] or None
    :ivar configuration_handler: Function for handling configuration commands
    :vartype configuration_handler: Callable[[dict], None] or None
    :ivar configuration_provider: Function for getting current configuration options
    :vartype configuration_provider: Callable[[None], dict] or None
    :ivar connectivity_service: Means of sending/receiving data
    :vartype connectivity_service: ConnectivityService
    :ivar device: Contains device key and password, and actuator references
    :vartype device: Device
    :ivar file_management: File management module
    :vartype file_management: FileManagement or None
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
    :ivar keep_alive_service_enabled: Enable keep alive service
    :vartype keep_alive_service_enabled: bool
    :ivar keep_alive_interval: Interval in seconds when to publish message
    :vartype keep_alive_interval: int
    :ivar keep_alive_service: Keep alive service
    :vartype keep_alive_service: RepeatingTimer or None
    """

    def __init__(
        self,
        device: Device,
        host: Optional[str] = None,
        port: Optional[int] = None,
        ca_cert: Optional[str] = None,
    ):
        """
        Provide communication with WolkAbout IoT Platform.

        :param device: Contains key and password, and actuator references
        :type device: Device
        :param host: Host name or IP address of the remote broker
        :type host: str, optional
        :param port: Network port of the server host to connect to
        :type port: int, optional
        :param ca_cert: String path to Certificate Authority certificate file
        :type ca_cert: str, optional
        """
        logger_factory.logger_factory.set_device_key(device.key)
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(
            f"Device: {device} ; "
            f"Host: {host} ; Port: {port} ; ca_cert: {ca_cert}"
        )

        self.device = device
        self.actuation_handler: Optional[
            Callable[[str, Union[bool, int, float, str]], None]
        ] = None
        self.actuator_status_provider: Optional[
            Callable[[str], ActuatorValue]
        ] = None

        self.configuration_handler: Optional[
            Callable[[Dict[str, ConfigurationValue]], None]
        ] = None
        self.configuration_provider: Optional[
            Callable[[None], Dict[str, ConfigurationValue]]
        ] = None
        self.file_management: Optional[FileManagement] = None
        self.firmware_update: Optional[FirmwareUpdate] = None
        self.message_queue: MessageQueue = MessageDeque()
        self.message_factory: MessageFactory = WAPMFactory(device.key)
        self.message_deserializer: MessageDeserializer = WAPMDeserializer(
            self.device
        )

        wolk_ca_cert = os.path.join(os.path.dirname(__file__), "ca.crt")
        last_will_message = self.message_factory.make_last_will_message()

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
            self.connectivity_service = MQTTCS(
                device,
                self.message_deserializer.get_inbound_topics(),
                last_will_message,
                ca_cert=wolk_ca_cert,
            )

        self.connectivity_service.set_inbound_message_listener(
            self._on_inbound_message
        )

        self.keep_alive_service_enabled = True
        self.keep_alive_interval = 60
        self.keep_alive_service: Optional[RepeatingTimer] = None

        self.last_platform_timestamp: Optional[int] = None

    def with_actuators(  # type: ignore
        self,
        actuation_handler: Callable[[str, Union[bool, int, float, str]], None],
        actuator_status_provider: Callable[[str], ActuatorValue],
    ):
        """
        Enable controlling actuators on the device from the Platform.

        :param actuation_handler: Handle actuation commands
        :type actuation_handler: Callable[[str, Union[bool, int, float, str]], None]
        :param actuator_status_provider: Read actuator status
        :type actuator_status_provider: Callable[[str], ActuatorValue]
        """
        self.logger.debug(
            f"Actuation handler: {actuation_handler} ; "
            f"Actuator status provider: {actuator_status_provider}"
        )

        if not callable(actuation_handler):
            raise ValueError(f"{actuation_handler} is not a callable!")
        if len(signature(actuation_handler).parameters) != 2:
            raise ValueError(f"{actuation_handler} invalid signature!")
        self.actuation_handler = actuation_handler

        if not callable(actuator_status_provider):
            raise ValueError(f"{actuator_status_provider} is not a callable!")
        if len(signature(actuator_status_provider).parameters) != 1:
            raise ValueError(f"{actuator_status_provider} invalid signature!")
        self.actuator_status_provider = actuator_status_provider

        return self

    def with_configuration(  # type: ignore
        self,
        configuration_handler: Callable[[Dict[str, ConfigurationValue]], None],
        configuration_provider: Callable[
            [None], Dict[str, ConfigurationValue]
        ],
    ):
        """
        Enable setting device's configuration options from the Platform.

        :param configuration_handler: Handle configuration commands
        :type configuration_handler: Callable[[Dict[str,ConfigurationValue]], None]
        :param configuration_provider: Read configuration options
        :type configuration_provider: Callable[[None], Dict[str, ConfigurationValue]]
        """
        self.logger.debug(
            f"Configuration handler: {configuration_handler} ; "
            f"Configuration provider: {configuration_provider}"
        )

        if not callable(configuration_handler):
            raise ValueError(f"{configuration_handler} is not a callable!")
        if len(signature(configuration_handler).parameters) != 1:
            raise ValueError(f"{configuration_handler} invalid signature!")
        self.configuration_handler = configuration_handler

        if not callable(configuration_provider):
            raise ValueError(f"{configuration_provider} is not a callable!")
        if len(signature(configuration_provider).parameters) != 0:
            raise ValueError(f"{configuration_provider} invalid signature!")
        self.configuration_provider = configuration_provider

        return self

    def with_file_management(  # type: ignore
        self,
        preferred_package_size: int,
        max_file_size: int,
        file_directory: str,
        custom_url_download: Optional[Callable[[str, str], bool]] = None,
    ):
        """
        Enable file management on the device.

        :param preferred_package_size: Size of file package chunk in bytes
        :type preferred_package_size: int
        :param max_file_size: Maximum supported file size in bytes
        :type max_file_size: int
        :param file_directory: Directory where files are stored
        :type file_directory: str
        :param custom_url_download: Optional custom function for downloading file from URL
        :type custom_url_download: Optional[Callable[[str, str], bool]]
        """
        self.logger.debug(
            f"Preferred package size: {preferred_package_size}, "
            f"maximum file size: {max_file_size}, "
            f"file directory: '{file_directory}'"
        )

        self.file_management = OSFileManagement(
            self._on_file_upload_status,
            self._on_package_request,
            self._on_file_url_status,
        )
        self.file_management.configure(
            preferred_package_size,
            max_file_size,
            file_directory,
        )

        if custom_url_download is not None:
            self.file_management.set_custom_url_downloader(custom_url_download)

        return self

    def with_firmware_update(self, firmware_handler: FirmwareHandler):  # type: ignore
        """
        Enable firmware update for device.

        Requires that file management is previously enabled on device.

        :param firmware_handler: Provide firmware version and handle installation
        :type firmware_handler: FirmwareHandler
        """
        self.logger.debug(f"Firmware handler: {firmware_handler}")
        if self.file_management is None:
            raise RuntimeError(
                "File management must be enabled before firmware update"
            )
        self.firmware_update = OSFirmwareUpdate(
            firmware_handler, self._on_firmware_update_status
        )

        message = self.message_factory.make_from_firmware_version_update(
            self.firmware_update.get_current_version()
        )
        self.message_queue.put(message)
        self.firmware_update.report_result()

        return self

    def with_custom_message_queue(self, message_queue: MessageQueue):  # type: ignore
        """
        Set custom means of storing serialized messages.

        :param message_queue: Custom message queue
        :type message_queue: MessageQueue
        """
        self.logger.debug(f"Message queue: {message_queue}")
        if not isinstance(message_queue, MessageQueue):
            raise ValueError(
                "Provided message queue does not implement MessageQueue"
            )

        self.message_queue = message_queue

        return self

    def with_custom_protocol(  # type: ignore
        self,
        message_factory: MessageFactory,
        message_deserializer: MessageDeserializer,
    ):
        """
        Provide a custom protocol to use for communication with the Platform.

        :param message_factory: Creator of messages to be sent to the Platform
        :type message_factory: MessageFactory
        :param message_deserializer: Deserializer of messages from the Platform
        :type message_deserializer: MessageDeserializer
        """
        self.logger.debug(
            f"Message factory: {message_factory} ; "
            f"message deserializer: {message_deserializer}"
        )
        if not isinstance(message_factory, MessageFactory):
            raise ValueError("Invalid message factory provided")
        self.message_factory = message_factory

        if not isinstance(message_deserializer, MessageDeserializer):
            raise ValueError("Invalid message deserializer provided")
        self.message_deserializer = message_deserializer

        return self

    def with_custom_connectivity(  # type: ignore
        self, connectivity_service: ConnectivityService
    ):
        """
        Provide a custom way to communicate with the Platform.

        :param connectivity_service: Custom connectivity service
        :type connectivity_service: ConnectivityService
        """
        self.logger.debug(f"Connectivity service: {connectivity_service}")
        if not isinstance(connectivity_service, ConnectivityService):
            raise ValueError("Invalid connectivity service provided")
        self.connectivity_service = connectivity_service
        self.connectivity_service.set_inbound_message_listener(
            self._on_inbound_message
        )

        return self

    def with_keep_alive_service(  # type: ignore
        self, enabled: bool, interval: Optional[int] = None
    ):
        """
        Enable or disable keep alive service.

        :param enabled: Enable or disable keep alive service
        :type enabled: bool
        :param interval: Interval in seconds, default is 60
        :type interval: int or None
        """
        if not enabled:
            self.keep_alive_service_enabled = False
            self.keep_alive_service = None

        if interval:
            self.keep_alive_interval = interval

        return self

    def _send_keep_alive(self) -> None:
        if not self.connectivity_service.is_connected():
            return
        message = self.message_factory.make_keep_alive_message()
        self.connectivity_service.publish(message)

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

        try:
            self.connectivity_service.connect()
        except Exception as exception:
            self.logger.exception(
                f"Something went wrong when trying to connect: {exception}"
            )
            return

        if self.connectivity_service.is_connected():

            if self.actuator_status_provider:
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
                message = (
                    self.message_factory.make_from_firmware_version_update(
                        self.firmware_update.get_current_version()
                    )
                )
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)

                self.firmware_update.report_result()

            if self.keep_alive_service_enabled:
                self._send_keep_alive()
                self.keep_alive_service = RepeatingTimer(
                    self.keep_alive_interval, self._send_keep_alive
                )
                self.keep_alive_service.start()

    def disconnect(self) -> None:
        """Disconnect the device from WolkAbout IoT Platform."""
        if not self.connectivity_service.is_connected():
            return
        self.logger.debug("Disconnecting")
        if self.keep_alive_service is not None:
            self.keep_alive_service.cancel()
        self.connectivity_service.disconnect()

    def add_sensor_reading(
        self,
        reference: str,
        value: Union[ReadingValue, List[Tuple[ReadingValue, int]]],
        timestamp: Optional[int] = None,
    ) -> None:
        """
        Place a sensor reading into storage.

        Pass a single reading or multiple readings as a list
        of tuples where the first element is the reading data
        and the second element is timestamp when the reading occurred.
        If passing a list of readings, omit the `timestamp` argument.

        :param reference: The reference of the sensor
        :type reference: str
        :param value: The value of the sensor reading
        :type value: Union[ReadingValue, List[Tuple[ReadingValue, int]]]
        :param timestamp: Unix timestamp. If not provided, library will assign
        :type timestamp: Optional[int]
        """
        self.logger.debug(
            f"Adding sensor reading: reference = '{reference}', "
            f"value = {value}, timestamp = {timestamp}"
        )
        if isinstance(value, list):
            reading: Union[SensorReading, List[SensorReading]] = [
                SensorReading(reference, data[0], data[1]) for data in value
            ]
        else:
            reading = SensorReading(reference, value, timestamp)
        message = self.message_factory.make_from_sensor_reading(reading)
        self.message_queue.put(message)

    def add_sensor_readings(
        self,
        readings: Dict[str, ReadingValue],
        timestamp: Optional[int] = None,
    ) -> None:
        """
        Place multiple sensor readings into storage.

        :param readings: Dictionary of reference: value pairs
        :type readings: Dict[str, Union[bool, int, Tuple[int, ...] float, Tuple[float, ...], str]]
        :param timestamp: Unix timestamp. If not provided, library will assign
        :type timestamp: Optional[int]
        """
        self.logger.debug(
            f"Adding sensor readings: readings:{readings}, "
            f"timestamp = {timestamp}"
        )
        message = self.message_factory.make_from_sensor_readings(
            readings, timestamp
        )
        self.message_queue.put(message)

    def add_alarm(
        self,
        reference: str,
        active: bool,
        timestamp: Optional[int] = None,
    ) -> None:
        """
        Publish an alarm to WolkAbout IoT Platform.

        :param reference: Reference of the alarm
        :type reference: str
        :param active: Current state of the alarm
        :type active: bool
        :param timestamp: Unix timestamp. If not provided, current time will be used
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

        actuator_status = self.actuator_status_provider(reference)
        if actuator_status is None:
            self.logger.error(  # type: ignore
                "Actuator status provider did not return "
                f"status for reference '{reference}'"
            )
            return
        message = self.message_factory.make_from_actuator_status(
            ActuatorStatus(reference, actuator_status[0], actuator_status[1])
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

    def request_timestamp(self) -> Optional[int]:
        """
        Return last received timestamp from Platform.

        If keep alive service is disabled or device didn't connect
        at least once, then this will return None.

        :returns: UTC timestamp in milliseconds
        :rtype: int or None
        """
        if self.last_platform_timestamp is None:
            self.logger.warning("No timestamp available, returning None")
            return None

        return self.last_platform_timestamp

    def _on_inbound_message(self, message: Message) -> None:
        """
        Handle inbound messages.

        :param message: message received from the Platform
        :type message: Message
        """
        if "binary" in message.topic:
            self.logger.debug(
                f"Received message: {message.topic} , "
                f"{len(message.payload)}"  # type: ignore
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
            self.actuation_handler(actuation.reference, actuation.value)
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
            self.configuration_handler(configuration.value)
            self.publish_configuration()
            return

        if self.message_deserializer.is_keep_alive_response(message):
            timestamp = self.message_deserializer.parse_keep_alive_response(
                message
            )
            self.logger.debug(
                "Updating last platform timestamp "
                f"from {self.last_platform_timestamp}"
                f" to {timestamp}"
            )
            self.last_platform_timestamp = timestamp
            return

        if any(is_message(message) for is_message in file_management_messages):
            self._on_file_management_message(message)
            return

        if any(is_message(message) for is_message in firmware_update_messages):
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

        self.logger.warning(f"Received unknown message: {message}")

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

        if self.message_deserializer.is_firmware_install(message):
            file_name = self.message_deserializer.parse_firmware_install(
                message
            )
            file_path = self.file_management.get_file_path(file_name)  # type: ignore
            if not file_path:
                self.logger.error(
                    f"Specified file not found on device! Message: {message}"
                )
                firmware_status = FirmwareUpdateStatus(
                    FirmwareUpdateStatusType.ERROR,
                    FirmwareUpdateErrorType.FILE_NOT_PRESENT,
                )
                message = (
                    self.message_factory.make_from_firmware_update_status(
                        firmware_status
                    )
                )
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)
                return
            self.firmware_update.handle_install(file_path)
            return

        if self.message_deserializer.is_firmware_abort(message):
            self.firmware_update.handle_abort()
            return

        self.logger.warning(f"Received unknown firmware message: {message}")

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

        :param status: The status to be reported to the Platform
        :type status: FirmwareUpdateStatus
        """
        message = self.message_factory.make_from_firmware_update_status(status)
        if self.connectivity_service.is_connected():
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)
        else:
            self.message_queue.put(message)
        if (
            status.status == FirmwareUpdateStatusType.COMPLETED
            and self.firmware_update
        ):
            version = self.firmware_update.get_current_version()
            message = self.message_factory.make_from_firmware_version_update(
                version
            )
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
