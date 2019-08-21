"""Actuator command received from WolkAbout IoT Platform."""
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
from typing import Optional, Union


@unique
class ActuatorCommandType(Enum):
    """Actuator command type.

    :ivar GET: Get current actuator value
    :vartype GET: int
    :ivar SET: Set actuator to value
    :vartype SET: int
    """

    GET = auto()
    SET = auto()


@dataclass
class ActuatorCommand:
    """Actuator command for reference with command and optionally value.

    :ivar reference: What actuator is the command for
    :vartype reference: str
    :ivar command: Type of command received
    :vartype command: ActuatorCommandType
    :ivar value: Value to be set
    :vartype value: Optional[Union[bool, int, float, str]]
    """

    reference: str
    command: ActuatorCommandType
    value: Optional[Union[bool, int, float, str]] = field(default=None)
