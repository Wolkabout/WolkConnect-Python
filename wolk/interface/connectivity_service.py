"""Service for exchanging data with WolkAbout IoT Platform."""
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
from typing import Callable

from wolk.model.message import Message


class ConnectivityService(ABC):
    """Responsible for exchanging data with WolkAbout IoT Platform."""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to WolkAbout IoT Platform."""
        raise NotImplementedError()

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from WolkAbout IoT Platform."""
        raise NotImplementedError()

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Return current connection state.

        :returns: connected
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def publish(self, message: Message) -> bool:
        """
        Publish a message to WolkAbout IoT Platform.

        :param outbound_message: Message to send
        :type outbound_message: Message
        :returns: success
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def set_inbound_message_listener(
        self, listener: Callable[[Message], None]
    ) -> None:
        """
        Set a callback method to handle inbound messages.

        :param listener: Method hat handles inbound messages
        :type listener: Callable[[Message], None]
        """
        raise NotImplementedError()
