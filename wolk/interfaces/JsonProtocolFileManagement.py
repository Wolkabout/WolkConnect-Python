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

from enum import Enum

from wolk.interfaces.FileManagement import FileManagement

from wolk.models.InboundMessage import InboundMessage
from wolk.models.OutboundMessage import OutboundMessage

from wolk import LoggerFactory

"""
Json Protocol File Management Module.
"""


class JsonProtocolFileManagement(FileManagement):
    """
    File transfer manager.

    Enables device to transfer files from WolkAbout IoT Platform
     package by package or/and URL download.
    """

    def __init__(
        self,
        prefered_package_size: int,
        max_file_size: int,
        download_location: str,
    ):
        """
        File Management using WolkAbout's JSON_PROTOCOL.

        :param prefered_package_size: Size in bytes
        :type prefered_package_size: int
        :param max_file_size: Maximum file size that can be stored
        :type max_file_size: int
        :param download_location: Path to where files are stored
        :type download_location: str
        """
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )

        self.logger.debug(
            "Prefered package size: %s ; Maximum file size %s "
            "; Download location: '%s'",
            prefered_package_size,
            max_file_size,
            download_location,
        )

        self.prefered_package_size = prefered_package_size
        self.max_file_size = max_file_size
        self.download_location = download_location

        class States(Enum):
            FILE_TRANSFER = 1
            FILE_READY = 2
            ERROR = 3
            ABORTED = 4

        class Errors(Enum):
            UNSPECIFIED_ERROR = 0
            TRANSFER_PROTOCOL_DISABLED = 1
            UNSUPPORTED_FILE_SIZE = 2
            MALFORMED_URL = 3
            FILE_HASH_MISMATCH = 4
            FILE_SYSTEM_ERROR = 5
            RETRY_COUNT_EXCEEDED = 10

        self.state = None
        self.error = None

    def handle_upload_initiation(
        self, file_management_command: InboundMessage
    ) -> bool:
        """Start making package requests and set status to file transfer."""
        pass

    def report_file_upload_status(
        self, file_transfer_status: dict
    ) -> OutboundMessage:
        """Send current file upload status to WolkAbout IoT Platform."""
        pass

    def handle_file_upload_abort(
        self, file_management_command: InboundMessage
    ) -> bool:
        """Abort file upload and revert to idle state."""
        pass

    def handle_file_binary_response(
        self, file_management_command: InboundMessage
    ) -> bool:
        """Store received package and validate."""
        pass

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
