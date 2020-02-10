"""Tests for MessageDeque."""
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
import logging
import sys
import unittest

sys.path.append("..")  # noqa

from wolk.message_deque import MessageDeque
from wolk.model.message import Message


class TestMessageDeque(unittest.TestCase):
    """Tests for MessageDeque."""

    default_message = Message("some_topic", "some_payload")

    def test_init(self):
        """Test creating an instance of MessageDeque."""
        message_deque = MessageDeque()
        self.assertIsNotNone(message_deque.queue)

    def test_put_no_message(self):
        """Test passing None to put method."""
        message_deque = MessageDeque()
        message_deque.logger.setLevel(logging.CRITICAL)  # Disable logging
        self.assertFalse(message_deque.put(None))

    def test_put_message(self):
        """Test passing None to put method."""
        message_deque = MessageDeque()
        self.assertTrue(message_deque.put(self.default_message))

    def test_get_message(self):
        """Test getting message from queue."""
        message_deque = MessageDeque()
        message_deque.put(self.default_message)
        self.assertEqual(self.default_message, message_deque.get())

    def test_get_empty(self):
        """Test getting no message from queue."""
        message_deque = MessageDeque()
        self.assertIsNone(message_deque.get())

    def test_peek_empty(self):
        """Test getting no message from queue peek."""
        message_deque = MessageDeque()
        self.assertIsNone(message_deque.peek())

    def test_peek_not_empty(self):
        """Test getting no message from queue peek."""
        message_deque = MessageDeque()
        message_deque.put(self.default_message)
        self.assertIsNotNone(message_deque.peek())
