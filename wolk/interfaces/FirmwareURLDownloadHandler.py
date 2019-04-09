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

"""FirmwareURLDownloadHandler Module."""


class FirmwareURLDownloadHandler(ABC):
    """Responsible for providing means of downloading firmware file from a URL."""

    @abstractmethod
    def download(self, url, file, result_callback):
        """
        Download the resource located at the url to the file.

        Return the result of the download process as a bool to result_callback

        :param url: URL from where to download the file
        :type url: str
        :param file: Name of file to which to download
        :type file: str
        :param result_callback: Function to which to report the outcome
        :type result_callback: function
        """
        pass
