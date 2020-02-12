"""Device connection states as defined on WolkAbout IoT Platform."""
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
#   limitations under the License.from enum import Enum
from enum import Enum
from enum import unique


@unique
class DeviceState(Enum):
    """
    Enumeration of device connection statuses.

    :ivar CONNECTED: Device currently connected to Platform.
    :vartype CONNECTED: str
    :ivar OFFLINE: Device disconnected from Platform.
    :vartype OFFLINE: str
    :ivar SLEEP: Device in a controlled offline state.
    :vartype SLEEP: str
    :ivar SERVICE_MODE: Device in service mode and may not respond to input from Platform.
    :vartype SERVICE_MODE: str
    """

    CONNECTED = "CONNECTED"
    OFFLINE = "OFFLINE"
    SLEEP = "SLEEP"
    SERVICE_MODE = "SERVICE_MODE"
