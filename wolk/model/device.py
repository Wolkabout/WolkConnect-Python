"""Everything needed for authenticating a device on WolkAbout IoT Platform."""
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
from typing import List


@dataclass
class Device:
    """
    Device identified by key and password, and list of actuator references.

    :ivar key: Device's key
    :vartype key: str
    :ivar password: Device's unique password
    :vartype password: str
    :ivar actuator_references: Actuator references present on device
    :vartype actuator_references: List[str]
    """

    key: str
    password: str
    actuator_references: List[str] = field(default_factory=list)
