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


@dataclass
class Device:
    """
    Device identified by key and password, and its outbound data mode.

    The outbound data mode is either an always connected device,
    or a device that only periodically establishes connected and
    then subsequently checks if there are any pending messages
    that are intended for

    :ivar key: Device's key
    :vartype key: str
    :ivar password: Device's unique password
    :vartype password: str
    :ivar always_connected: Is the device always connected or only periodically
    :vartype always_connected: bool
    """

    key: str
    password: str
    always_connected: bool = True
