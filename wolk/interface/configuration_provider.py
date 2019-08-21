"""Stub method for providing current device configuration options."""
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
from typing import Dict, Union, Tuple


def get_configuration(
    device_key: str
) -> Dict[
    str,
    Union[
        int,
        float,
        bool,
        str,
        Tuple[int, int],
        Tuple[int, int, int],
        Tuple[float, float],
        Tuple[float, float, float],
        Tuple[str, str],
        Tuple[str, str, str],
    ],
]:
    """
    Get current configuration options.

    Reads device configuration and returns it as a dictionary
    with device configuration reference as key,
    and device configuration value as value.
    Must be implemented as non blocking.
    Must be implemented as thread safe.

    :param device_key: Device identifier
    :type device_key: str
    :returns: configuration
    :rtype: dict
    """
    pass
