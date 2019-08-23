"""File Management module."""
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

import base64
import hashlib
import math
from threading import Timer
import tempfile
from typing import Callable, List, Optional

from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.file_management_error_type import FileManagementErrorType
from wolk.model.file_transfer_package import FileTransferPackage
from wolk.interfaces.file_management import FileManagement
from wolk import LoggerFactory


class JsonProtocolFileManagement(FileManagement):
    """
    File transfer manager.

    Enables device to transfer files from WolkAbout IoT Platform
    package by package or/and URL download as well as report list of files
    currently on device.
    """

    def __init__(
        self,
        preferred_package_size: int,
        max_file_size: int,
        download_location: str,
    ):
        """
        File Management Module.

        :param preferred_package_size: Size in bytes
        :type preferred_package_size: int
        :param max_file_size: Maximum file size that can be stored
        :type max_file_size: int
        :param download_location: Path to where files are stored
        :type download_location: str
        """
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )

        self.logger.debug(
            f"Preferred package size: {preferred_package_size} ; "
            f"Maximum file size {max_file_size} ; "
            f"Download location: '{download_location}'"
        )

        self.preferred_package_size = preferred_package_size
        self.max_file_size = max_file_size
        self.download_location = download_location

        self.current_status = FileManagementStatus()

        self.max_retries = 3
        self.next_chunk_index = None
        self.expected_number_of_chunks = None
        self.retry_count = None
        self.request_timeout = None
        self.install_timer = None
        self.last_packet_hash = 32 * b"\x00"

    def handle_upload_initiation(
        self, file_name: str, file_size: int, file_hash: str
    ) -> None:
        """Start making package requests and set status to file transfer.

        :param file_name: File name
        :type file_name: str
        :param file_size: Size in bytes
        :type file_size: int
        :param file_hash: base64 encoded sha256 hash of file
        :type file_hash: str
        """
        self.logger.info(
            f"File name: {file_name} ; "
            f"File size: {file_size} ; "
            f"File hash: {file_hash}"
        )

        if self.current_status.status is not None:
            self.logger.warning(
                "Not in idle state, ignoring file upload initiation"
            )
            return

        if file_size > self.max_file_size:
            self.logger.error("File size too big, canceling")
            self.current_status.status = FileManagementStatusType.ERROR
            self.current_status.error = (
                FileManagementErrorType.UNSUPPORTED_FILE_SIZE
            )
            self.file_upload_status_callback(self.current_status)
            self.current_status = FileManagementStatus()
            return

        self.current_status.status = FileManagementStatusType.FILE_TRANSFER
        self.temp_file = tempfile.NamedTemporaryFile(mode="a+b", delete=False)
        self.file_name = file_name
        self.file_size = file_size
        self.file_hash = file_hash
        self.expected_number_of_chunks = math.ceil(
            self.file_size / self.firmware_handler.chunk_size
        )
        self.next_chunk_index = 0
        self.retry_count = 0

        self.logger.info(
            "Initializing file transfer and requesting first package"
        )
        self.file_upload_status_callback(self.current_status)

        if self.file_size < self.preferred_package_size:
            self.request_file_binary_callback(
                self.file_name, self.next_chunk_index, self.file_size + 64
            )
        else:
            self.request_file_binary_callback(
                self.file_name,
                self.next_chunk_index,
                self.preferred_package_size + 64,
            )

        self.request_timeout = Timer(60.0, self._timeout)
        self.request_timeout.start()

    def _set_file_upload_status_callback(
        self, callback: Callable[[FileManagementStatus], None]
    ) -> None:
        """
        Set the callback method for reporting current status.

        :param callback: Method to call
        :type callback: Callable[[FileManagementStatus], None]
        """
        self.file_upload_status_callback = callback

    def _set_request_file_binary_callback(
        self, callback: Callable[[str, int, int], None]
    ) -> None:
        """
        Set the callback method for requesting file packets.

        :param callback: Method to call
        :type callback: Callable[[str, int, int], None]
        """
        self.request_file_binary_callback = callback

    def _set_file_url_download_status_callback(
        self,
        callback: Callable[[str, FileManagementStatus, Optional[str]], None],
    ) -> None:
        """
        Set the callback method for reporting file url download status.

        :param callback: Method to call
        :type callback: Callable[[str, FileManagementStatus, Optional[str]], None]
        """
        self.file_url_download_status_callback = callback

    def _set_file_list_report_callback(
        self, callback: Callable[[List[str]], None]
    ) -> None:
        """
        Set the callback method for reporting list of files present on device.

        :param callback: Method to call
        :type callback: Callable[[List[str]], None]
        """
        self.file_list_report_callback = callback

    def handle_file_upload_abort(self) -> None:
        """Abort file upload and revert to idle status."""
        self.logger.info("Aborting file upload.")
        if self.temp_file:
            self.temp_file.close()

        self.temp_file = None
        self.file_name = None
        self.file_size = None
        self.file_hash = None
        self.current_status = FileManagementStatus()
        self.next_chunk_index = None
        self.expected_number_of_chunks = None
        self.retry_count = None
        self.request_timeout = None
        self.install_timer = None
        self.last_packet_hash = 32 * b"\x00"

    def handle_file_binary_response(
        self, package: FileTransferPackage
    ) -> None:
        """
        Validate received package and store or use callback to request again.

        :param package: Package of file being transfered.
        :type package: FileTransferPackage
        """
        self.logger.debug(
            f"Previous hash: {package.previous_hash} ; "
            f"Data size: {len(package.data)} ; "
            f"Current hash: {package.current_hash}"
        )

        if (
            self.current_status.status
            != FileManagementStatusType.FILE_TRANSFER
        ):
            self.logger.warning(
                "File transfer not in progress, ignoring package"
            )
            return

        valid_package = False

        if (
            len(package.previous_hash)
            + len(package.data)
            + len(package.current_hash)
            < 65
        ):
            self.logger.error("Received package size too small!")
        else:
            data_hash = hashlib.sha256(package.data).digest()
            if package.current_hash != data_hash:
                self.logger.error(
                    f"Data hash '{data_hash}' does not match "
                    f"expected hash '{package.current_hash}' !"
                )
            else:
                self.logger.debug(
                    f"Valid package #{self.next_chunk_index} received"
                )
                valid_package = True

        # TODO: Handle valid/invalid package, validate file on last package

    def handle_file_url_download_initiation(self, file_url: str) -> bool:
        """
        Start file transfer from specified URL.

        :param file_url: URL from where to download file
        :type file_url: str
        :returns: valid_url
        :rtype: bool
        """
        pass

    def handle_file_url_download_abort(self) -> bool:
        """
        Abort file URL download.

        :return: successfully_aborted
        :rtype: bool
        """
        pass

    def get_file_list(self) -> List[str]:
        """
        Return list of files present on device.

        :returns: file_list
        :rtype: List[str]
        """
        pass

    def handle_file_list_confirm(self) -> None:
        """Acknowledge file list response from WolkAbout IoT Platform."""
        pass

    def _timeout(self) -> None:
        self.logger.error("Timed out waiting for next package, aborting")
        self.current_status.status = FileManagementStatusType.ERROR
        self.current_status.error = FileManagementErrorType.UNSPECIFIED_ERROR
        self.file_upload_status_callback(self.current_status)
        self.handle_file_upload_abort()
