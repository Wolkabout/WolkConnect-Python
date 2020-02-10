"""Store messages before sending them to WolkAbout IoT Platform."""
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
from abc import ABC
from abc import abstractmethod
from typing import Optional

from wolk.model.message import Message


class MessageQueue(ABC):
    """Store messages on device before publishing to WolkAbout IoT Platform."""

    @abstractmethod
    def put(self, message: Message) -> bool:
        """
        Place a message in storage.

        :param message: Message to be stored
        :type message: Message
        :returns: result
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def get(self) -> Optional[Message]:
        """
        Get a message from storage.

        :returns: message
        :rtype: Optional[Message]
        """
        raise NotImplementedError()

    @abstractmethod
    def peek(self) -> Optional[Message]:
        """
        Get a message without removing from storage.

        :returns: message
        :rtype: Optional[Message]
        """
        raise NotImplementedError()
