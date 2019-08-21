"""Stub method for setting new actuator value."""
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
from typing import Union


def handle_actuation(
    device_key: str, reference: str, value: Union[bool, int, float, str]
) -> None:
    """
    Set device actuator identified by reference to value.

    Must be implemented as non blocking.
    Must be implemented as thread safe.

    :param device_key: Device identifier
    :type device_key: str
    :param reference: Reference of the actuator
    :type reference: str
    :param value: Value to which to set the actuator
    :type value: str
    """
    pass
