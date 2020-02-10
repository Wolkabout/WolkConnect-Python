"""Firmware handler for file installation and version reporting."""
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


class FirmwareHandler(ABC):
    """Handle firmware installation and get current firmware version."""

    @abstractmethod
    def install_firmware(self, firmware_file_path: str) -> None:
        """
        Handle the installation of the firmware file.

        :param firmware_file_path: Path where the firmware file is located
        :type firmware_file_path: str
        """
        raise NotImplementedError()

    @abstractmethod
    def get_current_version(self) -> str:
        """
        Obtain device's current firmware version.

        :returns: version
        :rtpe: str
        """
        raise NotImplementedError()
