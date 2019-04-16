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
InboundMessage Module.
"""


class InboundMessage:
    """Inbound Messages that get received from the platform."""

    def __init__(self, channel, payload):
        """
        Inbound MQTT message.

        :param channel: Channel where the message was published to
        :type channel: str
        :param payload: Payload of the message that was published to channel
        :type payload: str or bytes
        """
        self.channel = channel
        self.payload = payload
