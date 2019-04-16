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
OutboundMessage Module.
"""


class OutboundMessage:
    """Outbound Message that gets published to the platform."""

    def __init__(self, channel, payload):
        """
        Data ready to be sent as an MQTT message.

        :param channel: Channel where the message will be published to
        :type channel: str
        :param payload: Payload of message that will be published to channel
        :type payload: str or None
        """
        self.channel = channel
        self.payload = payload
