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

import time
from enum import unique
from WolkConnect.ReadingType import ReadingType, DataType

@unique
class AlarmType(ReadingType):
    """ Alarms
    """
    TEMPERATURE_HIGH = ("TH", DataType.BOOLEAN)
    TEMPERATURE_LOW = ("TL", DataType.BOOLEAN)
    HUMIDITY_HIGH = ("HH", DataType.BOOLEAN)

class Alarm():
    """ Alarm with alarm type
    """
    def __init__(self, alarmType, isSet=False, timestamp=None):
        self.alarmType = alarmType
        self.alarmValue = isSet
        self.timestamp = timestamp

    def setAlarm(self):
        """ Set alarm
        """
        self.alarmValue = True

    def resetAlarm(self):
        """ Reset alarm
        """
        self.alarmValue = False

    def setTimestamp(self, timestamp=None):
        self.timestamp = timestamp if timestamp else time.time()

class TemperatureHighAlarm(Alarm):
    """ Temperature high alarm
    """
    def __init__(self, isSet=False):
        super().__init__(AlarmType.TEMPERATURE_HIGH, isSet)

class TemperatureLowAlarm(Alarm):
    """ Temperature low alarm
    """
    def __init__(self, isSet=False):
        super().__init__(AlarmType.TEMPERATURE_LOW, isSet)

class HumidityHighAlarm(Alarm):
    """ Humidity high alarm
    """
    def __init__(self, isSet=False):
        super().__init__(AlarmType.HUMIDITY_HIGH, isSet)
