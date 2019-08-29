"""Enables firmware update for device."""
#   Copyright 2019 WolkAbout Technology s.r.o.
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

from abc import ABC, abstractmethod
from typing import Callable

from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.interface.firmware_handler import FirmwareHandler


class FirmwareUpdate(ABC):
    """
    Firmware Update enabler.

    Responsible for supervising firmware installation and reporting current
    firmware installation status and version.
    """

    @abstractmethod
    def handle_install(self, file_path: str) -> None:
        """Handle received firmware installation command.

        :param file_path: Firmware file to install
        :type file_path: str
        """
        pass

    @abstractmethod
    def handle_abort(self) -> None:
        """Handle received firmware installation abort command."""
        pass

    @abstractmethod
    def report_result(self) -> None:
        """Report the results of the firmware update process."""
        pass

    @abstractmethod
    def _set_on_status_callback(
        self, on_status_callback: Callable[[FirmwareUpdateStatus], None]
    ) -> None:
        """Set a callback function to handle firmware status reporting.

        :param on_status_callback: Method for reporting firmware status
        :type on_status_callback: Callable[[FirmwareUpdateStatus], None]
        """
        pass

    @abstractmethod
    def _set_firmware_handler(self, handler: FirmwareHandler) -> None:
        """Set firmware handler.

        Must set as self.handler.

        :param handler: Installs firmware and reports current version
        :type handler: FirmwareHandler
        """
        pass
