"""Message storage implemented via double ended queue."""
#   Copyright 2019 WolkAbout Technology s.r.o.
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

from collections import deque
from typing import Optional

from wolk.model.message import Message
from wolk.interface.message_queue import MessageQueue
from wolk import logger_factory


class MessageDeque(MessageQueue):
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
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )

    def put(self, message: Message) -> bool:
        """
        Add the message to the queue.

        Combines sensor reading messages of the same reference
        into a single message.

        :param message: Message to place in the queue
        :type message: Message
        :returns: success
        :rtype: bool
        """
        if not message:
            self.logger.error("Nothing to store!")
            return False

        if "reading" not in message.topic:
            self.queue.append(message)
            self.logger.debug(
                f"Stored message: {message} - Queue size: {len(self.queue)}"
            )
            return True

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
                f"Stored message: {message} - Queue size: {len(self.queue)}"
            )
            return True

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
                        f"Stored message: {message} "
                        f"- Queue size: {len(self.queue)}"
                    )
                    return True

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
                        f"Stored message: {message} "
                        f"- Queue size: {len(self.queue)}"
                    )
                    return True

    def get(self) -> Optional[Message]:
        """
        Take the first message from the queue.

        :returns: message
        :rtype: Optional[Message]
        """
        if len(self.queue) == 0:
            return None
        message = self.queue.popleft()
        self.logger.debug(
            f"Returning message: {message} " f"- Queue size: {len(self.queue)}"
        )
        return message

    def peek(self) -> Optional[Message]:
        """
        Return the first message from the queue without removing it.

        :returns: message
        :rtype: Optional[Message]
        """
        if len(self.queue) == 0:
            self.logger.debug("Empty queue")
            return
        else:
            message = self.queue[0]
            self.logger.debug(
                f"Returning message: {message} "
                f"- Queue size: {len(self.queue)}"
            )
            return message
