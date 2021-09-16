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
import logging
import os
import sys
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
        """Mock firmware installer class that whose methods will be mocked."""

        def install_firmware(self, firmware_file_path: str) -> None:
            """
            Handle the installation of the firmware file.

            :param firmware_file_path: Path where the firmware file is located
            :type firmware_file_path: str
            """
            raise NotImplementedError()

        def get_current_version(self) -> str:
            """
            Obtain device's current firmware version.

            :returns: version
            :rtype: str
            """
            raise NotImplementedError()

    def test_invalid_firmware_handler(self):
        """Test passing an invalid firmware handler."""
        mock_status_callback = MagicMock()

        self.assertRaises(
            ValueError, OSFirmwareUpdate, 1, mock_status_callback
        )

    def test_get_firmware_version(self):
        """Test getting firmware version from firmware handler."""
        mock_status_callback = MagicMock()
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

    def test_handle_install_not_idle(self):
        """Test receiving install command when module not idle."""
        mock_status_callback = MagicMock()
        mock_firmware_handler = self.MockFirmwareHandler()

        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )
        firmware_update.logger.setLevel(logging.CRITICAL)
        firmware_update.logger.warning = MagicMock()

        firmware_update.current_status = 1  # Not None

        firmware_update.handle_install("some_file")

        firmware_update.logger.warning.assert_called_once()

    def test_handle_install_existing_version_file(self):
        """Test receiving install command when version file exists."""
        mock_status_callback = MagicMock()
        mock_firmware_handler = self.MockFirmwareHandler()

        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )
        firmware_update.logger.setLevel(logging.CRITICAL)

        file_handle = open("last_firmware_version.txt", "w")
        expected_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.ERROR,
            FirmwareUpdateErrorType.UNKNOWN,
        )

        firmware_update.handle_install("some_file")

        firmware_update.status_callback.assert_called_once_with(
            expected_status
        )

        file_handle.close()
        os.remove("last_firmware_version.txt")

    def test_handle_install_file_not_present(self):
        """Test receiving install command when file does not exist."""
        mock_status_callback = MagicMock()
        mock_firmware_handler = self.MockFirmwareHandler()
        firmware_version = "1.0"
        mock_firmware_handler.get_current_version = MagicMock(
            return_value=firmware_version
        )

        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )
        firmware_update.logger.setLevel(logging.CRITICAL)

        expected_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.ERROR,
            FirmwareUpdateErrorType.UNKNOWN_FILE,
        )

        firmware_update.handle_install("some_file")

        firmware_update.status_callback.assert_called_once_with(
            expected_status
        )

    def test_handle_install_file_present(self):
        """Test receiving install command and file exists on device."""
        mock_status_callback = MagicMock()
        mock_firmware_handler = self.MockFirmwareHandler()
        mock_firmware_handler.get_current_version = MagicMock(
            return_value="1.0"
        )
        mock_firmware_handler.install_firmware = MagicMock()

        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )
        firmware_update.logger.setLevel(logging.CRITICAL)
        expected_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.INSTALLING
        )

        file_handle = open("test_file", "w")
        firmware_update.handle_install("test_file")

        firmware_update.status_callback.assert_called_once_with(
            expected_status
        )
        file_handle.close()
        os.remove("test_file")
        os.remove("last_firmware_version.txt")

    def test_handle_abort_when_not_idle(self):
        """Test receiving the abort command when module not idle."""
        mock_status_callback = MagicMock()
        mock_firmware_handler = self.MockFirmwareHandler()
        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )
        firmware_update.logger.setLevel(logging.CRITICAL)
        expected_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.ABORTED
        )
        firmware_update.current_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.INSTALLING
        )
        firmware_update.handle_abort()

        firmware_update.status_callback.assert_called_once_with(
            expected_status
        )

    def test_handle_abort_when_not_idle_and_version_file(self):
        """Test the abort command when not idle and version file exists."""
        mock_status_callback = MagicMock()
        mock_firmware_handler = self.MockFirmwareHandler()
        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )
        firmware_update.logger.setLevel(logging.CRITICAL)
        firmware_update.current_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.INSTALLING
        )
        file_handle = open("last_firmware_version.txt", "w")
        file_handle.close()
        firmware_update.handle_abort()

        self.assertFalse(os.path.exists("last_firmware_version.txt"))

    def test_report_result_no_stored_file(self):
        """Test reporting result with no stored firmware version."""
        mock_status_callback = MagicMock()
        mock_firmware_handler = self.MockFirmwareHandler()
        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )
        firmware_update.logger.setLevel(logging.CRITICAL)

        firmware_update.logger.debug = MagicMock()

        firmware_update.report_result()

        self.assertEqual(2, firmware_update.logger.debug.call_count)

    def test_report_result_unchanged_version(self):
        """Test reporting result with unchanged version."""
        mock_status_callback = MagicMock()
        mock_firmware_handler = self.MockFirmwareHandler()
        firmware_version = "1.0"
        mock_firmware_handler.get_current_version = MagicMock(
            return_value=firmware_version
        )
        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )
        firmware_update.logger.setLevel(logging.CRITICAL)
        with open("last_firmware_version.txt", "w") as file:
            file.write(firmware_update.firmware_handler.get_current_version())

        expected_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.ERROR,
            FirmwareUpdateErrorType.INSTALLATION_FAILED,
        )

        firmware_update.report_result()

        firmware_update.status_callback.assert_called_once_with(
            expected_status
        )

    def test_report_result_changed_version(self):
        """Test reporting result with changed version."""
        mock_status_callback = MagicMock()
        mock_firmware_handler = self.MockFirmwareHandler()
        firmware_version = "1.0"
        mock_firmware_handler.get_current_version = MagicMock(
            return_value=firmware_version
        )
        firmware_update = OSFirmwareUpdate(
            mock_firmware_handler, mock_status_callback
        )
        firmware_update.logger.setLevel(logging.CRITICAL)
        with open("last_firmware_version.txt", "w") as file:
            file.write(firmware_update.firmware_handler.get_current_version())

        firmware_version = "2.0"
        mock_firmware_handler.get_current_version = MagicMock(
            return_value=firmware_version
        )
        expected_status = FirmwareUpdateStatus(
            FirmwareUpdateStatusType.SUCCESS
        )

        firmware_update.report_result()

        firmware_update.status_callback.assert_called_once_with(
            expected_status
        )
