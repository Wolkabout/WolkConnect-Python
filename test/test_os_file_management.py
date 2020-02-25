"""Tests for OSFileManagement."""
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
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock

sys.path.append("..")  # noqa

from wolk.os_file_management import OSFileManagement
from wolk.model.file_management_error_type import FileManagementErrorType
from wolk.model.file_management_status import FileManagementStatus
from wolk.model.file_management_status_type import FileManagementStatusType
from wolk.model.file_transfer_package import FileTransferPackage


class TestOSFileManagement(unittest.TestCase):
    """Tests for OSFileManagement class."""

    def test_configure_no_existing_folder(self):
        """Test configuring file management module and create files folder."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )

        preferred_package_size = 1000
        max_file_size = 1000000
        file_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "files"
        )
        file_management.configure(
            preferred_package_size, max_file_size, file_directory
        )
        self.assertTrue(os.path.exists(file_directory))
        os.rmdir(file_directory)

    def test_configure_existing_folder(self):
        """Test configuring file management module with existing folder."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        preferred_package_size = 1000
        max_file_size = 1000000
        file_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "files"
        )
        os.makedirs(os.path.abspath(file_directory))
        file_management.configure(
            preferred_package_size, max_file_size, file_directory
        )
        self.assertTrue(os.path.exists(file_directory))
        os.rmdir(file_directory)

    def test_handle_upload_initiation_not_idle_state(self):
        """Test handle upload initiation when module not idle."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)

        file_name = "file"
        file_size = 1024
        file_hash = "some_hash"
        file_management.current_status = 1  # Not None

        file_management.handle_upload_initiation(
            file_name, file_size, file_hash
        )

        file_management.status_callback.assert_not_called()

    def test_handle_upload_initiation_unconfigured(self):
        """Test handle upload initiation when module not configured."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)

        file_name = "file"
        file_size = 1024
        file_hash = "some_hash"

        file_management.handle_upload_initiation(
            file_name, file_size, file_hash
        )

        expected_status = FileManagementStatus(
            FileManagementStatusType.ERROR,
            FileManagementErrorType.TRANSFER_PROTOCOL_DISABLED,
        )

        file_management.status_callback.assert_called_once_with(
            file_name, expected_status
        )

    def test_handle_upload_initiation_file_too_big(self):
        """Test handle upload initiation when file too big."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        preferred_package_size = 256
        max_file_size = 512
        file_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "files"
        )
        os.makedirs(os.path.abspath(file_directory))
        file_management.configure(
            preferred_package_size, max_file_size, file_directory
        )

        file_name = "file"
        file_size = 1024
        file_hash = "some_hash"

        file_management.handle_upload_initiation(
            file_name, file_size, file_hash
        )

        expected_status = FileManagementStatus(
            FileManagementStatusType.ERROR,
            FileManagementErrorType.UNSUPPORTED_FILE_SIZE,
        )

        file_management.status_callback.assert_called_once_with(
            file_name, expected_status
        )
        os.rmdir(file_directory)

    def test_handle_upload_initiation_valid_file(self):
        """Test handle upload initiation for valid file."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        preferred_package_size = 256
        max_file_size = 1024
        file_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "files"
        )
        os.makedirs(os.path.abspath(file_directory))
        file_management.configure(
            preferred_package_size, max_file_size, file_directory
        )

        file_name = "file"
        file_size = 512
        file_hash = "some_hash"

        file_management.handle_upload_initiation(
            file_name, file_size, file_hash
        )

        expected_status = FileManagementStatus(
            FileManagementStatusType.FILE_TRANSFER
        )

        file_management.status_callback.assert_called_once_with(
            file_name, expected_status
        )
        os.rmdir(file_directory)
        file_management.request_timeout.cancel()
        file_management.temp_file.close()

    def test_handle_upload_initiation_small_file(self):
        """Test handle upload initiation for small file."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        preferred_package_size = 512
        max_file_size = 1024
        file_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "files"
        )
        os.makedirs(os.path.abspath(file_directory))
        file_management.configure(
            preferred_package_size, max_file_size, file_directory
        )

        file_name = "file"
        file_size = 256
        file_hash = "some_hash"

        file_management.handle_upload_initiation(
            file_name, file_size, file_hash
        )

        file_management.packet_request_callback.assert_called_once_with(
            file_name, 0, file_size + 64
        )
        os.rmdir(file_directory)
        file_management.request_timeout.cancel()
        file_management.temp_file.close()

    def test_handle_abort_with_temp_file(self):
        """Test aborting file transfer with temp file set."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_management.temp_file = NamedTemporaryFile(
            mode="a+b", delete=False
        )

        file_management.handle_file_upload_abort()

        self.assertIsNone(file_management.temp_file)

    def test_handle_abort(self):
        """Test aborting file transfer."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)

        file_management.handle_file_upload_abort()

        self.assertIsNone(file_management.temp_file)

    def test_file_package_binary_idle_state(self):
        """Test receveiving file package when in idle state."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_management.logger.warning = MagicMock()

        file_transfer_package = FileTransferPackage(b"", b"", b"")

        file_management.handle_file_binary_response(file_transfer_package)

        file_management.logger.warning.assert_called_once()
