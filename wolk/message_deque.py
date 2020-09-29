"""Message storage implemented via double ended queue."""
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
from collections import deque
from typing import Optional

from wolk import logger_factory
from wolk.interface.message_queue import MessageQueue
from wolk.model.message import Message


class MessageDeque(MessageQueue):
    """
    Store messages before they are sent to the WolkAbout IoT Platform.

    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar queue: Double ended queue used to store messages
    :vartype queue: collections.deque
    """

    def __init__(self) -> None:
        """Create a double ended queue to store messages."""
        self.queue: deque = deque()
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )

    def put(self, message: Message) -> bool:
        """
        Add the message to the queue.

        :param message: Message to place in the queue
        :type message: Message
        :returns: success
        :rtype: bool
        """
        if not message:
            self.logger.error("Nothing to store!")
            return False

        self.queue.append(message)
        self.logger.debug(
            f"Stored message: {message} - Queue size: {len(self.queue)}"
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
            return None

        message = self.queue[0]
        self.logger.debug(
            f"Returning message: {message} " f"- Queue size: {len(self.queue)}"
        )
        return message
