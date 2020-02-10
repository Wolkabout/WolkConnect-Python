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
            "name", logging.CRITICAL
        )
        self.assertEqual(logging.CRITICAL, logger.level)

    def test_logging_config_logger_with_log_file(self):
        """Test getting logger with log file."""
        test_log = "test.log"
        logger_factory.logging_config("info", test_log)
        logger = logger_factory.logger_factory.get_logger(
            "test", logging.CRITICAL
        )
        self.assertIsInstance(logger.handlers[1], logging.FileHandler)

    def test_logging_config_debug(self):
        """Test setting log level to debug."""
        logger_factory.logging_config("debug")
        self.assertEqual(logging.DEBUG, logger_factory.logger_factory.level)

    def test_logging_config_info(self):
        """Test setting log level to info."""
        logger_factory.logging_config("info")
        self.assertEqual(logging.INFO, logger_factory.logger_factory.level)

    def test_logging_config_notset(self):
        """Test setting log level to notset."""
        logger_factory.logging_config("notset")
        self.assertEqual(logging.NOTSET, logger_factory.logger_factory.level)

    def test_logging_config_log_file(self):
        """Test setting log level to notset."""
        test_log = "test.log"
        logger_factory.logging_config("info", test_log)
        self.assertEqual(test_log, logger_factory.logger_factory.log_file)

    def test_only_file_logger(self):
        """Test creating a logger that will only log to file."""
        test_log = "test.log"
        logger_file_factory = logger_factory.LoggerFactory(
            console=False, log_file=test_log
        )
        other_logger = logger_file_factory.get_logger("test")
        self.assertIsInstance(other_logger.handlers[1], logging.FileHandler)
