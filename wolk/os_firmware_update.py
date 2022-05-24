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
import os
from typing import Callable
from typing import Optional

from wolk import logger_factory
from wolk.interface.firmware_handler import FirmwareHandler
from wolk.interface.firmware_update import FirmwareUpdate
from wolk.model.firmware_update_error_type import FirmwareUpdateErrorType
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.firmware_update_status_type import FirmwareUpdateStatusType


class OSFirmwareUpdate(FirmwareUpdate):
    """Responsible for everything related to the firmware update process."""

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
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(f"firmware_handler: {firmware_handler}")
        self.status_callback = status_callback
        if not isinstance(firmware_handler, FirmwareHandler):
            raise ValueError(
                f"Given firmware handler {firmware_handler} is not "
                "an instance of FirmwareHandler"
            )
        self.firmware_handler = firmware_handler
        self.current_status: Optional[FirmwareUpdateStatus] = None

    def get_current_version(self) -> str:
        """
        Return device's current firmware version.

        :returns: Firmware version
        :rtype: str
        """
        return self.firmware_handler.get_current_version()

    def handle_install(self, file_path: str) -> None:
        """
        Handle received firmware installation command.

        :param file_path: Firmware file to install
        :type file_path: str
        """
        self.logger.debug(
            f"Handling install command with path path: {file_path}"
        )

        if self.current_status is not None:

            self.logger.warning(
                "Not in idle status, ignoring install command."
            )
            return

        if os.path.exists("last_firmware_version.txt"):
            self.current_status = FirmwareUpdateStatus(
                FirmwareUpdateStatusType.ERROR,
                FirmwareUpdateErrorType.UNKNOWN,
            )
            self.logger.error("Previous firmware update did not complete!")
            self.status_callback(self.current_status)
            self._reset_state()
            return

        if not os.path.exists(file_path):
            self.current_status = FirmwareUpdateStatus(
                FirmwareUpdateStatusType.ERROR,
                FirmwareUpdateErrorType.UNKNOWN_FILE,
            )
            self.logger.error("File not present at given path!")
            self.status_callback(self.current_status)
            self._reset_state()
            return

        with open("last_firmware_version.txt", "w") as file:
            file.write(self.firmware_handler.get_current_version())

        self.current_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.INSTALLING
        )
        self.logger.info(
            "Beginning firmware installation process "
            f"with file path: {file_path}"
        )
        self.status_callback(self.current_status)

        self.firmware_handler.install_firmware(file_path)

    def handle_abort(self) -> None:
        """Handle the abort command received from the platform."""
        if self.current_status is not None:
            self.logger.info("Aborting firmware installation")
            self.current_status = FirmwareUpdateStatus(
                FirmwareUpdateStatusType.ABORTED
            )
            self.status_callback(self.current_status)
            self._reset_state()
            if os.path.exists("last_firmware_version.txt"):
                os.remove("last_firmware_version.txt")

    def report_result(self) -> None:
        """Report the result of the firmware installation process."""
        self.logger.debug("Reporting firmware update result")

        if not os.path.exists("last_firmware_version.txt"):
            self.logger.debug("No stored firmware version found")
            return

        with open("last_firmware_version.txt") as file:
            last_firmware_version = file.read()

        if (
            last_firmware_version
            == self.firmware_handler.get_current_version()
        ):
            self.logger.warning(
                "Firmware version unchanged, reporting installation failed"
            )
            self.current_status = FirmwareUpdateStatus(
                FirmwareUpdateStatusType.ERROR,
                FirmwareUpdateErrorType.INSTALLATION_FAILED,
            )
            self.status_callback(self.current_status)
            self._reset_state()
            os.remove("last_firmware_version.txt")
            return

        self.logger.info(
            "Firmware version changed, reporting installation completed"
        )
        self.current_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.SUCCESS
        )
        self.status_callback(self.current_status)
        self._reset_state()
        os.remove("last_firmware_version.txt")

    def _reset_state(self) -> None:
        """Reset the state of the firmware update process."""
        self.current_status = None
