"""LoggerFactory Module."""
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
from typing import List
from typing import Optional


class LoggerFactory:
    """Factory for issuing ready to use loggers in other modules."""

    def __init__(self, level=logging.INFO, console=True, log_file=None):  # type: ignore
        """
        Create a factory that will give loggers through calls to get_logger().

        :param level: Set the desired logging level
        :type level: int or None
        :param console: Should the log messages be outputted to the console
        :type console: bool or None
        :param log_file: Name of the log file to output to
        :type log_file: str or None
        """
        self.level = level
        self.device_key = None
        self.console = console
        self.log_file = log_file
        self.loggers: List[logging.Logger] = []

    def set_device_key(self, device_key: str) -> None:
        """
        Set device key.

        :param device_key: Device key
        :type device_key: str
        """
        self.device_key = device_key

    def get_logger(
        self, name: str, level: Optional[int] = None
    ) -> logging.Logger:
        """
        Return a ready to use logger instance.

        :param name: Name of the logger
        :type name: str
        :param level: Override the log level
        :type level: int or None

        :returns: Logger instance
        :rtype: logger
        """
        logger = logging.getLogger(name)

        if level is not None:
            logger.setLevel(level)
        else:
            logger.setLevel(self.level)

        if self.device_key is not None:
            formatter = logging.Formatter(
                "%(asctime)s - '"
                + str(self.device_key)
                + "' - %(levelname)s [%(filename)s:%(lineno)s"
                + " - %(funcName)s()] - %(message)s"
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s [%(filename)s:%(lineno)s"
                + " - %(funcName)s()] - %(message)s"
            )
        if self.console:

            console_handler = logging.StreamHandler()
            if level is not None:
                console_handler.setLevel(level)
            else:
                console_handler.setLevel(self.level)

            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        if self.log_file is not None:
            file_handler = logging.FileHandler(self.log_file)
            if level is not None:
                file_handler.setLevel(level)
            else:
                file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        self.loggers.append(logger)
        return logger


# Logging levels available: NOTSET, INFO, DEBUG
logger_factory = LoggerFactory(level=logging.INFO)

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "notset": logging.NOTSET,
}


def logging_config(level: str, log_file: Optional[str] = None) -> None:
    """
    Set desired log level and designate a log file.

    :param level: Available levels : debug, info, notset
    :type level: str
    :param log_file: path to log file
    :type log_file: str or None
    """
    if log_file is not None:
        logger_factory.log_file = log_file

    if level not in LEVELS:
        print(f"Invalid level '{level}'")
        return

    if LEVELS[level] == logger_factory.level:
        return

    logger_factory.level = LEVELS[level]

    for logger in logger_factory.loggers:
        logger.setLevel(logger_factory.level)
        for handler in logger.handlers:
            handler.setLevel(logger_factory.level)
