"""
Module that provides connection to WolkAbout IoT Platform.

To start publishing data to the platform
create an instance of Device class with credentials obtained from the platform
and pass it to an instance of WolkConnect class.

For more information about module features visit:
https://github.com/Wolkabout/WolkConnect-Python/tree/master/examples/full_feature_set
"""
__version__ = "4.1.3"
from .interface.connectivity_service import ConnectivityService
from .interface.firmware_handler import FirmwareHandler
from .interface.message_deserializer import MessageDeserializer
from .interface.message_factory import MessageFactory
from .interface.message_queue import MessageQueue
from .logger_factory import logging_config
from .model.device import Device
from .model.file_management_error_type import FileManagementErrorType
from .model.file_management_status import FileManagementStatus
from .model.file_management_status_type import FileManagementStatusType
from .model.file_transfer_package import FileTransferPackage
from .model.firmware_update_error_type import FirmwareUpdateErrorType
from .model.firmware_update_status import FirmwareUpdateStatus
from .model.firmware_update_status_type import FirmwareUpdateStatusType
from .model.message import Message
from .repeating_timer import RepeatingTimer
from .os_file_management import OSFileManagement
from .os_firmware_update import OSFirmwareUpdate
from .wolk_connect import WolkConnect
from .wolkabout_protocol_message_factory import WolkAboutProtocolMessageFactory
from .wolkabout_protocol_message_deserializer import (
    WolkAboutProtocolMessageDeserializer,
)
from .mqtt_connectivity_service import MQTTConnectivityService
from .message_deque import MessageDeque


__all__ = [
    "ActuatorCommand",
    "State",
    "ActuatorStatus",
    "Alarm",
    "ConfigurationCommand",
    "Device",
    "FileTransferPackage",
    "FirmwareUpdateStatus",
    "FirmwareUpdateStatusType",
    "FirmwareUpdateErrorType",
    "FileManagementStatus",
    "FileManagementStatusType",
    "FileManagementErrorType",
    "Message",
    "SensorReading",
    "handle_actuation",
    "get_actuator_status",
    "handle_configuration",
    "get_configuration",
    "ConnectivityService",
    "FirmwareHandler",
    "MessageDeserializer",
    "MessageFactory",
    "MessageQueue",
    "OSFileManagement",
    "OSFirmwareUpdate",
    "logging_config",
    "RepeatingTimer",
    "WolkConnect",
    "WolkAboutProtocolMessageFactory",
    "WolkAboutProtocolMessageDeserializer",
    "MQTTConnectivityService",
    "MessageDeque",
    "__version__",
]
