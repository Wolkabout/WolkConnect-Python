"""Stub function for providing current device configuration options."""
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
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from wolk.model.state import State

ConfigurationValue = Optional[
    Union[
        int,
        float,
        bool,
        str,
        Tuple[int, int],
        Tuple[int, int, int],
        Tuple[float, float],
        Tuple[float, float, float],
    ]
]


def get_configuration() -> List[
    Dict[str, Union[str, ConfigurationValue, State, int]]
]:
    """
    Get current configuration options.

    Reads device configuration and returns it as a list of dictionaries
    with the following fields:
    `reference` - string that identifies configuration option
    `value` - current configuration value, None if unable to read
    `status` - state of the configuration: ready when functioning normally,
    busy when in the process of changing value, and error if unable to read
    `last_modified` - UTC timestamp when the value was last modified

    Must be implemented as non blocking.
    Must be implemented as thread safe.

    :returns: configuration
    :rtype: list
    """
    raise NotImplementedError()
