"""Stub function for providing current device actuator status."""
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
from typing import Optional
from typing import Tuple
from typing import Union

from wolk.model.state import State


def get_actuator_status(
    reference: str,
) -> Tuple[State, Optional[Union[bool, int, float, str]]]:
    """
    Get current actuator status identified by reference.

    Reads the status of actuator from the device
    and returns it as a tuple containing the actuator state and current value.

    If unable to get current actuator value,
    return `(State.ERROR, None)`.

    Must be implemented as non blocking.
    Must be implemented as thread safe.

    :param reference: Actuator reference
    :type reference: str
    :returns: (state, value)
    :rtype: (State, bool or int or float or str or None)
    """
    raise NotImplementedError()
