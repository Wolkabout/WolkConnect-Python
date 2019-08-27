"""Module responsible for handling files and file transfer."""
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
from typing import Callable, Optional, List

from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_transfer_package import FileTransferPackage


class FileManagement(ABC):
    """
    File transfer manager.

    Enables device to transfer files from WolkAbout IoT Platform
     package by package or/and URL download.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def _set_file_upload_status_callback(
        self, callback: Callable[[str, FileManagementStatus], None]
    ) -> None:
        """
        Set the callback method for reporting current status.

        :param callback: Method to call
        :type callback: Callable[[FileManagementStatus], None]
        """
        pass

    @abstractmethod
    def _set_request_file_binary_callback(
        self, callback: Callable[[str, int, int], None]
    ) -> None:
        """
        Set the callback method for requesting file packets.

        :param callback: Method to call
        :type callback: Callable[[str, int, int], None]
        """
        pass

    @abstractmethod
    def _set_file_url_download_status_callback(
        self,
        callback: Callable[[str, FileManagementStatus, Optional[str]], None],
    ) -> None:
        """
        Set the callback method for reporting file url download status.

        :param callback: Method to call
        :type callback: Callable[[str, FileManagementStatus, Optional[str]], None]
        """
        pass

    @abstractmethod
    def handle_file_upload_abort(self) -> None:
        """Abort file upload and revert to idle status."""
        pass

    @abstractmethod
    def handle_file_binary_response(
        self, package: FileTransferPackage
    ) -> None:
        """
        Validate received package and store or use callback to request again.

        :param package: Package of file being transfered.
        :type package: FileTransferPackage
        """
        pass

    @abstractmethod
    def handle_file_url_download_initiation(self, file_url: str) -> None:
        """
        Start file transfer from specified URL.

        :param file_url: URL from where to download file
        :type file_url: str
        """
        pass

    @abstractmethod
    def handle_file_url_download_abort(self) -> None:
        """Abort file URL download."""
        pass

    @abstractmethod
    def get_file_list(self) -> List[str]:
        """
        Return list of files present on device.

        :returns: file_list
        :rtype: List[str]
        """
        pass

    @abstractmethod
    def handle_file_list_confirm(self) -> None:
        """Acknowledge file list response from WolkAbout IoT Platform."""
        pass

    @abstractmethod
    def handle_file_delete(self, file_name: str) -> None:
        """
        Delete file from device.

        :param file_name: File to be deleted
        :type file_name: str
        """
        pass

    @abstractmethod
    def handle_file_purge(self) -> None:
        """Delete all files from device."""
        pass
