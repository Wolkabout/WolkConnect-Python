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

"""
FirmwareCommand Module.
"""


class FirmwareCommand:
    """Firmware update command received from WolkAbout IoT Platform."""

    def __init__(
        self,
        command,
        file_name=None,
        file_size=None,
        file_hash=None,
        auto_install=None,
        file_url=None,
    ):
        """
        Firmware command that was received.

        :param command: Command to be executed
        :type command: wolk.models.FirmwareCommandType.FirmwareCommandType
        :param file_name: Name of the file to be received
        :type file_name: str or None
        :param file_size: Size of the file to be received
        :type file_size: int or None
        :param file_hash: Hash of the file to be received
        :type file_hash: str or None
        :param auto_install: Install the file when it is received
        :type auto_install: bool or None
        :param file_url: URL where the file is located
        :type file_url: str or None
        """
        self.command = command
        self.file_name = file_name
        self.file_size = file_size
        self.file_hash = file_hash
        self.auto_install = auto_install
        self.file_url = file_url
