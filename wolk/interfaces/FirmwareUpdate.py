#   Copyright 2018 WolkAbout Technology s.r.o.
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

"""
FirmwareUpdate Module.
"""


class FirmwareUpdate(ABC):
    """
    Firmware Update enabler.

    Responsible for handling file and URL download, as well as reporting firmware status.
    Should be implemented to depend upon an object of FirmwareHandler class
    """

    @abstractmethod
    def handle_file_upload(self, firmware_command):
        """Pass the information necessary to start a file download to an instance of FirmwareHandler."""
        pass

    @abstractmethod
    def handle_url_download(self, firmware_command):
        """Pass the information necessary to start a URL download to an instance of FirmwareHandler."""
        pass

    @abstractmethod
    def handle_url_download_result(self, result):
        """Handle the result of the url file download reported from an instance of FirmwareHandler."""
        pass

    @abstractmethod
    def handle_install(self):
        """Pass the install command to an instance of FirmwareHandler."""
        pass

    @abstractmethod
    def handle_abort(self):
        """Pass the abort command to an instance of FirmwareHandler."""
        pass

    @abstractmethod
    def handle_packet(self, packet):
        """Pass the packet to an instance of FirmwareHandler."""
        pass

    @abstractmethod
    def report_result(self):
        """Report the results of the firmware update process."""
        pass

    @abstractmethod
    def set_on_file_packet_request_callback(self, on_file_packet_request_callback):
        """Set a callback function to handle file packet requests."""
        pass

    @abstractmethod
    def set_on_status_callback(self, on_status_callback):
        """Set a callback fucntion to handle firmware status reporting."""
        pass
