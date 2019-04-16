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

"""FileSystemFirmwareHandler Module."""

import os
import shutil
import tempfile
from threading import Timer
from urllib.parse import urlparse

from persistent_queue import PersistentQueue

from wolk import LoggerFactory
from wolk.interfaces.FirmwareHandler import FirmwareHandler


class FileSystemFirmwareHandler(FirmwareHandler):
    """
    Firmware handler that uses OS provided disk storage for firmware files.

    :ivar chunk_size: Desired chunk size in bytes
    :vartype chunk_size: int
    :ivar download_location: Where to store the completed firmware file
    :vartype download_location: str
    :ivar file_name: Name of firmware file
    :vartype file_name: str
    :ivar file_size: Size of firmware file in bytes
    :vartype file_size: int
    :ivar file_url: URL where there firmware file is located
    :vartype file_url: str
    :ivar firmware_installer: Installer of firmware file
    :vartype firmware_installer: wolk.interfaces.FirmwareInstaller.FirmwareInstaller
    :ivar firmware_url_download_handler: URL downloader
    :vartype firmware_url_download_handler: wolk.interfaces.FirmwareURLDownloadHandler.FirmwareURLDownloadHandler or None
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar max_file_size: Maximum file size supported by device in bytes
    :vartype max_file_size: int
    :ivar report_result_callback: Callback for reporting URL download result
    :vartype report_result_callback: function
    :ivar temp_file: Handle of temp file used to store incomplete firmware file
    :vartype temp_file: file object
    :ivar version: Current version of the device firmware
    :vartype version: str
    :ivar version_persister: Means of storing current version on disk
    :vartype version_persister: persistent_queue.PersistentQueue
    """

    def __init__(
        self,
        version,
        chunk_size,
        max_file_size,
        firmware_installer,
        download_location,
        firmware_url_download_handler=None,
    ):
        """
        Handle file manipulation on disk storage.

        :param version: Current version of the device firmware
        :type version: str
        :param chunk_size: Desired chunk size in bytes
        :type chunk_size: int
        :param max_file_size: Maximum file size supported by device in bytes
        :type max_file_size: int
        :param firmware_installer: Installer of firmware file
        :type firmware_installer: wolk.interfaces.FirmwareInstaller.FirmwareInstaller
        :param download_location: Where to store the completed firmware file
        :type download_location: str
        :param firmware_url_download_handler: Optional URL downloader
        :type firmware_url_download_handler: wolk.interfaces.FirmwareURLDownloadHandler.FirmwareURLDownloadHandler or None
        """
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(
            "Init:  Version: %s ; Chunk size: %s ; Max file size: %s ; "
            "Firmware installer: %s ; Download location: '%s'  "
            "Firmware URL download handler: %s",
            version,
            chunk_size,
            max_file_size,
            firmware_installer,
            download_location,
            firmware_url_download_handler,
        )
        self.version = version
        self.chunk_size = chunk_size
        self.max_file_size = max_file_size
        self.download_location = download_location
        self.firmware_installer = firmware_installer
        self.firmware_url_download_handler = firmware_url_download_handler
        self.temp_file = None
        self.file_name = None
        self.file_size = None
        self.file_url = None
        self.report_result_callback = None
        self.version_persister = PersistentQueue("persisted_version")

    def update_start(self, file_name, file_size):
        """
        Start receiving the firmware file.

        :param file_name: Name of the firmware file
        :type file_name: str
        :param file_size: Size of the firmware file in bytes
        :type file_size: int

        :returns: result
        :rtype: bool
        """
        self.logger.debug(
            "update_start called - File name: %s ; File size: %s", file_name, file_size
        )
        if file_size > self.max_file_size:
            self.logger.debug("update_start - File size too big, returning False")
            return False

        self.temp_file = tempfile.NamedTemporaryFile(mode="a+b", delete=False)
        self.file_name = file_name
        self.file_size = file_size
        self.logger.debug("update_start - Temporary file created, returning True")
        return True

    def update_finalize(self):
        """
        Finalize firmware installation process.

        Copies the content of the temporary file to
        the desired download location.
        Calls the provided firmware installer's install_firmware function
        """
        self.logger.debug("update_finalize called")
        self.logger.debug(
            "download location: %s ;file_name: %s ;temp_file: %s",
            self.download_location,
            self.file_name,
            self.temp_file,
        )

        if not os.path.exists(os.path.abspath(self.download_location)):
            os.makedirs(os.path.abspath(self.download_location))

        firmware_file_path = os.path.join(
            os.path.abspath(self.download_location), self.file_name
        )

        if self.temp_file:
            shutil.copy2(os.path.realpath(self.temp_file.name), firmware_file_path)
            self.temp_file.close()

        self.logger.info(
            "Firmware file copied to download location from "
            "temporary file, calling firmware_installer.install_firmware "
            "with path: %s",
            firmware_file_path,
        )
        self.firmware_installer.install_firmware(firmware_file_path)

    def update_abort(self):
        """Abort the firmware update process."""
        self.logger.debug("update_abort called")

        if self.temp_file:
            self.temp_file.close()

        self.temp_file = None
        self.file_name = None
        self.file_size = None
        self.file_url = None

    def write_chunk(self, chunk):
        """
        Write a chunk of the firmware file to the temporary file.

        :param chunk: A piece of the firmware file
        :type chunk: bytes

        :returns: result
        :rtype: bool
        """
        self.logger.debug("write_chunk called - Chunk size: %s", len(chunk))

        self.temp_file.write(chunk)
        self.temp_file.flush()
        os.fsync(self.temp_file)
        self.logger.debug("write_chunk - Chunk written, returning True")
        return True

    def read_chunk(self, index):
        """
        Read a chunk of the temporary firmware file.

        :param index: Offset from the beginning of the file
        :type index: int

        :returns: chunk
        :rtype: bytes
        """
        self.logger.debug("read_chunk called - Index: %s", index)

        self.temp_file.seek(index * self.chunk_size)
        chunk = self.temp_file.read(self.chunk_size)
        self.logger.debug("read_chunk - Chunk size: %s", len(chunk))
        return chunk

    def persist_version(self, version):
        """
        Place the current firmware version into persistent storage.

        Later to be used to determine the result
        of the firmware update process

        :param version: Current firmware version
        :type version: str

        :returns: result
        :rtype: bool
        """
        self.logger.debug("persist_version called - Version: %s", version)

        self.version_persister.clear()
        self.version_persister.flush()
        self.version_persister.push(version)
        self.logger.debug("persist_version - Persisted version, returning True")
        return True

    def unpersist_version(self):
        """
        Remove the firmware version from persistent storage.

        :returns: version
        :rtype: str or None
        """
        self.logger.debug("unpersist_version called")

        if not self.version_persister.peek():
            self.version_persister.clear()
            self.logger.debug(
                "unpersist_version - No persisted version, returning None"
            )
            return None
        else:
            version = self.version_persister.pop()
            self.version_persister.flush()
            self.logger.debug(
                "unpersist_version - Persisted version found, returning %s", version
            )
            return version

    def set_url_download_result_callback(self, callback):
        """
        Set callback for reporting URL download result.

        :param callback: Function to call
        :type callback: function
        """
        self.logger.debug(
            "set_url_download_result_callback called - Callback: %s", callback
        )
        self.report_result_callback = callback

    def update_start_url_download(self, file_url):
        """
        Start firmware file URL download process.

        Calls download function from firmware_url_download_handler.
        Returns the validity of the URL and calls download function if valid.

        :param file_url: URL that contains the firmware file
        :type file_url: str

        :returns: result
        :rtype: bool
        """
        self.logger.debug("update_start_url_download called - File URL: %s", file_url)

        if not self.firmware_url_download_handler:
            self.logger.debug(
                "update_start_url_download - No firmware_url_download_handler,"
                "returning False"
            )
            return False

        parsed_url = urlparse(file_url)

        if bool(parsed_url.scheme):

            self.file_url = file_url
            self.file_name = self.file_url.split("/")[-1]
            t = Timer(
                2.0,
                self.firmware_url_download_handler.download,
                [self.file_url, self.file_name, self.report_result_callback],
            )
            t.start()
            self.logger.debug(
                "update_start_url_download - Valid URL, calling "
                "firmware_url_download_handler.download and returning True"
            )
            return True

        else:

            self.logger.debug(
                "update_start_url_download - Invalid URL, returning False"
            )
            return False
