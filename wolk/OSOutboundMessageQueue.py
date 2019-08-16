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

"""OSOutboundMessageQueue Module."""

from collections import deque

from wolk.interfaces.OutboundMessageQueue import OutboundMessageQueue
from wolk import LoggerFactory


class OSOutboundMessageQueue(OutboundMessageQueue):
    """
    Store messages before they are sent to the WolkAbout IoT Platform.

    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar queue: Double ended queue used to store messages
    :vartype queue: collections.deque
    """

    def __init__(self):
        """Create a double ended queue to store messages."""
        self.queue = deque()
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug("Init")

    def put(self, message):
        """
        Add the message to the queue.

        Combines sensor reading messages of the same reference
        into a single message.

        :param message: Message to place in the queue
        :type message: wolk.models.OutboundMessage.OutboundMessage
        """
        if not message:
            return

        if "reading" not in message.topic:
            self.queue.append(message)
            self.logger.debug(
                "put - Queue size: %s ; Topic: %s ; Payload: %s",
                len(self.queue),
                message.topic,
                message.payload,
            )
            return

        reading_reference = message.topic.split("/")[-1]

        present_in_queue = False

        for stored_message in self.queue:
            if "reading" not in message.topic:
                continue
            if reading_reference == stored_message.topic.split("/")[-1]:
                present_in_queue = True
                break

        if not present_in_queue:
            self.queue.append(message)
            self.logger.debug(
                "put - Queue size: %s ; Topic: %s ; Payload: %s",
                len(self.queue),
                message.topic,
                message.payload,
            )
            return

        readings = 0
        max_data = 1

        for stored_message in self.queue:
            if "reading" not in stored_message.topic:
                continue
            if reading_reference == stored_message.topic.split("/")[-1]:
                readings += 1
                data_count = stored_message.payload.count('"data"')
                if data_count > max_data:
                    max_data = data_count

        if readings > 0 and max_data == 1:
            for stored_message in self.queue:
                if reading_reference == stored_message.topic.split("/")[-1]:
                    stored_message.payload = "[" + stored_message.payload
                    stored_message.payload += "," + message.payload + "]"
                    self.logger.debug(
                        "put - Queue size: %s ; Topic: %s ; Payload: %s",
                        len(self.queue),
                        message.topic,
                        message.payload,
                    )
                    break

        if max_data > 1:
            for stored_message in self.queue:
                if "reading" not in stored_message.topic:
                    continue
                if reading_reference == stored_message.topic.split("/")[-1]:
                    data_count = stored_message.payload.count('"data"')
                    if max_data > data_count:
                        continue

                    stored_message.payload = stored_message.payload[:-1]
                    stored_message.payload += "," + message.payload + "]"
                    self.logger.debug(
                        "put - Queue size: %s ; Topic: %s ; Payload: %s",
                        len(self.queue),
                        message.topic,
                        message.payload,
                    )

    def get(self):
        """
        Take the first message from the queue.

        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage or None
        """
        if len(self.queue) == 0:
            return None

        message = self.queue.popleft()
        self.logger.debug(
            "get - Queue size: %s ; Topic: %s ; Payload: %s",
            len(self.queue),
            message.topic,
            message.payload,
        )
        return message

    def peek(self):
        """
        Return the first message from the queue without removing it.

        :returns: message
        :rtype: wolk.models.OutboundMessage.OutboundMessage or None
        """
        if len(self.queue) == 0:

            self.logger.debug("peek - Queue size: %s", len(self.queue))
            return

        else:
            message = self.queue[0]
            self.logger.debug(
                "peek - Queue size: %s ; Topic: %s ; Payload: %s",
                len(self.queue),
                message.topic,
                message.payload,
            )
            return message
