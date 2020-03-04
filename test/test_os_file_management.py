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
import hashlib
import logging
import os
import sys
import unittest
from tempfile import NamedTemporaryFile
from threading import Timer
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
        """Test receiving file package when in idle state."""
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

    def test_file_package_binary_cancel_timeout(self):
        """Test receiving file package cancels request timeout timer."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_management.current_status = True
        file_management.retry_count = 0
        file_management.request_timeout = Timer(60.0, file_management._timeout)
        file_management.request_timeout.cancel = MagicMock()

        file_transfer_package = FileTransferPackage(b"", b"", b"")

        file_management.handle_file_binary_response(file_transfer_package)
        file_management.request_timeout.cancel()
        file_management.packet_request_callback.assert_called()

    # def test_file_package_binary(self):
    #     """Test receiving file package cancels request timeout timer."""
    #     mock_status_callback = MagicMock(return_value=None)
    #     mock_packet_request_callback = MagicMock(return_value=None)
    #     mock_url_status_callback = MagicMock(return_value=None)

    #     file_management = OSFileManagement(
    #         mock_status_callback,
    #         mock_packet_request_callback,
    #         mock_url_status_callback,
    #     )
    #     file_management.logger.setLevel(logging.CRITICAL)
    #     file_management.current_status = True
    #     file_management.retry_count = 0
    #     data = b"Let's try something else"
    #     current_hash = hashlib.sha256(data).digest()

    #     hashlib.sha256 = MagicMock(return_value=b"")

    #     file_transfer_package = FileTransferPackage(
    #         32 * b"\x00", data, current_hash
    #     )

    #     file_management.handle_file_binary_response(file_transfer_package)
    #     file_management.request_timeout.cancel()
    #     file_management.packet_request_callback.assert_called()

    def test_handle_file_url_download_abort(self):
        """Test method resets state."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_management.handle_file_url_download_abort()
        self.assertIsNone(file_management.current_status)

    def test_get_file_list_current_dir(self):
        """Test get file list for running in current directory."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_list = file_management.get_file_list()
        self.assertNotEqual(0, len(file_list))

    def test_get_file_list_empty_dir(self):
        """Test get file list for running in current directory."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        os.mkdir("test_dir")
        file_management.file_directory = "test_dir"
        file_management.logger.setLevel(logging.CRITICAL)
        file_list = file_management.get_file_list()
        self.assertEqual(0, len(file_list))
        os.rmdir("test_dir")

    def test_get_file_path_existing(self):
        """Test get file path for existing file."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_name = "test_file"
        file_handle = open(file_name, "w")
        file_handle.close()
        file_path = file_management.get_file_path(file_name)
        expected_file_path = os.path.join(
            os.path.abspath(os.getcwd()), file_name
        )
        self.assertEqual(expected_file_path, file_path)
        os.remove(file_name)

    def test_get_file_path_non_existing(self):
        """Test get file path for non_existing file."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_name = "test_file"
        file_path = file_management.get_file_path(file_name)
        self.assertIsNone(file_path)

    def handle_file_list_confirm_does_nothing(self):
        """Test file list confirm doesn't call status callbacks."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_management.handle_file_list_confirm()
        file_management.status_callback.assert_not_called()

    def test_handle_file_delete_non_existing(self):
        """Test deleting file that doesn't exist."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_name = "test_file"
        file_management.handle_file_delete(file_name)
        self.assertFalse(os.path.exists(os.path.join(os.getcwd(), file_name)))

    def test_handle_file_delete_existing(self):
        """Test deleting file that exists."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_name = "test_file"
        file_handle = open(file_name, "w")
        file_handle.close()
        file_management.handle_file_delete(file_name)
        self.assertFalse(os.path.exists(os.path.join(os.getcwd(), file_name)))

    def test_handle_file_purge(self):
        """Test deleting all regular files in a directory."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_names = ["file1", "file2", ".special-file"]
        files_directory = "test_dir"
        os.mkdir(files_directory)
        directory_path = os.path.join(os.getcwd(), files_directory)
        for file in file_names:
            file_handle = open(os.path.join(directory_path, file), "w")
            file_handle.close()

        file_management.file_directory = directory_path
        file_management.handle_file_purge()
        self.assertEqual(1, len(os.listdir(directory_path)))
        os.remove(os.path.join(directory_path, ".special-file"))
        os.rmdir(files_directory)

    def test_timeout(self):
        """Test timeout calls abort."""
        mock_status_callback = MagicMock(return_value=None)
        mock_packet_request_callback = MagicMock(return_value=None)
        mock_url_status_callback = MagicMock(return_value=None)

        file_management = OSFileManagement(
            mock_status_callback,
            mock_packet_request_callback,
            mock_url_status_callback,
        )
        file_management.logger.setLevel(logging.CRITICAL)
        file_management.handle_file_upload_abort = MagicMock()

        file_management._timeout()
        file_management.handle_file_upload_abort.assert_called_once()
