# coding=utf-8
"""
.. module:: wolk

This module provides connection to WolkAbout IoT Platform.

To start publishing data to the platform
create an instance of Device class with credentials obtained from the platform
and pass it to an instance of WolkConnect class.

For more information about module features visit:
https://github.com/Wolkabout/WolkConnect-Python/tree/master/examples/full_feature_set
"""
from .interfaces.ActuationHandler import ActuationHandler
from .interfaces.ActuatorStatusProvider import ActuatorStatusProvider
from .models.ActuatorState import ActuatorState
from .interfaces.ConfigurationHandler import ConfigurationHandler
from .interfaces.ConfigurationProvider import ConfigurationProvider
from .models.Device import Device
from .FileSystemFirmwareHandler import FileSystemFirmwareHandler
from .interfaces.FirmwareInstaller import FirmwareInstaller
from .interfaces.FirmwareURLDownloadHandler import FirmwareURLDownloadHandler
from .LoggerFactory import logging_config
from .interfaces.OutboundMessageQueue import OutboundMessageQueue
from .interfaces.OutboundMessageFactory import OutboundMessageFactory
from .interfaces.InboundMessageDeserializer import InboundMessageDeserializer
from .WolkConnect import WolkConnect


__all__ = [
    "ActuationHandler",
    "ActuatorStatusProvider",
    "ActuatorState",
    "ConfigurationHandler",
    "ConfigurationProvider",
    "Device",
    "FileSystemFirmwareHandler",
    "FirmwareInstaller",
    "FirmwareURLDownloadHandler",
    "LoggerFactory",
    "logging_config",
    "OutboundMessageQueue",
    "OutboundMessageFactory",
    "InboundMessageDeserializer",
    "WolkConnect",
]

# "Enum" of connector version
VERSION_MAJOR = 3
VERSION_MINOR = 2
VERSION_PATCH = 0
