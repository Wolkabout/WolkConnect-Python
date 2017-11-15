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

def serializeBufferToFile(buffer, filename):
    """ Persist buffer into binary file
    """
    with open(filename, mode='wb') as outfile:
        pickle.dump(buffer, outfile, pickle.HIGHEST_PROTOCOL)

def deserializeBufferFromFile(filename):
    """ Load buffer content from  binary file
    """
    with open(filename, mode='rb') as infile:
        buffer = pickle.load(infile)
        return buffer

class WolkBuffer():
    """ Base buffer class
    """
    def __init__(self, content=None, capacity=0, overwrite=False):
        """ Initialize buffer with content (which may be a list of items or single object)
            capacity - if 0, there is no limit on amount of items in the buffer
            overwrite - when capacity is limited (e.g capacity > 0), and buffer is full
                        if overwrite = True, new items will overwrite the oldest
                        if overwrite = False, new items will not be added to the buffer
        """
        if isinstance(content, list):
            self.content = content
        elif not content:
            self.content = []
        else:
            self.content = list(content)

        self.capacity = capacity
        self.overwrite = overwrite

    def addItem(self, item):
        """ Add item to buffer
        """
        if self.capacity == 0 or len(self.content) < self.capacity:
            self.content.append(item)
        elif self.overwrite:
            del self.content[0]
            self.content.append(item)

    def addItems(self, items):
        """ Add list of items to buffer
        """
        for item in items:
            self.addItem(item)

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
    def __init__(self, content=None, useCurrentTimestamp=False, capacity=0, overwrite=False):
        """ Initialize readings buffer with content that may be
            list of Sensors/RawReadings, a single Sensor/RawReading or None.

            Content is deep copied and stored in the buffer,
            preventing unintentional side effects like changing reading values/timestamps.

            If useCurrentTimestamp is True, each reading will be set the current timestamp,
            otherwise, timestamp from the reading will not be changed.
        """

        if not content:
            super().__init__(content, capacity, overwrite)
            return

        readings = copy.deepcopy(content)

        if useCurrentTimestamp:
            timestamp = int(time.time())
            if isinstance(readings, list):
                for reading in readings:
                    reading.timestamp = timestamp
            else:
                readings.timestamp = timestamp

        super().__init__(readings, capacity, overwrite)

    def getReadings(self):
        """ Get buffer content
        """
        return super().getContent()

    def addReading(self, reading, useCurrentTimestamp=False):
        """ Add a Sensor/RawReading

            If useCurrentTimestamp is True, the current timestamp will be set to the reading
            otherwise, timestamp from the reading will not be changed.
        """
        readingCopy = copy.deepcopy(reading)
        if useCurrentTimestamp:
            readingCopy.timestamp = time.time()

        super().addItem(readingCopy)

    def addReadings(self, readings, useCurrentTimestamp=False):
        """ Add list of Sensors/RawReadings

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
        """ Clear buffer content
        """
        super().clear()

class WolkAlarmsBuffer(WolkBuffer):
    """ WolkAlarmsBuffer
    """

    def __init__(self, content=None, useCurrentTimestamp=False, capacity=0, overwrite=False):
        """ Initialize alarms buffer with content that may be
            list of alarms, a single alarm or None.

            Content is deep copied and stored in the buffer,
            preventing unintentional side effects.

            If useCurrentTimestamp is True, each alarm will be set the current timestamp,
            otherwise, timestamp from the alarm will not be changed.
        """

        if not content:
            super().__init__(content, capacity, overwrite)
            return

        alarms = copy.deepcopy(content)

        if useCurrentTimestamp:
            timestamp = int(time.time())
            if isinstance(alarms, list):
                for alarm in alarms:
                    alarm.timestamp = timestamp
            else:
                alarms.timestamp = timestamp

        super().__init__(alarms, capacity, overwrite)

    def getAlarms(self):
        """ Get buffer content as list of alarms
        """
        return super().getContent()

    def addAlarm(self, alarm, useCurrentTimestamp=False):
        """ Add an alarm

            If useCurrentTimestamp is True, the current timestamp will be set to the alarm
            otherwise, timestamp from the alarm will not be changed.
        """
        alarmCopy = copy.deepcopy(alarm)
        if useCurrentTimestamp:
            alarmCopy.timestamp = time.time()

        super().addItem(alarmCopy)

    def addAlarms(self, alarms, useCurrentTimestamp=False):
        """ Add list of alarms

            If useCurrentTimestamp is True, each alarm will be set the current timestamp,
            otherwise, timestamp from the alarm will not be changed.
        """
        alarmsCopy = copy.deepcopy(alarms)
        if useCurrentTimestamp:
            timestamp = time.time()
            for alarm in alarmsCopy:
                alarm.timestamp = timestamp

        super().addItems(alarmsCopy)

    def clearAlarms(self):
        """ Clear alarms
        """
        super().clear()
