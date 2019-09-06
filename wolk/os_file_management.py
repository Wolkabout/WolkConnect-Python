"""OS File Management module."""
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
import os
import shutil
from threading import Timer
from urllib.parse import urlparse
import tempfile
from typing import Callable, List, Optional

import requests

from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.file_management_error_type import FileManagementErrorType
from wolk.model.file_transfer_package import FileTransferPackage
from wolk.interface.file_management import FileManagement
from wolk import logger_factory


class OSFileManagement(FileManagement):
    """
    File transfer manager.

    Enables device to transfer files from WolkAbout IoT Platform
    package by package or/and URL download as well as report list of files
    currently on device and delete them on request.
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
        self.logger = logger_factory.logger_factory.get_logger(
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
        self.next_package_index = None
        self.expected_number_of_packages = None
        self.retry_count = None
        self.request_timeout = None
        self.install_timer = None
        self.last_package_hash = 32 * b"\x00"

        if not os.path.exists(os.path.abspath(self.download_location)):
            os.mkdir(os.path.abspath(self.download_location))

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
        self.logger.info("Starting file transfer")
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
            self.file_upload_status_callback(
                self.file_name, self.current_status
            )
            self.current_status = FileManagementStatus()
            return

        self.expected_number_of_packages = math.ceil(
            file_size / self.preferred_package_size
        )

        if os.path.exists(
            os.path.join(os.path.abspath(self.download_location), file_name)
        ):
            valid_file = False

            sha256_received_file_hash = base64.b64decode(
                file_hash + ("=" * (-len(file_hash) % 4))
            )
            sha256_file_hash = hashlib.sha256()

            existing_file = open(
                os.path.join(
                    os.path.abspath(self.download_location), file_name
                ),
                "rb",
            )

            for x in range(self.expected_number_of_packages):

                existing_file.seek(x * self.preferred_package_size)
                chunk = existing_file.read(self.preferred_package_size)
                if not chunk:
                    self.logger.error("File size too small!")
                    break

                sha256_file_hash.update(chunk)

            sha256_file_hash = sha256_file_hash.digest()
            valid_file = sha256_received_file_hash == sha256_file_hash

            if valid_file:
                self.logger.info(
                    "File requested for transfer already on device"
                )
                self.current_status.status = (
                    FileManagementStatusType.FILE_READY
                )
                self.current_status.error = None
                self.file_upload_status_callback(
                    file_name, self.current_status
                )

                self.current_status = FileManagementStatus()
                self.last_package_hash = 32 * b"\x00"
                return

        self.current_status.status = FileManagementStatusType.FILE_TRANSFER
        self.temp_file = tempfile.NamedTemporaryFile(mode="a+b", delete=False)
        self.file_name = file_name
        self.file_size = file_size
        self.file_hash = file_hash
        self.next_package_index = 0
        self.retry_count = 0

        self.logger.info(
            "Initializing file transfer and requesting first package"
        )
        self.file_upload_status_callback(self.file_name, self.current_status)

        if self.file_size < self.preferred_package_size:
            self.request_file_binary_callback(
                self.file_name, self.next_package_index, self.file_size + 64
            )
        else:
            self.request_file_binary_callback(
                self.file_name,
                self.next_package_index,
                self.preferred_package_size + 64,
            )

        self.request_timeout = Timer(60.0, self._timeout)
        self.request_timeout.start()

    def _set_file_upload_status_callback(
        self, callback: Callable[[str, FileManagementStatus], None]
    ) -> None:
        """
        Set the callback method for reporting current status.

        :param callback: Method to call
        :type callback: Callable[[str, FileManagementStatus], None]
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
        self.next_package_index = None
        self.expected_number_of_packages = None
        self.retry_count = None
        self.request_timeout = None
        self.install_timer = None
        self.last_package_hash = 32 * b"\x00"

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

        if self.request_timeout:
            self.request_timeout.cancel()

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
                    f"Valid package #{self.next_package_index} received"
                )
                valid_package = True

        if (
            not valid_package
            or self.last_package_hash != package.previous_hash
        ):
            self.logger.warning("Received invalid file package")
            self.retry_count += 1

            if self.retry_count >= self.max_retries:
                self.logger.error(
                    "Retry count exceeded, aborting file transfer"
                )
                self.current_status.status = FileManagementStatusType.ERROR
                self.current_status.error = (
                    FileManagementErrorType.RETRY_COUNT_EXCEEDED
                )
                self.file_upload_status_callback(
                    self.file_name, self.current_status
                )
                self.handle_file_upload_abort()
                return

            else:
                self.logger.info(
                    f"Requesting package #{self.next_package_index} again"
                )
                self.request_file_binary_callback(
                    self.file_name,
                    self.next_package_index,
                    self.preferred_package_size + 64,
                )

                self.request_timeout = Timer(60.0, self._timeout)
                self.request_timeout.start()
                return

        self.last_package_hash = package.current_hash

        try:
            self.temp_file.write(package.data)
            self.temp_file.flush()
            os.fsync(self.temp_file)
        except Exception:
            self.logger.error(
                "Failed to write package, aborting file transfer"
            )
            self.current_status.status = FileManagementStatusType.ERROR
            self.current_status.error = (
                FileManagementErrorType.FILE_SYSTEM_ERROR
            )
            self.file_upload_status_callback(
                self.file_name, self.current_status
            )
            self.handle_file_upload_abort()
            return

        self.next_package_index += 1

        if self.next_package_index < self.expected_number_of_packages:
            self.logger.debug(
                f"Stored package, requesting "
                f"#{self.next_package_index}/"
                f"#{self.expected_number_of_packages}"
            )
            self.request_file_binary_callback(
                self.file_name,
                self.next_package_index,
                self.preferred_package_size + 64,
            )

            self.request_timeout = Timer(60.0, self._timeout)
            self.request_timeout.start()
            return

        valid_file = False

        sha256_received_file_hash = base64.b64decode(
            self.file_hash + ("=" * (-len(self.file_hash) % 4))
        )
        sha256_file_hash = hashlib.sha256()

        for x in range(self.expected_number_of_packages):

            self.temp_file.seek(x * self.preferred_package_size)
            chunk = self.temp_file.read(self.preferred_package_size)
            if not chunk:
                self.logger.error("File size too small!")
                break

            sha256_file_hash.update(chunk)

        sha256_file_hash = sha256_file_hash.digest()
        valid_file = sha256_received_file_hash == sha256_file_hash

        if not valid_file:
            self.logger.error("Invalid file - File hash does not match")
            self.current_status.status = FileManagementStatusType.ERROR
            self.current_status.error = (
                FileManagementErrorType.FILE_HASH_MISMATCH
            )
            self.file_upload_status_callback(
                self.file_name, self.current_status
            )
            self.handle_file_upload_abort()
            return

        if not os.path.exists(os.path.abspath(self.download_location)):
            os.makedirs(os.path.abspath(self.download_location))

        file_path = os.path.join(
            os.path.abspath(self.download_location), self.file_name
        )

        # TODO: File already exists?
        shutil.copy2(os.path.realpath(self.temp_file.name), file_path)
        self.temp_file.close()

        if not os.path.exists(file_path):
            self.logger.error(f"File failed to store to at: {file_path}")
            self.current_status.status = FileManagementStatusType.ERROR
            self.current_status.error = (
                FileManagementErrorType.FILE_SYSTEM_ERROR
            )
            self.file_upload_status_callback(
                self.file_name, self.current_status
            )
            self.handle_file_upload_abort()
            return

        self.logger.info(f"Received file '{self.file_name}'")
        self.current_status.status = FileManagementStatusType.FILE_READY
        self.current_status.error = None
        self.file_upload_status_callback(self.file_name, self.current_status)

        self.current_status = FileManagementStatus()
        self.last_package_hash = 32 * b"\x00"

    def handle_file_url_download_initiation(self, file_url: str) -> None:
        """
        Start file transfer from specified URL.

        :param file_url: URL from where to download file
        :type file_url: str
        """
        if self.current_status.status is not None:
            self.logger.warning(
                "Not in idle state, ignoring file upload initiation"
            )
            return

        if not bool(urlparse(file_url).scheme):
            self.logger.error(f"Received URL '{file_url}' is not valid!")
            self.current_status.status = FileManagementStatusType.ERROR
            self.current_status.error = FileManagementErrorType.MALFORMED_URL
            self.file_url_download_status_callback(
                file_url, self.current_status
            )
            self.handle_file_upload_abort()
            return

        self.file_url = file_url
        self.file_name = self.file_url.split("/")[-1]
        file_path = os.path.join(
            os.path.abspath(self.download_location), self.file_name
        )

        self.current_status.status = FileManagementStatusType.FILE_TRANSFER
        self.file_url_download_status_callback(file_url, self.current_status)

        response = requests.get(file_url)
        with open(file_path, "ab") as file:
            file.write(response.content)
            file.flush()
            os.fsync(file)

        if not os.path.exists(file_path):
            self.logger.error(f"File failed to store to at: {file_path}")
            self.current_status.status = FileManagementStatusType.ERROR
            self.current_status.error = (
                FileManagementErrorType.FILE_SYSTEM_ERROR
            )
            self.file_url_download_status_callback(
                file_url, self.current_status
            )
            self.handle_file_url_download_abort()
            return

        self.logger.info(f"File obtained from URL: '{file_url}'")
        self.current_status.status = FileManagementStatusType.FILE_READY
        self.current_status.error = None
        self.file_url_download_status_callback(
            file_url, self.current_status, self.file_name
        )

        self.current_status = FileManagementStatus()

    def handle_file_url_download_abort(self) -> None:
        """Abort file URL download."""
        self.logger.info("Aborting URL download")
        self.file_url = None
        self.file_name = None
        self.current_status = FileManagementStatus()

    def get_file_list(self) -> List[str]:
        """
        Return list of files present on device.

        :returns: file_list
        :rtype: List[str]
        """
        file_list = os.listdir(os.path.abspath(self.download_location))

        if file_list:
            for item in file_list:
                if not os.path.isfile(
                    os.path.join(os.path.abspath(self.download_location), item)
                ) or item.startswith("."):
                    file_list.remove(item)
        else:
            file_list = []

        self.logger.debug(f"Files on device: {file_list}")
        return file_list

    def get_file_path(self, file_name: str) -> Optional[str]:
        """
        Return path to file if it exists.

        :param file_name: File for which to get path
        :type file_name: str
        :returns: file_path
        :rtype: Optional[str]
        """
        self.logger.debug(f"Get file path for file: {file_name}")
        file_path = None
        for file in self.get_file_list():
            if file == file_name:
                file_path = os.path.join(
                    os.path.abspath(self.download_location), file_name
                )
                break
        self.logger.debug(f"File path: {file_path}")
        return file_path

    def handle_file_list_confirm(self) -> None:
        """Acknowledge file list response from WolkAbout IoT Platform."""
        pass

    def handle_file_delete(self, file_name: str) -> None:
        """
        Delete file from device.

        :param file_name: File to be deleted
        :type file_name: str
        """
        self.logger.info(f"Attempting to delete file: '{file_name}'")
        file_path = os.path.join(
            os.path.abspath(self.download_location), file_name
        )

        if os.path.exists(file_path):
            os.remove(file_path)

    def handle_file_purge(self) -> None:
        """Delete all files from device."""
        for file in os.listdir(os.path.abspath(self.download_location)):
            if not os.path.isfile(file) or file.startswith("."):
                continue
            os.remove(
                os.path.join(os.path.abspath(self.download_location), file)
            )

    def _timeout(self) -> None:
        self.logger.error("Timed out waiting for next package, aborting")
        self.current_status.status = FileManagementStatusType.ERROR
        self.current_status.error = FileManagementErrorType.UNSPECIFIED_ERROR
        self.file_upload_status_callback(self.file_name, self.current_status)
        self.handle_file_upload_abort()
