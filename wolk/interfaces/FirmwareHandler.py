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
FirmwareHandler Module.
"""


class FirmwareHandler(ABC):
    """
    Handle firmware update process.

    Implement this class to write and read files in persistent memory,
    persist firmware version and handle the process
    of installation of firmware file itself.
    Optionally provide implementation for URL download
    """

    @abstractmethod
    def update_start(self, file_name, file_size):
        """
        Start receiving the firmware file.

        :param file_name: name of the firmware file
        :type file_name: str
        :param file_size: size of the firmware file in bytes
        :type file_size: int

        :returns: result
        :rtype: bool
        """
        pass

    @abstractmethod
    def update_finalize(self):
        """Finish the process of firmware update."""
        pass

    @abstractmethod
    def update_abort(self):
        """Abort the process of firmware update."""
        pass

    @abstractmethod
    def write_chunk(self, chunk):
        """
        Write a chunk of the firmware file to the temporary file.

        :param chunk: A piece of the firmware file
        :type chunk: bytes

        :returns: result
        :rtype: bool
        """
        pass

    @abstractmethod
    def read_chunk(self, index):
        """
        Read a chunk of the temporary firmware file.

        :param index: offset from the beginning of the file
        :type index: int

        :returns: chunk
        :rtype: bytes
        """
        pass

    @abstractmethod
    def persist_version(self, version):
        """
        Place the current firmware version into persistent storage.

        Later to be used to determine the result
        of the firmware update process

        :param version: The current firmware version
        :type version: str

        :returns: result
        :rtype: bool
        """
        pass

    @abstractmethod
    def unpersist_version(self):
        """
        Remove the firmware version from persistent storage.

        :returns: version
        :rtype: str or None
        """
        pass

    @abstractmethod
    def update_start_url_download(self, file_url):
        """
        Prepare the device for the URL file transfer.

        :param file_url: The URL that contains the firmware file
        :type file_url: str

        :returns: result
        :rtype: bool
        """
        pass

    @abstractmethod
    def set_url_download_result_callback(self, callback):
        """
        Set the callback function for reporting the result of URL file download.

        :param callback: function to call
        :type callback: function
        """
        pass
