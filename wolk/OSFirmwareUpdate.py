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

"""OSFirmwareUpdate Module."""

import base64
import hashlib
import math
from threading import Timer

from wolk.models.FirmwareErrorType import FirmwareErrorType
from wolk.models.FirmwareStatus import FirmwareStatus
from wolk.models.FirmwareStatusType import FirmwareStatusType
from wolk.models.FirmwareUpdateStateType import FirmwareUpdateStateType
from wolk.interfaces.FirmwareUpdate import FirmwareUpdate
from wolk import LoggerFactory


class OSFirmwareUpdate(FirmwareUpdate):
    """
    Responsible for everything related to the firmware update process.

    :ivar auto_install: install upon receiving the firmware file
    :vartype auto_install: bool
    :ivar expected_number_of_chunks: expected number of firmware chunks
    :vartype expected_number_of_chunks: int
    :ivar file_hash: hash of firmware file received from the platform
    :vartype file_hash: str
    :ivar file_name: firmware file name
    :vartype file_name: str
    :ivar file_size: firmware file size
    :vartype file_size: int
    :ivar firmware_handler: implementation of FirmwareHandler interface
    :vartype firmware_handler: wolk.interfaces.FirmwareHandler.FirmwareHandler
    :ivar install_timer: timer for install countdown
    :vartype install_timer: threading.Timer
    :ivar last_packet_hash: hash of last valid packet received
    :vartype last_packet_hash: str
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar max_retries: number of retries for a firmware packet
    :vartype max_retries: int
    :ivar minimum_packet_size: minimal size of a firmware chunk
    :vartype minimum_packet_size: int
    :ivar next_chunk_index: index of next firmware chunk
    :vartype next_chunk_index: int
    :ivar on_file_packet_request_callback: callback for chunk request
    :vartype on_file_packet_request_callback: function
    :ivar on_status_callback: callback for reporting firmware update status
    :vartype on_status_callback: function
    :ivar request_timeout: countdown timer for request timeout
    :vartype request_timeout: threading.Timer
    :ivar retry_count: current retry count
    :vartype retry_count: int
    :ivar state: current firmware installation state
    :vartype state: wolk.models.FirmwareUpdateStateType.FirmwareUpdateStateType
    """

    def __init__(self, firmware_handler=None):
        """
        Responsible for firmware update flow.

        :param firmware_handler: Responsible for the firmware file itself
        :type firmware_handler: wolk.interfaces.FirmwareHandler.FirmwareHandler or None
        """
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug("Init - firmware_handler: %s", firmware_handler)
        self.firmware_handler = firmware_handler
        self.state = FirmwareUpdateStateType.IDLE
        self.max_retries = 3
        self.minimum_packet_size = 65
        self.on_status_callback = None
        self.on_file_packet_request_callback = None
        self.file_name = None
        self.file_size = None
        self.file_hash = None
        self.auto_install = None
        self.next_chunk_index = None
        self.expected_number_of_chunks = None
        self.retry_count = None
        self.request_timeout = None
        self.install_timer = None
        self.last_packet_hash = 32 * b"\x00"

        if self.firmware_handler:

            self.firmware_handler.set_url_download_result_callback(
                self.handle_url_download_result
            )

    def set_on_file_packet_request_callback(self, on_file_packet_request_callback):
        """
        Set the callback function for requesting file packets.

        :param on_file_packet_request_callback: Function to be called
        :type on_file_packet_request_callback: function
        """
        self.logger.debug(
            "set_on_file_packet_request_callback called - "
            "on_file_packet_request_callback = %s",
            on_file_packet_request_callback,
        )
        self.on_file_packet_request_callback = on_file_packet_request_callback

    def set_on_status_callback(self, on_status_callback):
        """
        Set the callback function for reporting firmware status.

        :param on_status_callback: Function to be called
        :type on_status_callback: function
        """
        self.logger.debug(
            "set_on_status_callback called - " "on_status_callback = %s",
            on_status_callback,
        )
        self.on_status_callback = on_status_callback

    def handle_url_download_result(self, result):
        """
        Receive the result of URL download from the firmware handler.

        :param result: Result of the URL download
        :type result: bool
        """
        self.logger.debug("handle_url_download_result called - Result: %s", result)
        if not self.firmware_handler:

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
            )
            self.logger.debug(
                "handle_url_download_result - No firmware_handler, "
                "reporting DFU disabled"
            )
            self.on_status_callback(status)
            return

        if result:

            self.state = FirmwareUpdateStateType.FILE_OBTAINED
            status = FirmwareStatus(FirmwareStatusType.FILE_READY)
            self.logger.debug(
                "handle_url_download_result - result valid, " "reporting file ready"
            )
            self.on_status_callback(status)

            if self.auto_install:

                self.logger.debug(
                    "handle_url_download_result - auto_install is true, "
                    "handling install"
                )
                self.handle_install()

        else:

            self.logger.debug(
                "handle_url_download_result - result invalid, " "abort and report error"
            )
            self.firmware_handler.update_abort()
            self.reset_state()
            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.UNSPECIFIED_ERROR
            )
            self.on_status_callback(status)

    def handle_file_upload(self, firmware_command):
        """
        Handle the file upload command received from the platform.

        :param firmware_command: Firmware command received
        :type firmware_command: wolk.models.FirmwareCommand.FirmwareCommand
        """
        self.logger.info(
            "Received firmware command - Command: FILE_UPLOAD ; "
            "File name: %s ; File size: %s ; "
            "File hash: %s ; Auto install: %s",
            firmware_command.file_name,
            firmware_command.file_size,
            firmware_command.file_hash,
            firmware_command.auto_install,
        )
        if not self.firmware_handler:

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
            )
            self.logger.error("No firmware_handler, reporting DFU disabled")
            self.on_status_callback(status)
            return

        if self.state != FirmwareUpdateStateType.IDLE:

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.UNSPECIFIED_ERROR
            )
            self.logger.error("State not idle, reporting unspecified error")
            self.state = FirmwareUpdateStateType.IDLE
            self.on_status_callback(status)
            return

        if (
            self.firmware_handler.max_file_size == 0
            or self.firmware_handler.chunk_size == 0
        ):

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
            )
            self.logger.error("firmware_handler not configured, reporting DFU disabled")
            self.on_status_callback(status)
            return

        if self.firmware_handler.max_file_size < firmware_command.file_size:

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.UNSUPPORTED_FILE_SIZE
            )
            self.logger.error("File size not supported, reporting size error")
            self.on_status_callback(status)
            return

        if not self.firmware_handler.update_start(
            firmware_command.file_name, firmware_command.file_size
        ):

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.UNSPECIFIED_ERROR
            )
            self.logger.error(
                "Failed to create temporary file, reporting unspecified error"
            )
            self.on_status_callback(status)
            return

        self.file_name = firmware_command.file_name
        self.file_size = firmware_command.file_size
        self.file_hash = firmware_command.file_hash
        self.auto_install = firmware_command.auto_install
        self.expected_number_of_chunks = math.ceil(
            self.file_size / self.firmware_handler.chunk_size
        )
        self.next_chunk_index = 0
        self.retry_count = 0
        self.state = FirmwareUpdateStateType.FILE_TRANSFER

        status = FirmwareStatus(FirmwareStatusType.FILE_TRANSFER)
        self.logger.info("Initializing file transfer and requesting first chunk...")
        self.on_status_callback(status)

        if firmware_command.file_size < self.firmware_handler.chunk_size:
            self.on_file_packet_request_callback(
                self.file_name, self.next_chunk_index, firmware_command.file_size + 64
            )
        else:
            self.on_file_packet_request_callback(
                self.file_name, self.next_chunk_index, self.firmware_handler.chunk_size + 64
            )

        self.request_timeout = Timer(60.0, self.handle_abort)
        self.request_timeout.start()

    def handle_url_download(self, firmware_command):
        """
        Handle the URL download command received from the platform.

        :param firmware_command: Firmware command received
        :type firmware_command: wolk.models.FirmwareCommand.FirmwareCommand
        """
        self.logger.info(
            "Received URL download command; File URL: %s ; Auto install:%s",
            firmware_command.file_url,
            firmware_command.auto_install,
        )
        if not self.firmware_handler:

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
            )
            self.logger.error("No firmware_handler, reporting DFU disabled")
            self.on_status_callback(status)
            return

        if self.state != FirmwareUpdateStateType.IDLE:

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.UNSPECIFIED_ERROR
            )
            self.logger.error("State not idle, reporting unspecified error")
            self.state = FirmwareUpdateStateType.IDLE
            self.on_status_callback(status)
            return

        if not self.firmware_handler.update_start_url_download(
            firmware_command.file_url
        ):

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.MALFORMED_URL
            )
            self.logger.error("Malformed URL!")
            self.on_status_callback(status)
            return

        self.auto_install = firmware_command.auto_install
        self.state = FirmwareUpdateStateType.URL_DOWNLOAD
        status = FirmwareStatus(FirmwareStatusType.FILE_TRANSFER)
        self.logger.info("Initializing URL file transfer...")
        self.on_status_callback(status)

    def handle_install(self):
        """Handle the install command received from the platform."""
        self.logger.debug("handle_install called")
        if not self.firmware_handler:

            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
            )
            self.logger.error("No firmware_handler, reporting DFU disabled")
            self.on_status_callback(status)
            return

        if self.state == FirmwareUpdateStateType.FILE_OBTAINED:

            if not self.firmware_handler.persist_version(self.firmware_handler.version):

                self.logger.error(
                    "Unable to persist version, " "aborting firmware update process"
                )
                self.firmware_handler.update_abort()
                self.reset_state()
                status = FirmwareStatus(
                    FirmwareStatusType.ERROR, FirmwareErrorType.INSTALLATION_FAILED
                )
                self.on_status_callback(status)
                return

            self.state = FirmwareUpdateStateType.INSTALL
            status = FirmwareStatus(FirmwareStatusType.INSTALLATION)
            self.logger.info("Beginning firmware installation process")
            self.on_status_callback(status)

            self.install_timer = Timer(
                5.0, self.firmware_handler.update_finalize
            )  # For possible abort command
            self.install_timer.start()

        elif self.state == FirmwareUpdateStateType.INSTALL:

            self.logger.debug(
                "handle_install - Ignore install command, "
                "installation already started"
            )

        else:  # Returns an error in all other states

            self.logger.error("Invalid flow, aborting and reporting unspecified error")
            self.firmware_handler.update_abort()
            self.reset_state()
            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.UNSPECIFIED_ERROR
            )
            self.on_status_callback(status)

    def handle_abort(self):
        """Handle the abort command received from the platform."""
        self.logger.debug("handle_abort called")
        if self.install_timer:

            self.logger.debug("handle_abort - Stopping installation timer")
            self.install_timer.cancel()

        if not self.firmware_handler:

            self.logger.debug(
                "handle_abort - No firmware_handler, reporting DFU disabled"
            )
            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
            )
            self.on_status_callback(status)
            return

        if self.state != FirmwareUpdateStateType.IDLE:

            self.logger.info("Received abort command from platform")
            self.firmware_handler.update_abort()
            self.reset_state()
            status = FirmwareStatus(FirmwareStatusType.ABORTED)
            self.on_status_callback(status)

        else:

            self.logger.error("Invalid flow, reporting unspecified error")
            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.UNSPECIFIED_ERROR
            )
            self.on_status_callback(status)

    def handle_packet(self, packet):
        """
        Handle the firmware file chunk packet received from the platform.

        :param packet: Firmware file chunk received
        :type packet: wolk.models.FileTransferPacket.FileTransferPacket
        """
        self.logger.debug(
            "handle_packet called - Previous hash: %s ; "
            "Data size: %s ; Current hash: %s",
            packet.previous_hash,
            len(packet.data),
            packet.current_hash,
        )
        if self.state != FirmwareUpdateStateType.FILE_TRANSFER:

            self.logger.debug(
                "handle_packet - State not file transfer, ignoring packet"
            )
            return

        if self.request_timeout:
            self.logger.debug("handle_packet - Canceling request timeout timer")
            self.request_timeout.cancel()

        if not self.firmware_handler:

            self.logger.error("No firmware_handler, reporting DFU disabled")
            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
            )
            self.on_status_callback(status)
            return

        if not self.validate_packet(packet):

            self.logger.debug("handle_packet - Packet not valid")
            self.retry_count += 1

            if self.retry_count >= self.max_retries:

                self.logger.error(
                    "Retry count exceeded, aborting firmware update process"
                )
                self.firmware_handler.update_abort()
                self.reset_state()
                status = FirmwareStatus(
                    FirmwareStatusType.ERROR, FirmwareErrorType.RETRY_COUNT_EXCEEDED
                )
                self.on_status_callback(status)
                return

            else:

                self.logger.info("Requesting chunk #%s again", self.next_chunk_index)
                self.on_file_packet_request_callback(
                    self.file_name,
                    self.next_chunk_index,
                    self.firmware_handler.chunk_size + 64,
                )

                self.request_timeout = Timer(60.0, self.handle_abort)
                self.request_timeout.start()
                return

        if self.last_packet_hash != packet.previous_hash:

            self.logger.error("Received chunk out of order!")
            self.retry_count += 1

            if self.retry_count >= self.max_retries:

                self.logger.error(
                    "Retry count exceeded, aborting firmware update process"
                )
                self.firmware_handler.update_abort()
                self.reset_state()
                status = FirmwareStatus(
                    FirmwareStatusType.ERROR, FirmwareErrorType.RETRY_COUNT_EXCEEDED
                )
                self.on_status_callback(status)
                return

            else:

                self.logger.info("Requesting chunk #%s again", self.next_chunk_index)
                self.on_file_packet_request_callback(
                    self.file_name,
                    self.next_chunk_index,
                    self.firmware_handler.chunk_size + 64,
                )

                self.request_timeout = Timer(60.0, self.handle_abort)
                self.request_timeout.start()
                return

        self.last_packet_hash = packet.current_hash

        if not self.firmware_handler.write_chunk(packet.data):

            self.logger.error(
                "Failed to write chunk, aborting firmware update process!"
            )
            self.firmware_handler.update_abort()
            self.reset_state()
            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_SYSTEM_ERROR
            )
            self.on_status_callback(status)
            return

        self.next_chunk_index += 1

        if self.next_chunk_index < self.expected_number_of_chunks:

            self.logger.debug(
                "handle_packet - Wrote chunk successfully, " "requesting next chunk"
            )
            self.on_file_packet_request_callback(
                self.file_name,
                self.next_chunk_index,
                self.firmware_handler.chunk_size + 64,
            )

            self.request_timeout = Timer(60.0, self.handle_abort)
            self.request_timeout.start()
            return

        if not self.validate_firmware_file():

            self.logger.error(
                "Firmware file not valid, aborting firmware update process!"
            )
            self.firmware_handler.update_abort()
            self.reset_state()
            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_SYSTEM_ERROR
            )
            self.on_status_callback(status)
            return

        self.state = FirmwareUpdateStateType.FILE_OBTAINED
        self.request_timeout.cancel()
        self.request_timeout = None
        self.logger.info("Firmware file validated, ready for installation")
        status = FirmwareStatus(FirmwareStatusType.FILE_READY)
        self.on_status_callback(status)

        if self.auto_install:

            self.logger.info("Auto install is enabled, beginning installation..")
            self.handle_install()

    def report_result(self):
        """Report the result of the firmware installation process."""
        self.logger.debug("report_result called")
        if self.firmware_handler is not None:

            persisted_version = self.firmware_handler.unpersist_version()
            if not persisted_version:
                self.logger.debug("report_result - No persisted version")
                return

            if persisted_version == self.firmware_handler.version:

                self.logger.info(
                    "Firmware version unchanged, reporting installation failed"
                )
                status = FirmwareStatus(
                    FirmwareStatusType.ERROR, FirmwareErrorType.INSTALLATION_FAILED
                )
                self.on_status_callback(status)
                return

            self.logger.info(
                "Firmware version changed, reporting installation completed"
            )
            status = FirmwareStatus(FirmwareStatusType.COMPLETED)
            self.on_status_callback(status)

    def reset_state(self):
        """Reset the state of the firmware update handler."""
        self.logger.debug("reset_state called")
        self.state = FirmwareUpdateStateType.IDLE
        self.file_name = None
        self.file_size = None
        self.file_hash = None
        self.auto_install = None
        self.next_chunk_index = None
        self.expected_number_of_chunks = None
        self.retry_count = None
        self.request_timeout = None
        self.install_timer = None
        self.last_packet_hash = 32 * b"\x00"

    def validate_packet(self, packet):
        """
        Validate received firmware file packet.

        Checks if the packed is bigger than the minimum packet size
        and checks if the sha256 hash of the data matches the hash
        received from the platform

        :param packet: Packet to validate
        :type packet: wolk.models.FileTransferPacket.FileTransferPacket

        :returns: valid
        :rtype: bool
        """
        self.logger.debug("validate_packet called")
        if (
            len(packet.previous_hash) + len(packet.data) + len(packet.current_hash)
            < self.minimum_packet_size
        ):

            self.logger.error("Received packet size too small!")
            return False

        else:

            data_hash = hashlib.sha256(packet.data).digest()

            if packet.current_hash != data_hash:

                self.logger.error(
                    "Data hash '%s' doesn't match expected hash '%s'!",
                    data_hash,
                    packet.current_hash,
                )
                return False

            else:

                self.logger.debug(
                    "validate_packet - Data hash matches current_hash,"
                    " returning True"
                )
                return True

    def validate_firmware_file(self):
        """
        Validate the completed firmware file.

        Compares the sha256 hash of the received file with the file hash
        received from the platform.

        :returns: valid
        :rtype: bool
        """
        self.logger.debug("validate_firmware_file called")
        if not self.firmware_handler:

            self.logger.error("No firmware_handler, reporting DFU disabled")
            status = FirmwareStatus(
                FirmwareStatusType.ERROR, FirmwareErrorType.FILE_UPLOAD_DISABLED
            )
            self.on_status_callback(status)
            return

        sha256_command_file_hash = base64.b64decode(
            self.file_hash + ("=" * (-len(self.file_hash) % 4))
        )
        sha256_file_hash = hashlib.sha256()

        for x in range(0, self.expected_number_of_chunks):

            chunk = self.firmware_handler.read_chunk(x)
            if not chunk:
                self.logger.error("File size too small!")
                return False

            sha256_file_hash.update(chunk)

        sha256_file_hash = sha256_file_hash.digest()

        valid = sha256_command_file_hash == sha256_file_hash
        self.logger.debug("validate_firmware_file - returning valid: %s", valid)
        return valid
