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
import abc
import pickle

import json
import logging
import WolkConnect.Alarm as Alarm
import WolkConnect.Sensor as Sensor

logger = logging.getLogger(__name__)

class WolkBuffer(abc.ABC):
    """ Abstract MQTT serializer class
    """

    def serializeToFile(self, filename):
        with open(filename, mode='wb') as outfile:
            pickle.dump(self.content, outfile, pickle.HIGHEST_PROTOCOL)

    def deserializeFromFile(self, filename):
        with open(filename, mode='rb') as infile:
            readings = pickle.load(infile)
            self.content = readings


    def __init__(self, content=None):
        super().__init__()
        if not content:
            return 

        if type(content) is list:
            self.content = content
        else:
            self.content = list(content)

    def addItem(self, item):
        self.content.append(item)

    def addItems(self, items):
        self.content.extend(items)
    
    def getContent(self):
        return self.content

    def clear(self):
        self.content.clear()


""" WolkSense Serializer for WolkConnect
"""
class WolkReadingsBuffer(WolkBuffer):
    """ WolkReadingsBuffer
    """
    def __init__(self, readings=None):
        if readings:
            timestamp = int(time.time())
            for reading in readings:
                if not reading.timestamp:
                    reading.timestamp = timestamp
        super().__init__(readings)

    def getReadings(self):
        readings = super().getContent()
        readingsDict = {}

        for reading in readings:
            readingsForTimestamp = []
            try:
                readingsForTimestamp = readingsDict[reading.timestamp]
            except KeyError:
                readingsDict[reading.timestamp] = readingsForTimestamp

            readingsForTimestamp.append(reading)

        readingsCollection = Sensor.ReadingsCollection()
        for (key, value) in readingsDict.items():
            # print("new key ",key)
            # for val in value:
            #     print(val)
            rds = Sensor.ReadingsWithTimestamp(value,key)
            readingsCollection.addReadings(rds)

        # print("print(readingsCollection.readings)")
        # print(readingsCollection.readings)
        # for rds in readingsCollection.readings:
        #     print("rds")
        #     print(rds)
        #     for rdsItem in rds.readings:
        #         print("rdsItem")
        #         print(rdsItem)

        return readingsCollection


    def addReading(self, reading):
        """ Add reading
        """
        if not reading.timestamp:
            reading.timestamp = time.time()

        super().addItem(reading)

    def addReadings(self, readings):
        """ Add readings
        """
        timestamp = time.time()
        for reading in readings:
            if not reading.timestamp:
                reading.timestamp = timestamp

        super().addItems(readings)

    def clearReadings(self):
        super().clear()


class WolkAlarmsBuffer(WolkBuffer):
    """ WolkAlarmsBuffer
    """
    def __init__(self, alarms=None):
        super().__init__(alarms)

    def getAlarms(self):
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
        super().clear()


