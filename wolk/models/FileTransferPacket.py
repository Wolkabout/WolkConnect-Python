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
FileTransferPacket Module.
"""


class FileTransferPacket:
    """Hold all data contained from a firmware chunk request response."""

    def __init__(self, previous_hash, data, current_hash):
        """
        Chunk of a firmware file.

        :param previous_hash: Hash of the previous chunk
        :type previous_hash: bytes
        :param data: Requested chunk
        :type data: bytes
        :param current_hash: Hash of the current chunk
        :type current_hash: bytes
        """
        self.previous_hash = previous_hash
        self.data = data
        self.current_hash = current_hash
