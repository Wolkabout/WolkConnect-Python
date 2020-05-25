"""Stub function for setting new configuration values."""
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
from typing import Dict
from typing import Union


def handle_configuration(
    configuration: Dict[str, Union[int, float, bool, str]]
) -> None:
    """
    Change device's configuration options.

    Must be implemented as non blocking.
    Must be implemented as thread safe.

    :param configuration: Configuration options as reference:value pairs
    :type configuration: dict
    """
    raise NotImplementedError()
