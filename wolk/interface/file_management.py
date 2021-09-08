"""Module responsible for handling files and file transfer."""
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
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_transfer_package import FileTransferPackage


class FileManagement(ABC):
    """
    File transfer manager.

    Enables device to transfer files from WolkAbout IoT Platform
     package by package or/and URL download.
    """

    @abstractmethod
    def __init__(
        self,
        status_callback: Callable[[str, FileManagementStatus], None],
        packet_request_callback: Callable[[str, int, int], None],
        url_status_callback: Callable[
            [str, FileManagementStatus, Optional[str]], None
        ],
    ) -> None:
        """
        Enable file management for device.

        :param status_callback: Reporting current file transfer status
        :type status_callback: Callable[[FileManagementStatus], None]
        :param packet_request_callback: Request file packet from Platform
        :type packet_request_callback: Callable[[str, int, int], None]
        :param url_status_callback: Report file url download status
        :type url_status_callback: Callable[[str, FileManagementStatus, Optional[str]], None]
        """
        raise NotImplementedError()

    @abstractmethod
    def get_preffered_package_size(self) -> int:
        """
        Return preffered package size for file transfer.

        :returns: preferred_package_size
        :rtype: int
        """
        raise NotImplementedError()

    @abstractmethod
    def supports_url_download(self) -> bool:
        """
        Return if the file management module supports URL download.

        :returns: supports_url_download
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
    def set_custom_url_downloader(
        self, downloader: Callable[[str, str], bool]
    ) -> None:
        """
        Set the URL file downloader to a custom implementation.

        :param downloader: Function that will download the file from the URL
        :type downloader: Callable[[str, str], bool]
        """
        raise NotImplementedError()

    @abstractmethod
    def handle_upload_initiation(
        self, file_name: str, file_size: int, file_hash: str
    ) -> None:
        """
        Start making package requests and set status to file transfer.

        :param file_name: File name
        :type file_name: str
        :param file_size: Size in bytes
        :type file_size: int
        :param file_hash: base64 encoded sha256 hash of file
        :type file_hash: str
        """
        raise NotImplementedError()

    @abstractmethod
    def handle_file_upload_abort(self) -> None:
        """Abort file upload and revert to idle status."""
        raise NotImplementedError()

    @abstractmethod
    def handle_file_binary_response(
        self, package: FileTransferPackage
    ) -> None:
        """
        Validate received package and store or use callback to request again.

        :param package: Package of file being transfered.
        :type package: FileTransferPackage
        """
        raise NotImplementedError()

    @abstractmethod
    def handle_file_url_download_initiation(self, file_url: str) -> None:
        """
        Start file transfer from specified URL.

        :param file_url: URL from where to download file
        :type file_url: str
        """
        raise NotImplementedError()

    @abstractmethod
    def handle_file_url_download_abort(self) -> None:
        """Abort file URL download."""
        raise NotImplementedError()

    @abstractmethod
    def get_file_list(self) -> List[Dict[str, Union[str, int]]]:
        """
        Return list of files present on device.

        Each list item is a dictionary that contains the name of the file,
        its size in bytes, and a MD5 checksum of the file.

        :returns: file_list
        :rtype: List[Dict[str, Union[str, int]]]

        """
        raise NotImplementedError()

    @abstractmethod
    def get_file_path(self, file_name: str) -> Optional[str]:
        """
        Return path to file if it exists.

        :param file_name: File for which to get path
        :type file_name: str
        :returns: file_path
        :rtype: Optional[str]
        """
        raise NotImplementedError()

    @abstractmethod
    def handle_file_delete(self, file_names: List[str]) -> None:
        """
        Delete files from device.

        :param file_names: Files to be deleted
        :type file_names: List[str]
        """
        raise NotImplementedError()

    @abstractmethod
    def handle_file_purge(self) -> None:
        """Delete all files from device."""
        raise NotImplementedError()
