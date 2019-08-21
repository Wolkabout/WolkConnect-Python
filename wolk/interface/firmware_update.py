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


class FirmwareUpdate(ABC):
    """
    Firmware Update enabler.

    Responsible for supervising firmware installation and reporting current
    firmware installation status and version.
    """

    @abstractmethod
    def handle_install(self):
        """Handle received firmware installation command."""
        pass

    @abstractmethod
    def handle_abort(self):
        """Handle received firmware installation abort command."""
        pass

    @abstractmethod
    def report_result(self):
        """Report the results of the firmware update process."""
        pass

    @abstractmethod
    def set_on_status_callback(self, on_status_callback):
        """Set a callback function to handle firmware status reporting."""
        pass

    @abstractmethod
    def set_installer(self, installer: Callable[[str], None]) -> None:
        """Set firmware installer function."""
        pass
