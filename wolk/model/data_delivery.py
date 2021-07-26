"""Enumeration of data delivery types."""
#   Copyright 2021 WolkAbout Technology s.r.o.
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
from enum import Enum


class DataDelivery(Enum):
    """
    Enumeration of available data delivery types.

    A device's data delivery mode is either an always connected device (PUSH),
    or a device that only periodically establishes connection and
    then subsequently checks if there are any pending messages
    that are intended for it (PULL).
    """

    PULL = "PULL"
    PUSH = "PUSH"
