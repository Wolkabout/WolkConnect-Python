#   Copyright 2018 WolkAbout Technology s.r.o.
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

"""
SensorReading Module.
"""


class SensorReading:
    """Measurement that device performed and wants to report to platform."""

    def __init__(self, reference, value, timestamp=None):
        """
        Sensor reading as data.

        :param reference: The reference of the sensor
        :type reference: str
        :param value: The value of the reading
        :type value: int or float or str
        :param timestamp: Unix timestamp. If not provided, platform will assign
        :type timestamp: int or None
        """
        self.reference = reference
        self.value = value
        self.timestamp = timestamp
