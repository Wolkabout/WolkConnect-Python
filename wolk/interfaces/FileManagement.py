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

from wolk.models.OutboundMessage import OutboundMessage
from wolk.models.InboundMessage import InboundMessage

"""
File Management Module.
"""


class FileManagement(ABC):
    """
    File transfer manager.

    Enables device to transfer files from WolkAbout IoT Platform
     package by package or/and URL download.
    """

    @abstractmethod
    def handle_upload_initiation(
        self, file_management_command: InboundMessage
    ) -> bool:
        """Start making package requests and set status to file transfer."""
        pass

    @abstractmethod
    def report_file_upload_status(
        self, file_transfer_status: dict
    ) -> OutboundMessage:
        """Send current file upload status to WolkAbout IoT Platform."""
        pass

    @abstractmethod
    def handle_file_upload_abort(
        self, file_management_command: InboundMessage
    ) -> bool:
        """Abort file upload and revert to idle state."""
        pass

    @abstractmethod
    def handle_file_binary_response(
        self, file_management_command: InboundMessage
    ) -> bool:
        """Store received package and validate."""
        pass

    @abstractmethod
    def request_file_binary(self, package_request: dict) -> OutboundMessage:
        """Request package from WolkAbout IoT Platform."""
        pass

    def handle_file_url_download_initiation(
        self, file_management_command: InboundMessage
    ) -> bool:
        """Start file transfer from specified URL."""
        raise NotImplementedError()

    def handle_file_url_download_abort(
        self, file_management_command: InboundMessage
    ) -> bool:
        """Abort file URL download command from WolkAbout IoT Platform."""
        raise NotImplementedError()

    def report_file_url_download_status(
        self, file_transfer_status: dict
    ) -> OutboundMessage:
        """Send current file URL download status to WolkAbout IoT Platform."""
        raise NotImplementedError()

    def handle_file_list_request(
        self, file_management_command: InboundMessage
    ) -> bool:
        """Respond with list of files present on device."""
        raise NotImplementedError()

    def report_file_list(self, is_response: bool) -> OutboundMessage:
        """Send list of files present on device to WolkAbout IoT Platform."""
        raise NotImplementedError()

    def handle_file_list_confirm(
        self, file_management_command: InboundMessage
    ) -> None:
        """Acknowledge file list response from WolkAbout IoT Platform."""
        raise NotImplementedError()
