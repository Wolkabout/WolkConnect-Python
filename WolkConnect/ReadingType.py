#   Copyright 2017 WolkAbout Technology s.r.o.
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
    WolkConnect reading data types
"""

import time
from enum import Enum, unique

@unique
class DataType(Enum):
    """ Data types
    """
    NUMERIC = "NUMERIC"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    
class RawReading():
    """ Free form reading with reference, value and timestamp
    """
    def __init__(self, reference, value, timestamp=None):
        self.reference = reference
        self.value = value
        self.timestamp = timestamp
        if not timestamp:
            self.timestamp = time.time()


    def __str__(self):
        return "RawReading reference={0} value={1}, timestamp={2}".format(self.reference, self.value, self.timestamp)
