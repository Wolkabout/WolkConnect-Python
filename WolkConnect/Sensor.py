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
    Sensors and readings
"""
import time
import random
import string
import WolkConnect.ReadingType as ReadingType

class Sensor():
    """ Sensor as defined in device manifest
        sensorRef - Sensor reference
        dataType - Any of DataType members (NUMERIC, STRING or BOOLEAN)
        value - Current reading value of the sensor.
        minValue - If applicable, minimum reading value of the sensor
        maxValue - If applicable, maximum reading value of the sensor
        dataSize - By default it is 1 rendering sensor reading values as scalar
            e.g. temperature sensor would typically have scalar reading values as t=23.4℃
                accelerometer sensor would typically have 3 reading values for x, y, z; like (0.1, -1.0, 0.5) G
        dataDelimiter - Delimitier for parsing values (applicable if dataSize > 1)
        timestamp - timestamp for value
    """
    def __init__(self, sensorRef, dataType, value=None, minValue=None, maxValue=None, dataSize=1, dataDelimiter="", timestamp=None):
        self.sensorRef = sensorRef
        self.dataType = dataType
        self.readingValue = value
        if not self.readingValue:
            self.readingValue = []
        self.minValue = minValue
        self.maxValue = maxValue
        self.dataSize = dataSize
        self.dataDelimiter = dataDelimiter
        self.timestamp = timestamp

    def setReadingValue(self, value):
        """ Set reading value
        """
        self.readingValue = [value]

    def setReadingValues(self, values):
        """ Set reading values
        """
        self.readingValue = values

    def setTimestamp(self, timestamp):
        """ Set reading timestamp
        """
        self.timestamp = timestamp if timestamp else time.time()

    @property
    def isScalar(self):
        """ Is reading type scalar i.e. data size is 1
        """
        return self.dataSize == 1

    def __str__(self):
        isScalar = " isScalar={0}".format(self.isScalar)
        dataSizeString = "" if self.dataSize == 1 else " dataSize={0}".format(self.dataSize)
        dataDelimiter = " dataDelimiter={0}".format(self.dataDelimiter) if dataSizeString else ""
        sensorType = self.sensorRef + ":" + self.dataType.value + isScalar + dataSizeString + dataDelimiter
        return "Reading sensor type={0} values={1}, timestamp={2}".format(sensorType, self.readingValue, self.timestamp)

    def getRawReading(self):
        """ Convert reading to RawReading; useful for easier serialization to MQTT messages
        """
        value = self.readingValue
        if not value:
            value = []
            return ReadingType.RawReading(self.sensorRef, value, self.timestamp)

        if self.isScalar:
            value = self.readingValue[0]

        return ReadingType.RawReading(self.sensorRef, value, self.timestamp)

    def generateRandomValues(self):
        """ Generate random value in range (minValue, maxValue)
            A handy way to use for device simulator
        """
        if self.dataType == ReadingType.DataType.NUMERIC:
            if self.minValue is None or self.maxValue is None:
                return None

            return [random.uniform(self.minValue, self.maxValue) for _ in range(self.dataSize)]
        elif self.dataType == ReadingType.DataType.BOOLEAN:
            return [bool(int(random.uniform(0, 1)))]

        rndValue = random.SystemRandom()
        return [''.join(rndValue.choice(string.ascii_uppercase + string.digits) for _ in range(10))]

class ReadingsWithTimestamp():
    """ List of readings for defined timestamp
    """
    def __init__(self, readings, timestamp=None):
        self.readings = readings
        self.timestamp = timestamp

    def addReading(self, reading):
        """ Add single reading
        """
        self.readings.append(reading)

    def addReadings(self, readings):
        """ Add list of readings
        """
        self.readings.extend(readings)

class ReadingsCollection():
    """ List of ReadingsWithTimestamp
    """

    def __init__(self, readings=None):
        if not readings:
            self.readings = []
        else:
            self.readings = [readings]

    def addReadings(self, readings):
        """ Add readings with timestamp
        """
        self.readings.append(readings)

    def addListOfReadings(self, readings):
        """ Add list of readings with timestamp
        """
        self.readings.extend(readings)

    @staticmethod
    def collectionFromReadingsList(readings):
        """ turn list of readings into ReadingsCollection
        """

        readingsDict = {}

        for reading in readings:
            readingsForTimestamp = []
            try:
                readingsForTimestamp = readingsDict[reading.timestamp]
            except KeyError:
                readingsDict[reading.timestamp] = readingsForTimestamp

            readingsForTimestamp.append(reading)

        readingsCollection = ReadingsCollection()
        for (key, value) in readingsDict.items():
            rds = ReadingsWithTimestamp(value, key)
            readingsCollection.addReadings(rds)

        return readingsCollection
