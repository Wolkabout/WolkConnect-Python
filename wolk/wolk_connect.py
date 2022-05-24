"""Core of this package. Wraps in all functionality."""
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
from wolk.model.data_delivery import DataDelivery
from wolk.model.data_type import DataType
from wolk.model.device import Device
from wolk.model.feed_type import FeedType
from wolk.model.file_management_error_type import FileManagementErrorType
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.firmware_update_error_type import FirmwareUpdateErrorType
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.firmware_update_status_type import FirmwareUpdateStatusType
from wolk.model.message import Message
from wolk.model.unit import Unit
from wolk.mqtt_connectivity_service import MQTTConnectivityService as MQTTCS
from wolk.os_file_management import OSFileManagement
from wolk.os_firmware_update import OSFirmwareUpdate
from wolk.wolkabout_protocol_message_deserializer import (
    WolkAboutProtocolMessageDeserializer as WAPMDeserializer,
)
from wolk.wolkabout_protocol_message_factory import (
    WolkAboutProtocolMessageFactory as WAPMFactory,
)

IncomingData = List[Dict[str, Union[bool, int, float, str]]]
OutgoingDataTypes = Union[bool, int, float, str]
Reading = Tuple[str, OutgoingDataTypes]


class WolkConnect:
    """
    Exchange data with WolkAbout IoT Platform.

    :ivar connectivity_service: Means of sending/receiving data
    :vartype connectivity_service: ConnectivityService
    :ivar device: Contains device key and password
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

        :param device: Contains key and password
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

        self.file_management: Optional[FileManagement] = None
        self.firmware_update: Optional[FirmwareUpdate] = None
        self.message_queue: MessageQueue = MessageDeque()
        self.message_factory: MessageFactory = WAPMFactory(device.key)
        self.message_deserializer: MessageDeserializer = WAPMDeserializer(
            self.device
        )
        self.parameters: Dict[str, Union[int, bool, float, str]] = {}

        wolk_ca_cert = os.path.join(os.path.dirname(__file__), "ca.crt")

        if host and port and ca_cert:
            self.connectivity_service: ConnectivityService = MQTTCS(
                device,
                self.message_deserializer.get_inbound_topics(),
                host=host,
                port=int(port),
                ca_cert=ca_cert,
            )
        elif host and port:
            self.connectivity_service = MQTTCS(
                device,
                self.message_deserializer.get_inbound_topics(),
                host=host,
                port=int(port),
            )
        else:
            # NOTE: Default to secure connection to 'demo.wolkabout.com'
            self.connectivity_service = MQTTCS(
                device,
                self.message_deserializer.get_inbound_topics(),
                port=8883,
                ca_cert=wolk_ca_cert,
            )

        self.connectivity_service.set_inbound_message_listener(
            self._on_inbound_message
        )

        self.last_platform_timestamp: Optional[int] = None

    def with_file_management(  # type: ignore
        self,
        file_directory: str,
        preferred_package_size: int = 0,
        url_downloader: Optional[Callable[[str, str], bool]] = None,
    ):
        """
        Enable file management on the device.

        :param file_directory: Directory where files are stored
        :type file_directory: str
        :param preferred_package_size: Size in kilobytes, 0 means no limit
        :type preferred_package_size: int
        :param url_downloader: Function for downloading file from URL
        :type url_downloader: Optional[Callable[[str, str], bool]]
        """
        self.logger.debug(
            f"File directory: '{file_directory}',"
            f"preferred package size: {preferred_package_size}, "
        )

        self.file_management = OSFileManagement(
            self._on_file_upload_status,
            self._on_package_request,
            self._on_file_url_status,
        )
        self.file_management.configure(
            file_directory,
            preferred_package_size,
        )

        if url_downloader is not None:
            self.file_management.set_custom_url_downloader(url_downloader)

        return self

    def with_incoming_feed_value_handler(  # type: ignore
        self, incoming_feed_value_handler: Callable[[IncomingData], None]
    ):
        """
        Enable device to respond to incoming feed value change commands.

        Commands will be delivered as a list of dictionaries that contain
        a feed_reference:value pair, and a "timestamp" field that specifies
        when this command was issued from the platform.
        The timestamp is an int representing Unix milliseconds.

        :param incoming_feed_value_handler: Handler of feed value commands
        :type incoming_feed_value_handler: Callable[[IncomingData], None]
        """
        self.logger.debug(
            f"Incoming feed value handler: {incoming_feed_value_handler}"
        )

        if not callable(incoming_feed_value_handler):
            raise ValueError(
                f"{incoming_feed_value_handler} is not a callable!"
            )
        if len(signature(incoming_feed_value_handler).parameters) != 1:
            raise ValueError(
                f"{incoming_feed_value_handler} invalid signature!"
            )
        self.incoming_feed_value_handler = incoming_feed_value_handler

        return self

    def with_firmware_update(self, firmware_handler: FirmwareHandler):  # type: ignore
        """
        Enable firmware update for device.

        Requires that file management is previously enabled on device.

        :param firmware_handler: Provide firmware version & handle installation
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

        return self

    def with_custom_message_queue(self, message_queue: MessageQueue):  # type: ignore
        """
        Use custom means of storing serialized messages.

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

    def connect(self) -> None:
        """
        Connect the device to the WolkAbout IoT Platform.

        If the connection is made, then it also sends information
        about list of files present on device, current firmware version
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
            parameters: dict = {}
            parameters["FILE_TRANSFER_PLATFORM_ENABLED"] = False
            parameters["FIRMWARE_UPDATE_ENABLED"] = False
            parameters["FILE_TRANSFER_URL_ENABLED"] = False
            if self.file_management:
                parameters["FILE_TRANSFER_PLATFORM_ENABLED"] = True
                parameters[
                    "FILE_TRANSFER_URL_ENABLED"
                ] = self.file_management.supports_url_download()
                parameters[
                    "MAXIMUM_MESSAGE_SIZE"
                ] = self.file_management.get_preffered_package_size()

                file_list = self.file_management.get_file_list()
                message = self.message_factory.make_from_file_list(file_list)
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)
            if self.firmware_update:
                parameters["FIRMWARE_UPDATE_ENABLED"] = True
                current_version = self.firmware_update.get_current_version()
                parameters["FIRMWARE_VERSION"] = current_version
                # TODO: "FIRMWARE_UPDATE_CHECK_TIME"
                # TODO: "FIRMWARE_UPDATE_REPOSITORY"

                self.firmware_update.report_result()

            self.logger.debug(f"Updating device parameters with: {parameters}")
            self.parameters.update(parameters)
            self.logger.info(
                f"Publishing device parameters: {self.parameters}"
            )
            message = self.message_factory.make_from_parameters(
                self.parameters
            )
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)

            if self.device.data_delivery == DataDelivery.PULL:
                self.pull_parameters()
                self.pull_feed_values()

    def disconnect(self) -> None:
        """Disconnect the device from WolkAbout IoT Platform."""
        if not self.connectivity_service.is_connected():
            return
        self.logger.debug("Disconnecting")
        self.connectivity_service.disconnect()

    def add_feed_value(
        self,
        reading: Union[Reading, List[Reading]],
        timestamp: Optional[int] = None,
    ) -> None:
        """
        Place a feed value reading into storage.

        A reading is identified by a unique feed reference string and
        the current value of the feed.

        This reading can either be passed as a tuple of (reference, value)
        for a single feed or as a list of previously mentioned tuples
        to pass multiple feed readings at once.

        A Unix epoch timestamp in milliseconds as int can be provided to
        denote when the reading occurred. By default, the current system
        provided time will be assigned to a reading.

        :param reading: Feed value reading
        :type reading: Union[Reading, List[Reading]]
        :param timestamp: Unix timestamp. Defaults to system time.
        :type timestamp: Optional[int]
        """
        self.logger.debug(
            f"Adding feed value: reading: {reading}, timestamp = {timestamp}"
        )

        message = self.message_factory.make_from_feed_value(reading, timestamp)
        # NOTE: if device is PUSH, do we try to publish instantly?
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

    def pull_parameters(self) -> None:
        """Issue a message to pull commanded feed values."""
        self.logger.info("Sending pull parameters request")
        if self.device.data_delivery == DataDelivery.PUSH:
            self.logger.warning(
                "Always connected devices (PUSH) do not"
                " need to issue pull commands."
            )
            return
        if not self.connectivity_service.is_connected():
            self.logger.warning(
                "Not connected - not sending pull parameters message"
            )
            return

        message = self.message_factory.make_pull_parameters()

        if not self.connectivity_service.publish(message):
            self.logger.warning(f"Failed to publish message: {message}")

    def pull_feed_values(self) -> None:
        """Issue a message to pull commanded feed values."""
        self.logger.info("Sending pull feed values request")
        if self.device.data_delivery == DataDelivery.PUSH:
            self.logger.warning(
                "Always connected devices (PUSH) do not"
                " need to issue pull commands."
            )
            return
        if not self.connectivity_service.is_connected():
            self.logger.warning(
                "Not connected - not sending pull feed values message"
            )
            return

        message = self.message_factory.make_pull_feed_values()

        if not self.connectivity_service.publish(message):
            self.logger.warning(f"Failed to publish message: {message}")

    def request_timestamp(self) -> Optional[int]:
        """
        Return last received timestamp from Platform.

        If the device didn't connect at least once,
        then this will return None.

        :returns: UTC timestamp in milliseconds
        :rtype: int or None
        """
        if self.last_platform_timestamp is None:
            self.logger.warning("No timestamp available yet, will return None")
        if not self.connectivity_service.is_connected():
            self.logger.warning("Not connected, not requesting new time")
            return self.last_platform_timestamp

        message = self.message_factory.make_time_request()

        if not self.connectivity_service.publish(message):
            self.logger.warning(f"Failed to publish message: {message}")

        return self.last_platform_timestamp

    def register_feed(
        self,
        name: str,
        reference: str,
        feed_type: FeedType,
        unit: Union[Unit, str],
    ) -> None:
        """
        Register a new feed for the device.

        Feed is identified by name, unique reference, type (in or in/out)
        and unit; Where unit is either a default available unit listed in
        Unit enumeration, or a custom user defined unit that should be passed
        as a string value.

        :param name: Feed name
        :type name: str
        :param reference: Unique identifier
        :type reference: str
        :param feed_type: Is the feed one or two-way communication
        :type feed_type: FeedType
        :param unit: Unit used to measure this feed
        :type unit: Union[Unit, str]
        """
        self.logger.debug(
            "Register feed called with: "
            f"name='{name}', "
            f"reference='{reference}', "
            f"feed_type={feed_type}, "
            f"unit='{unit}'"
        )

        if not isinstance(unit, Unit):
            self.logger.warning(
                "Registering feed with user defined unit "
                f"'{unit}'. "
                "If this unit is not present on the platform, "
                "this request will fail."
            )

        message = self.message_factory.make_feed_registration(
            name, reference, feed_type, unit
        )

        if not self.connectivity_service.is_connected():
            self.logger.warning(
                "Not connected - not sending register feed request"
            )
            self.message_queue.put(message)
            return

        if not self.connectivity_service.publish(message):
            self.logger.warning(f"Failed to publish message: {message}")
            self.message_queue.put(message)

    def remove_feed(self, reference: str) -> None:
        """
        Remove a feed from the device.

        :param reference: Unique identifier
        :type reference: str
        """
        self.logger.debug(f"Remove feed called with: reference='{reference}'")
        message = self.message_factory.make_feed_removal(reference)

        if not self.connectivity_service.is_connected():
            self.logger.warning(
                "Not connected - not sending remove feed request"
            )
            self.message_queue.put(message)
            return

        if not self.connectivity_service.publish(message):
            self.logger.warning(f"Failed to publish message: {message}")
            self.message_queue.put(message)

    def register_attribute(
        self, name: str, data_type: DataType, value: str
    ) -> None:
        """
        Register an attribute for the device.

        The attribute name must be unique per device.
        All attributes created by a device are always required and read-only.
        If an attribute with the given name already exists,
        the value will be updated.

        :param name: Unique attribute name
        :type name: str
        :param data_type: Data type this attribute will hold
        :type data_type: DataType
        :param value: Value of the attribute
        :type value: str
        """
        self.logger.debug(
            "Register attribute called with: "
            f"name='{name}', "
            f"data_type={data_type}, "
            f"value='{value}'"
        )

        message = self.message_factory.make_attribute_registration(
            name, data_type, value
        )

        if not self.connectivity_service.is_connected():
            self.logger.warning(
                "Not connected - not sending register attribute request"
            )
            self.message_queue.put(message)
            return

        if not self.connectivity_service.publish(message):
            self.logger.warning(f"Failed to publish message: {message}")
            self.message_queue.put(message)

    def _on_inbound_message(self, message: Message) -> None:
        """
        Handle inbound messages.

        :param message: message received from the Platform
        :type message: Message
        """
        if "binary" in message.topic:
            self.logger.debug(
                f"Received message: {message.topic} , "
                f"{len(message.payload)}"
            )
        else:
            self.logger.debug(f"Received message: {message}")

        if self.message_deserializer.is_parameters(message):
            # TODO: parameters handle
            # NOTE: "FIRMWARE_UPDATE_CHECK_TIME"
            # NOTE: Other optional parameters?
            parameters = self.message_deserializer.parse_parameters(message)
            self.logger.info(f"TODO: parameters update: {parameters}")
            self.parameters.update(parameters)
            return

        if self.message_deserializer.is_feed_values(message):
            if not self.incoming_feed_value_handler:
                self.logger.warning(
                    "Received incoming feed values,"
                    " but no handler has been set!"
                )
                return

            feed_values = self.message_deserializer.parse_feed_values(message)
            if not feed_values:
                self.logger.warning(
                    "Failed to parse incoming feed values, ignoring"
                )
                return

            self.logger.info(
                f"Calling incoming feed value handler with: {feed_values}"
            )
            self.incoming_feed_value_handler(feed_values)
            return

        if self.message_deserializer.is_time_response(message):
            timestamp = self.message_deserializer.parse_time_response(message)
            self.logger.info(
                "Updating last platform timestamp "
                f"from {self.last_platform_timestamp}"
                f" to {timestamp}"
            )
            self.last_platform_timestamp = timestamp
            return

        if self.message_deserializer.is_file_management_message(message):
            self._on_file_management_message(message)
            return

        if self.message_deserializer.is_firmware_message(message):
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

        if self.message_deserializer.is_file_list(message):
            file_list = self.file_management.get_file_list()
            message = self.message_factory.make_from_file_list(file_list)
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)
            return

        if self.message_deserializer.is_file_delete_command(message):
            file_names = self.message_deserializer.parse_file_delete_command(
                message
            )
            if file_names:  # ignore invalid messages
                self.file_management.handle_file_delete(file_names)
                file_list = self.file_management.get_file_list()
                message = self.message_factory.make_from_file_list(file_list)
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)
            return

        if self.message_deserializer.is_file_purge_command(message):
            self.file_management.handle_file_purge()
            file_list = self.file_management.get_file_list()
            message = self.message_factory.make_from_file_list(file_list)
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)
            return

        self.logger.warning(f"Received unknown message: {message}")

    def _on_firmware_message(self, message: Message) -> None:
        if not self.firmware_update:
            self.logger.warning(
                f"Received unexpected firmware update message: {message}"
            )
            firmware_status = FirmwareUpdateStatus(
                FirmwareUpdateStatusType.ERROR,
                FirmwareUpdateErrorType.UNKNOWN,
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
            file_path = self.file_management.get_file_path(file_name)
            if not file_path:
                self.logger.error(
                    f"Specified file not found on device! Message: {message}"
                )
                firmware_status = FirmwareUpdateStatus(
                    FirmwareUpdateStatusType.ERROR,
                    FirmwareUpdateErrorType.UNKNOWN_FILE,
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

    def _on_package_request(self, file_name: str, chunk_index: int) -> None:
        """
        Handle file transfer package requests.

        :param file_name: The name of the file to which the chunk belongs
        :type file_name: str
        :param chunk_index: The index of the requested chunk
        :type chunk_index: int
        """
        message = self.message_factory.make_from_package_request(
            file_name, chunk_index
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
            status.status == FirmwareUpdateStatusType.SUCCESS
            and self.firmware_update
        ):
            version = self.firmware_update.get_current_version()
            self.parameters.update({"FIRMWARE_VERSION": version})
            if self.connectivity_service.is_connected():
                message = self.message_factory.make_from_parameters(
                    self.parameters
                )
                if not self.connectivity_service.publish(message):
                    self.message_queue.put(message)

    def _on_file_upload_status(
        self, file_name: str, status: FileManagementStatus
    ) -> None:
        """
        Report file upload status to WolkAbout IoT Platform.

        :param file_name: File being transferred
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
            message = self.message_factory.make_from_file_list(file_list)
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
            message = self.message_factory.make_from_file_list(file_list)
            if not self.connectivity_service.publish(message):
                self.message_queue.put(message)
