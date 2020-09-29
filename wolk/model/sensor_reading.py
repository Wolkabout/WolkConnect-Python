"""Sensor reading model."""
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
from typing import Tuple
from typing import Union


@dataclass
class SensorReading:
    """
    Holds information about a sensor reading.

    :ivar reference: Device sensor's reference as defined in device template
    :vartype reference: str
    :ivar value: Data that the sensor reading yielded
    :vartype value: bool or int or float or str or tuple of int/float
    :ivar timestamp:  Unix timestamp in miliseconds
    :vartype timestamp: Optional[int]
    """

    reference: str
    value: Union[
        bool,
        int,
        Tuple[int, ...],
        float,
        Tuple[float, ...],
        str,
    ]
    timestamp: Optional[int] = field(default=None)
