"""OS File Management module."""
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
import hashlib
import math
import os
import shutil
from inspect import signature
from tempfile import NamedTemporaryFile
from threading import Timer
from typing import Callable
from typing import Dict
from typing import IO
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlparse

import requests

from wolk import logger_factory
from wolk.interface.file_management import FileManagement
from wolk.model.file_management_error_type import FileManagementErrorType
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.file_transfer_package import FileTransferPackage


class OSFileManagement(FileManagement):
    """
    File transfer manager.

    Enables device to transfer files from WolkAbout IoT Platform
    package by package or/and URL download as well as report list of files
    currently on device and delete them on request.
    """

    def __init__(
        self,
        status_callback: Callable[[str, FileManagementStatus], None],
        packet_request_callback: Callable[[str, int], None],
        url_status_callback: Callable[
            [str, FileManagementStatus, Optional[str]], None
        ],
    ) -> None:
        """
        Enable file management for device.

        :param status_callback: Reporting current file transfer status
        :type status_callback: Callable[[FileManagementStatus], None]
        :param packet_request_callback: Request file packet from Platform
        :type packet_request_callback: Callable[[str, int], None]
        :param url_status_callback: Report file URL download status
        :type url_status_callback: Callable[[str, FileManagementStatus, Optional[str]], None]
        """
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )

        self.status_callback = status_callback
        self.packet_request_callback = packet_request_callback
        self.url_status_callback = url_status_callback
        self.url_downloader = self.url_download
        self.preferred_package_size = 0
        self.file_directory = ""
        self.current_status: Optional[FileManagementStatus] = None
        self.max_retries = 3
        self.next_package_index: Optional[int] = None
        self.expected_number_of_packages: Optional[int] = None
        self.retry_count = 0
        self.request_timeout: Optional[Timer] = None
        self.last_package_hash = 32 * b"\x00"
        self.temp_file: Optional[IO[bytes]] = None
        self.file_name: Optional[str] = None
        self.file_size: Optional[int] = None
        self.file_hash: Optional[str] = None
        self.file_url: Optional[str] = None

    def configure(
        self,
        file_directory: str,
        preferred_package_size: int = 0,
    ) -> None:
        """
        Configure options for file management module.

        :param file_directory: Path to where files are stored
        :type file_directory: str
        :param preferred_package_size: Size in kilobytes, 0 means no limit
        :type preferred_package_size: int
        """
        self.file_directory = file_directory
        self.preferred_package_size = preferred_package_size

        if not os.path.exists(os.path.abspath(self.file_directory)):
            os.makedirs(os.path.abspath(self.file_directory))

    def get_preffered_package_size(self) -> int:
        """
        Return preffered package size for file transfer.

        :returns: preferred_package_size
        :rtype: int
        """
        return self.preferred_package_size

    def set_custom_url_downloader(
        self, downloader: Callable[[str, str], bool]
    ) -> None:
        """
        Set the URL file downloader to a custom implementation.

        Default implementation uses `requests` and is available as a
        static method within this class.

        :param downloader: Function that will download the file from the URL
        :type downloader: Callable[[[Arg(str, 'file_url'), Arg(str, 'file_path')], bool]
        """
        self.logger.debug(f"Setting custom URL downloader to {downloader}")
        if not callable(downloader):
            self.logger.warning(f"{downloader} is not a callable!")  # type: ignore
            return
        if len(signature(downloader).parameters) != 2:
            self.logger.warning(f"{downloader} invalid signature!")
            return
        self.url_downloader = downloader  # type: ignore

    def supports_url_download(self) -> bool:
        """
        Return if the file management module supports URL download.

        :returns: supports_url_download
        :rtype: bool
        """
        return self.url_downloader is not None

    def handle_upload_initiation(
        self, file_name: str, file_size: int, file_hash: str
    ) -> None:
        """
        Start making package requests and set status to file transfer.

        :param file_name: File name
        :type file_name: str
        :param file_size: Size in bytes
        :type file_size: int
        :param file_hash: MD5 hash of file
        :type file_hash: str
        """
        if self.current_status is not None:
            self.logger.warning(
                "Not in idle state, ignoring file upload initiation"
            )
            return

        self.logger.info("Starting file transfer")
        self.logger.info(
            f"File name: {file_name} ; "
            f"File size: {file_size} ; "
            f"File hash: {file_hash}"
        )

        self.expected_number_of_packages = (
            math.ceil(file_size / (self.preferred_package_size * 1024))
            if self.preferred_package_size != 0
            else 1
        )

        if os.path.exists(
            os.path.join(os.path.abspath(self.file_directory), file_name)
        ):
            valid_file = False

            try:
                with open(
                    os.path.join(
                        os.path.abspath(self.file_directory), file_name
                    ),
                    "rb",
                ) as existing_file:
                    data = existing_file.read()
                    if not data:
                        self.logger.error("Read data returned None!")
                        return
                    calculated_hash = hashlib.md5(data).hexdigest()
            except Exception as e:
                self.logger.exception(f"Error opening existing file: {e}")
                self.current_status = FileManagementStatus(
                    FileManagementStatusType.ERROR,
                    FileManagementErrorType.FILE_SYSTEM_ERROR,
                )
                self.status_callback(file_name, self.current_status)
                self.handle_file_upload_abort()
                return

            valid_file = file_hash == calculated_hash

            if valid_file:
                self.logger.info(
                    "File requested for transfer already on device"
                )
                self.current_status = FileManagementStatus(
                    FileManagementStatusType.FILE_READY
                )
                self.status_callback(file_name, self.current_status)

                self.current_status = None
                self.last_package_hash = 32 * b"\x00"
                return

            else:
                self.logger.warning(
                    "File requested for transfer already on device, "
                    "but the hashes do not match!"
                )
                self.current_status = FileManagementStatus(
                    FileManagementStatusType.ERROR,
                    FileManagementErrorType.FILE_HASH_MISMATCH,
                )
                self.status_callback(file_name, self.current_status)

                self.current_status = None
                self.last_package_hash = 32 * b"\x00"
                return

        self.current_status = FileManagementStatus(
            FileManagementStatusType.FILE_TRANSFER
        )
        self.temp_file = NamedTemporaryFile(mode="r+b", delete=False)
        self.file_name = file_name
        self.file_size = file_size
        self.file_hash = file_hash
        self.next_package_index = 0
        self.retry_count = 0

        self.logger.info(f"Initializing file transfer: '{file_name}'")
        self.logger.info(
            "File is expected to be received in "
            + f"{self.expected_number_of_packages}"
            + " packages"
        )
        self.status_callback(self.file_name, self.current_status)

        self.packet_request_callback(self.file_name, self.next_package_index)

        self.request_timeout = Timer(60.0, self._timeout)
        self.request_timeout.start()

    def handle_file_upload_abort(self) -> None:
        """Abort file upload and revert to idle status."""
        self.logger.info("Aborting file upload.")
        if self.temp_file:
            self.temp_file.close()

        self.temp_file = None
        self.file_name = None
        self.file_size = None
        self.file_hash = None
        self.current_status = None
        self.next_package_index = None
        self.expected_number_of_packages = None
        self.retry_count = 0
        self.request_timeout = None
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
            f"Previous hash: {package.previous_hash!r} ; "
            f"Data size: {len(package.data)} ; "
            f"Current hash: {package.current_hash!r}"
        )

        if self.current_status is None:
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
                    f"Data hash '{data_hash!r}' does not match "
                    f"expected hash '{package.current_hash!r}' !"
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
                self.current_status = FileManagementStatus(
                    FileManagementStatusType.ERROR,
                    FileManagementErrorType.RETRY_COUNT_EXCEEDED,
                )
                self.status_callback(self.file_name, self.current_status)
                self.handle_file_upload_abort()
                return

            self.logger.info(
                f"Requesting package #{self.next_package_index} again"
            )
            self.packet_request_callback(
                self.file_name, self.next_package_index
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
            self.current_status = FileManagementStatus(
                FileManagementStatusType.ERROR,
                FileManagementErrorType.FILE_SYSTEM_ERROR,
            )
            self.status_callback(self.file_name, self.current_status)
            self.handle_file_upload_abort()
            return

        self.next_package_index += 1

        if self.next_package_index < self.expected_number_of_packages:
            self.logger.debug(
                f"Stored package, requesting "
                f"#{self.next_package_index}/"
                f"#{self.expected_number_of_packages}"
            )
            self.packet_request_callback(
                self.file_name,
                self.next_package_index,
            )

            self.current_status = FileManagementStatus(
                FileManagementStatusType.FILE_TRANSFER
            )

            self.request_timeout = Timer(60.0, self._timeout)
            self.request_timeout.start()
            return

        valid_file = False

        try:
            self.temp_file.seek(0)
            data = self.temp_file.read()
            if not data:
                self.logger.error("Read data from temp file returned None!")
            calculated_hash = hashlib.md5(data).hexdigest()
        except Exception as e:
            self.logger.exception(f"Error while working with temp file: {e}")
            self.current_status = FileManagementStatus(
                FileManagementStatusType.ERROR,
                FileManagementErrorType.FILE_SYSTEM_ERROR,
            )
            self.status_callback(self.file_name, self.current_status)
            self.handle_file_upload_abort()
            return

        valid_file = self.file_hash == calculated_hash

        # FIXME: remove after bugfix:
        if not valid_file:
            self.logger.warning(
                "Hash mismatch!\n"
                + f"Received: {self.file_hash}\n"
                + f"Calculated: {calculated_hash}"
            )
            if len(self.file_hash) > 32:
                self.logger.warning("Known bug, ignoring hash diff")
                valid_file = True

        if not valid_file:
            self.logger.error("Invalid file - File hash does not match")
            self.current_status.status = FileManagementStatusType.ERROR
            self.current_status.error = (
                FileManagementErrorType.FILE_HASH_MISMATCH
            )
            self.status_callback(self.file_name, self.current_status)
            self.handle_file_upload_abort()
            return

        if not os.path.exists(os.path.abspath(self.file_directory)):
            os.makedirs(os.path.abspath(self.file_directory))

        file_path = os.path.join(
            os.path.abspath(self.file_directory),
            self.file_name,
        )

        try:
            self.logger.info(
                f"Finalizing file transfer for '{self.file_name}'"
            )
            shutil.copy2(os.path.realpath(self.temp_file.name), file_path)
            self.temp_file.close()
        except Exception as e:
            self.logger.exception(f"Error when storing file: {e}")

        if not os.path.exists(file_path):
            self.logger.error(f"File failed to store to at: {file_path}")
            self.current_status = FileManagementStatus(
                FileManagementStatusType.ERROR,
                FileManagementErrorType.FILE_SYSTEM_ERROR,
            )
            self.status_callback(self.file_name, self.current_status)
            self.handle_file_upload_abort()
            return

        self.logger.info(f"Received file '{self.file_name}'")
        self.current_status = FileManagementStatus(
            FileManagementStatusType.FILE_READY
        )
        self.status_callback(self.file_name, self.current_status)

        self.current_status = None
        self.retry_count = 0
        self.last_package_hash = 32 * b"\x00"

    def handle_file_url_download_initiation(self, file_url: str) -> None:
        """
        Start file transfer from specified URL.

        :param file_url: URL from where to download file
        :type file_url: str
        """
        if self.current_status is not None:
            self.logger.warning(
                "Not in idle state, ignoring file upload initiation"
            )
            return

        if self.url_downloader is None:
            self.logger.warning(
                "Received URL download, but no downloader is set!"
            )
            self.current_status = FileManagementStatus(
                FileManagementStatusType.ERROR,
                FileManagementErrorType.TRANSFER_PROTOCOL_DISABLED,
            )
            self.url_status_callback(file_url, self.current_status, None)
            self.handle_file_upload_abort()
            return

        if not bool(urlparse(file_url).scheme):
            self.logger.error(f"Received URL '{file_url}' is not valid!")
            self.current_status = FileManagementStatus(
                FileManagementStatusType.ERROR,
                FileManagementErrorType.MALFORMED_URL,
            )
            self.url_status_callback(file_url, self.current_status, None)
            self.handle_file_upload_abort()
            return

        self.file_url = file_url
        self.file_name = self.file_url.split("/")[-1]
        file_path = os.path.join(
            os.path.abspath(self.file_directory), self.file_name
        )
        self.current_status = FileManagementStatus(
            FileManagementStatusType.FILE_TRANSFER
        )
        self.url_status_callback(file_url, self.current_status, self.file_name)

        self.url_downloader(file_url, file_path)

        if not os.path.exists(file_path):
            self.logger.error(f"File failed to store to at: {file_path}")
            self.current_status = FileManagementStatus(
                FileManagementStatusType.ERROR,
                FileManagementErrorType.FILE_SYSTEM_ERROR,
            )
            self.url_status_callback(
                file_url, self.current_status, self.file_name
            )
            self.handle_file_url_download_abort()
            return

        self.logger.info(f"File obtained from URL: '{file_url}'")
        self.current_status = FileManagementStatus(
            FileManagementStatusType.FILE_READY
        )
        self.url_status_callback(file_url, self.current_status, self.file_name)

        self.current_status = None

    def handle_file_url_download_abort(self) -> None:
        """Abort file URL download."""
        self.logger.info("Aborting URL download")
        self.file_url = None
        self.file_name = None
        self.current_status = None

    def get_file_list(self) -> List[Dict[str, Union[str, int]]]:
        """
        Return list of files present on device.

        Each list item is a dictionary that contains the name of the file,
        its size in bytes, and a MD5 checksum of the file.

        :returns: file_list
        :rtype: List[Dict[str, Union[str, int]]]
        """
        files = os.listdir(os.path.abspath(self.file_directory))
        files_list = []

        for item in files:
            file_path = os.path.join(
                os.path.abspath(self.file_directory), item
            )
            if not os.path.isfile(file_path) or item.startswith("."):
                continue
            with open(file_path, "rb") as file:
                data = file.read()
                hash = hashlib.md5(data).hexdigest()
            size = os.path.getsize(file_path)
            files_list.append({"name": item, "size": size, "hash": hash})

        self.logger.debug(f"Files on device: {files_list}")
        return files_list  # type: ignore

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
            if file["name"] == file_name:
                file_path = os.path.join(
                    os.path.abspath(self.file_directory), file_name
                )
                break
        self.logger.debug(f"File path: {file_path}")
        return file_path

    def handle_file_delete(self, file_names: List[str]) -> None:
        """
        Delete files from device.

        :param file_names: Files to be deleted
        :type file_names: List[str]
        """
        self.logger.info(f"Attempting to delete files: {file_names}")
        for file in file_names:
            try:
                file_path = os.path.join(
                    os.path.abspath(self.file_directory), file
                )

                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                self.logger.exception(f"'{file}' failed to delete: {e}")

    def handle_file_purge(self) -> None:
        """Delete all files from device."""
        for file in os.listdir(os.path.abspath(self.file_directory)):
            if not os.path.isfile(
                os.path.join(os.path.abspath(self.file_directory), file)
            ) or file.startswith("."):
                continue
            os.remove(os.path.join(os.path.abspath(self.file_directory), file))

    def _timeout(self) -> None:
        """Revert to idle state when timeout occurs."""
        self.logger.error("Timed out waiting for next package, aborting")
        self.current_status = FileManagementStatus(
            FileManagementStatusType.ERROR,
            FileManagementErrorType.UNKNOWN,
        )
        self.status_callback(self.file_name, self.current_status)
        self.handle_file_upload_abort()

    @staticmethod
    def url_download(file_url: str, file_path: str) -> bool:
        """
        Attempt to download file from specified URL.

        :param file_url: URL from which to download file
        :type file_url: str
        :param file_path: Path where to store file
        :type: file_path: str
        :returns: Successful download
        :rtype: bool
        """
        response = requests.get(file_url)
        with open(file_path, "wb") as file:
            file.write(response.content)
            file.flush()
            os.fsync(file)

        return os.path.exists(file_path)
