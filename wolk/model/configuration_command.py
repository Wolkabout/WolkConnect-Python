"""Configuration command received from WolkAbout IoT Platform."""
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

from dataclasses import dataclass, field
from enum import Enum, auto, unique
from typing import Dict, Optional, Tuple, Union


@unique
class ConfigurationCommandType(Enum):
    """Configuration command type.

    :ivar GET: Get current configuration options
    :vartype GET: int
    :ivar SET: Set configuration to value
    :vartype SET: int
    """

    GET = auto()
    SET = auto()


@dataclass
class ConfigurationCommand:
    """Configuration command with command and optionally value.

    :ivar command: Configuration command received
    :vartype command: int
    :ivar value: Set configuration to value
    :vartype value: Optional[dict]
    """

    command: ConfigurationCommandType
    value: Optional[Dict[str, Union[bool, int, float, str, Tuple]]] = field(
        default=None
    )
