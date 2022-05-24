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
from typing import Optional

from wolk.model.data_delivery import DataDelivery


@dataclass
class Device:
    """
    Device identified by key and password, and its outbound data mode.

    A device's data delivery mode is either an always connected device (PUSH),
    or a device that only periodically establishes connection and
    then subsequently checks if there are any pending messages
    that are intended for it (PULL).

    :ivar key: Device's key
    :vartype key: str
    :ivar password: Device's unique password
    :vartype password: str
    :ivar data_delivery: Is the device always connected or only periodically
    :vartype data_delivery: DataDelivery
    """

    key: str
    password: str
    data_delivery: Optional[DataDelivery] = field(default=DataDelivery.PUSH)
