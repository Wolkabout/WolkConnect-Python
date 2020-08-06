"""Stub function for providing current device configuration options."""
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
from typing import Dict
from typing import Union


def get_configuration() -> Dict[str, Union[int, float, bool, str]]:
    """
    Get current configuration options.

    Reads device configuration and returns it as a dictionary
    where the key is the configuration reference and value
    is the current configuration value.

    Must be implemented as non blocking.
    Must be implemented as thread safe.

    :returns: configurations
    :rtype: Dict[str, Union[int, float, bool, str]]
    """
    raise NotImplementedError()
