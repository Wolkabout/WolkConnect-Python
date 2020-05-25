"""Alarm event model."""
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


@dataclass
class Alarm:
    """
    Holds information about a devices alarm.

    :ivar reference: Device alarm's reference as defined in device template
    :vartype reference: str
    :ivar active: Alarm's current state
    :vartype active: bool
    :ivar timestamp: Unix timestamp in miliseconds
    :vartype timestamp: int or None
    """

    reference: str
    active: bool
    timestamp: Optional[int] = field(default=None)
