# coding=utf-8
"""
This module provides connection to WolkAbout IoT Platform.

To start publishing data to the platform
create an instance of Device class with credentials obtained from the platform
and pass it to an instance of WolkConnect class.

For more information about module features visit:
https://github.com/Wolkabout/WolkConnect-Python/tree/master/examples/full_feature_set


Throughout this package usage of enumerations and ABCs are omitted
due to a constraint caused by the necessity to have
a single base (wolkcore) for two versions of python: CPython and Zerynth.

:ivar ACTUATOR_STATE_BUSY: Actuator state busy
:vartype ACTUATOR_STATE_BUSY: int
:ivar ACTUATOR_STATE_ERROR: Actuator state error
:vartype ACTUATOR_STATE_ERROR: int
:ivar ACTUATOR_STATE_READY: Actuator state ready
:vartype ACTUATOR_STATE_READY: int
:ivar VERSION_MAJOR: Major version
:vartype VERSION_MAJOR: int
:ivar VERSION_MINOR: Minor version
:vartype VERSION_MINOR: int
:ivar VERSION_PATCH: Patch version
:vartype VERSION_PATCH: int
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
VERSION_MINOR = 0
VERSION_PATCH = 6
