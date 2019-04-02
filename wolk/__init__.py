# coding=utf-8
"""
.. module:: wolk

This module provides connection to WolkAbout IoT Platform.

To start publishing data to the platform
create an instance of Device class with credentials obtained from the platform
and pass it to an instance of WolkConnect class.

For more information about module features visit:
https://github.com/Wolkabout/WolkConnect-Python/tree/master/examples/full_feature_set


Throughout this package usage of enumerations and ABCs are omitted
due to a constraint caused by the necessity to have
a single base (wolkcore) for two versions of Python: CPython and Zerynth.
"""
from .ActuationHandler import ActuationHandler
from .ActuatorStatusProvider import ActuatorStatusProvider
from .ConfigurationHandler import ConfigurationHandler
from .ConfigurationProvider import ConfigurationProvider
from .Device import Device
from .FileSystemFirmwareHandler import FileSystemFirmwareHandler
from .FirmwareInstaller import FirmwareInstaller
from .FirmwareURLDownloadHandler import FirmwareURLDownloadHandler
from .LoggerFactory import logging_config
from .wolkcore.OutboundMessageQueue import OutboundMessageQueue
from .WolkConnect import WolkConnect


__all__ = [
    "ActuationHandler",
    "ActuatorStatusProvider",
    "ConfigurationHandler",
    "ConfigurationProvider",
    "Device",
    "FileSystemFirmwareHandler",
    "FirmwareInstaller",
    "FirmwareURLDownloadHandler",
    "LoggerFactory",
    "logging_config",
    "OutboundMessageQueue",
    "WolkConnect",
]

# "Enum" of actuator states
ACTUATOR_STATE_READY = 0
ACTUATOR_STATE_BUSY = 1
ACTUATOR_STATE_ERROR = 2


# "Enum" of connector version
VERSION_MAJOR = 3
VERSION_MINOR = 1
VERSION_PATCH = 3
