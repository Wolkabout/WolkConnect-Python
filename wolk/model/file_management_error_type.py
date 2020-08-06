"""Enumeration of defined file management errors."""
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
from enum import Enum


class FileManagementErrorType(Enum):
    """Enumeration of available file management errors."""

    UNSPECIFIED_ERROR = 0
    TRANSFER_PROTOCOL_DISABLED = 1
    UNSUPPORTED_FILE_SIZE = 2
    MALFORMED_URL = 3
    FILE_HASH_MISMATCH = 4
    FILE_SYSTEM_ERROR = 5
    RETRY_COUNT_EXCEEDED = 10
