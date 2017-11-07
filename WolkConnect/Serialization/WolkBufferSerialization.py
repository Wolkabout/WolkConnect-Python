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
    WolkBuffer serialization
"""

import time
import pickle
import copy
import logging

logger = logging.getLogger(__name__)

class WolkBuffer():
    """ Base buffer class
    """

    def serializeToFile(self, filename):
        """ Persist buffer into binary file
        """
        with open(filename, mode='wb') as outfile:
            pickle.dump(self.content, outfile, pickle.HIGHEST_PROTOCOL)

    def deserializeFromFile(self, filename):
        """ Load buffer content from  binary file
        """
        with open(filename, mode='rb') as infile:
            readings = pickle.load(infile)
            self.content = readings

    def __init__(self, content=None):
        """ Initialize buffer with content (which may be a list of items or single object)
        """
        if isinstance(content, list):
            self.content = content
        elif not content:
            self.content = []
        else:
            self.content = list(content)

    def addItem(self, item):
        """ Add item to buffer
        """
        self.content.append(item)

    def addItems(self, items):
        """ Add list of items to buffer
        """
        self.content.extend(items)

    def getContent(self):
        """ Get buffer content as list of items
        """
        return self.content

    def clear(self):
        """ Clear buffer
        """
        self.content.clear()


""" WolkSense Serializer for WolkConnect
"""
class WolkReadingsBuffer(WolkBuffer):
    """ WolkReadingsBuffer
    """
    def __init__(self, content=None, useCurrentTimestamp=False):
        """ Initialize readings buffer with content that may be
            list of readings, a single reading or None.

            Content is deep copied and stored in the buffer,
            preventing unintentional side effects like changing reading values/timestamps.

            If useCurrentTimestamp is True, each reading will be set the current timestamp,
            otherwise, timestamp from the reading will not be changed.
        """

        if not content:
            super().__init__(content)
            return

        readings = copy.deepcopy(content)

        if useCurrentTimestamp:
            timestamp = int(time.time())
            if isinstance(readings, list):
                for reading in readings:
                    reading.timestamp = timestamp
            else:
                readings.timestamp = timestamp

        super().__init__(readings)

    def getReadings(self):
        """ Get buffer content as list of readings
        """
        readings = super().getContent()
        return readings

    def addReading(self, reading, useCurrentTimestamp=False):
        """ Add a reading

            If useCurrentTimestamp is True, the current timestamp will be set to the reading
            otherwise, timestamp from the reading will not be changed.
        """
        readingCopy = copy.deepcopy(reading)
        if useCurrentTimestamp:
            readingCopy.timestamp = time.time()

        super().addItem(readingCopy)

    def addReadings(self, readings, useCurrentTimestamp=False):
        """ Add list of readings

            If useCurrentTimestamp is True, each reading will be set the current timestamp,
            otherwise, timestamp from the reading will not be changed.
        """
        readingsCopy = copy.deepcopy(readings)
        if useCurrentTimestamp:
            timestamp = time.time()
            for reading in readingsCopy:
                reading.timestamp = timestamp

        super().addItems(readingsCopy)

    def clearReadings(self):
        """ Clear readings
        """
        super().clear()


class WolkAlarmsBuffer(WolkBuffer):
    """ WolkAlarmsBuffer
    """
    def __init__(self, alarms=None):
        if alarms:
            timestamp = int(time.time())
            for alarm in alarms:
                if not alarm.timestamp:
                    alarm.timestamp = timestamp
        super().__init__(alarms)

    def getAlarms(self):
        """ Get buffer content as list of alarms
        """
        return super().getContent()

    def addAlarm(self, alarm):
        """ Add alarm
        """
        super().addItem(alarm)

    def addAlarms(self, alarms):
        """ Add alarms
        """
        super().addItems(alarms)

    def clearAlarms(self):
        """ Clear alarms
        """
        super().clear()
