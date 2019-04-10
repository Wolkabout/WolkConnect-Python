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

from abc import ABC, abstractmethod

"""
ConnectivityService Module.
"""


class ConnectivityService(ABC):
    """Enable communication with WolkAbout IoT Platform."""

    @abstractmethod
    def connect(self):
        """Connect to WolkAbout IoT Platform."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from WolkAbout IoT Platform."""
        pass

    @abstractmethod
    def publish(self, outbound_message):
        """
        Publish a message to WolkAbout IoT Platform.

        Returns true on success, false otherwise.

        :param outbound_message: Message to send
        :type outbound_message: wolk.models.OutboundMessage.OutboundMessage
        :returns: success
        :rtype: bool
        """
        pass

    @abstractmethod
    def set_inbound_message_listener(self, listener):
        """
        Set a callback to ``WolkConnect._on_inbound_message`` method.

        callback function passes back an ``wolk.models.InboundMessage.InboundMessage`` object.

        :param listener: WolkConnect instance
        :type listener: wolk.WolkConnect.WolkConnect
        """
        pass
