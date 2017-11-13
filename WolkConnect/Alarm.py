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
    Alarms
"""
import time

class Alarm():
    """ Alarm as defined in device manifest
        alarmRef - Alarm reference
        alarmValue - Current alarm value
    """
    def __init__(self, alarmRef, isSet=False, timestamp=None):
        self.alarmRef = alarmRef
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
        """ Set alarm timestamp
        """
        self.timestamp = timestamp if timestamp else time.time()
