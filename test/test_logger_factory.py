"""Tests for LoggerFactory."""
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

from wolk import logger_factory


class TestLoggerFactory(unittest.TestCase):
    """Tests for LoggerFactory class."""

    def test_get_logger_with_level(self):
        """Test getting defualt logger with specified level."""
        logger = logger_factory.logger_factory.get_logger(
            "name", logging.NOTSET
        )
        self.assertEqual(logging.NOTSET, logger.level)

    def test_logging_config_logger_with_log_file(self):
        """Test getting logger with log file."""
        test_log = "test.log"
        logger_factory.logging_config("info", test_log)
        logger = logger_factory.logger_factory.get_logger(
            "test", logging.NOTSET
        )
        self.assertIsInstance(logger.handlers[1], logging.FileHandler)

        logger.handlers[1].close()
        logger.removeHandler(logger.handlers[1])
        logger_factory.logger_factory.log_file = None
        import os

        os.remove(test_log)

    def test_logging_config_logger_only_log_file(self):
        """Test getting logger only with log file."""
        test_log = "test.log"
        logger_factory.logging_config("info", test_log)
        logger_factory.logger_factory.console = False
        logger = logger_factory.logger_factory.get_logger("test")
        self.assertIsInstance(logger.handlers[0], logging.FileHandler)

        logger_factory.logger_factory.console = True
        logger.handlers[0].close()
        logger.removeHandler(logger.handlers[0])
        logger_factory.logger_factory.log_file = None
        import os

        os.remove(test_log)

    def test_logging_config_debug(self):
        """Test setting log level to debug."""
        logger_factory.logging_config("debug")
        self.assertEqual(logging.DEBUG, logger_factory.logger_factory.level)

    def test_logging_config_info_then_invalid(self):
        """Test setting log level to info and then to invalid value."""
        logger_factory.logging_config("info")
        logger_factory.logging_config("tests")
        self.assertEqual(logging.INFO, logger_factory.logger_factory.level)
