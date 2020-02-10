"""Actuator status model."""
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
from dataclasses import dataclass
from dataclasses import field
from typing import Optional
from typing import Union

from wolk.model.actuator_state import ActuatorState


@dataclass
class ActuatorStatus:
    """
    Holds information of a devices actuator current status.

    :ivar reference: Device actuator's reference as defined in device template
    :vartype reference: str
    :ivar state: Actuator's current state
    :vartype state: ActuatorState
    :ivar value: Current value of actuator, None only for error state
    :vartype value: Optional[Union[bool, int, float, str]]
    :ivar state: Optional timestamp when reading occurred
    :vartype state: Optional[int]
    """

    reference: str
    state: ActuatorState
    value: Optional[Union[bool, int, float, str]] = field(default=None)
    timestamp: Optional[int] = field(default=None)
