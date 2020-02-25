"""Tests for OSFirmwareUpdate."""
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
import json
import logging
import os
import sys
import time
import unittest
from unittest.mock import MagicMock

sys.path.append("..")  # noqa

from wolk.os_firmware_update import OSFirmwareUpdate
from wolk.interface.firmware_handler import FirmwareHandler
from wolk.model.firmware_update_error_type import FirmwareUpdateErrorType
from wolk.model.firmware_update_status import FirmwareUpdateStatus
from wolk.model.firmware_update_status_type import FirmwareUpdateStatusType


class TestOSFirmwareUpdate(unittest.TestCase):
    """Tests for OSFirmwareUpdate class."""

    class MockFirmwareHandler(FirmwareHandler):
        """Mock firmware intsaller class that whose methods will be mocked."""

        def install_firmware(self, firmware_file_path: str) -> None:
            """
            Handle the installation of the firmware file.

            :param firmware_file_path: Path where the firmware file is located
            :type firmware_file_path: str
            """
            pass

        def get_current_version(self) -> str:
            """
            Obtain device's current firmware version.

            :returns: version
            :rtpe: str
            """
            pass

    def test_invalid_firmware_handler(self):
        """Test passing an invalid firmware handler."""
        mock_status_callback = MagicMock(return_value=None)

        self.assertRaises(
            ValueError, OSFirmwareUpdate, 1, mock_status_callback
        )

    def test_get_firmware_version(self):
        """Test getting firmware version from firmware handler."""
        mock_status_callback = MagicMock(return_value=None)
        mock_firmware_handler = self.MockFirmwareHandler()
        firmware_version = "1.0"
        mock_firmware_handler.get_current_version = MagicMock(
            return_value=firmware_version
        )

        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )

        self.assertEqual(
            firmware_version, firmware_update.get_current_version()
        )
