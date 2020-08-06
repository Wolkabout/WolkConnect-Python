"""Enables firmware update for device."""
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
from abc import ABC
from abc import abstractmethod
from typing import Callable

from wolk.interface.firmware_handler import FirmwareHandler
from wolk.model.firmware_update_status import FirmwareUpdateStatus


class FirmwareUpdate(ABC):
    """
    Firmware Update enabler.

    Responsible for supervising firmware installation and reporting current
    firmware installation status and version.
    """

    @abstractmethod
    def __init__(
        self,
        firmware_handler: FirmwareHandler,
        status_callback: Callable[[FirmwareUpdateStatus], None],
    ) -> None:
        """
        Enable firmware update for device.

        :param firmware_handler: Install firmware and provide current version
        :type firmware_handler: FirmwareHandler
        :param status_callback: Reporting firmware update status
        :type status_callback: Callable[[FirmwareUpdateStatus], None]
        """
        raise NotImplementedError()

    @abstractmethod
    def handle_install(self, file_path: str) -> None:
        """
        Handle received firmware installation command.

        :param file_path: Firmware file to install
        :type file_path: str
        """
        raise NotImplementedError()

    @abstractmethod
    def handle_abort(self) -> None:
        """Handle received firmware installation abort command."""
        raise NotImplementedError()

    @abstractmethod
    def report_result(self) -> None:
        """Report the results of the firmware update process."""
        raise NotImplementedError()

    @abstractmethod
    def get_current_version(self) -> str:
        """
        Return device's current firmware version.

        :returns: Firmware version
        :rtype: str
        """
        raise NotImplementedError()
