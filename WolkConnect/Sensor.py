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
from enum import unique
import WolkConnect.ReadingType as ReadingType

@unique
class SensorType(ReadingType.ReadingType):
    """ Sensor types
    """
    TEMPERATURE = ("T", ReadingType.DataType.NUMERIC, -40.0, 80.0)
    PRESSURE = ("P", ReadingType.DataType.NUMERIC, 900.0, 1100.0)
    HUMIDITY = ("H", ReadingType.DataType.NUMERIC, 0.0, 100.0)
    LIGHT = ("LT", ReadingType.DataType.NUMERIC, 0.0, 100.0)
    ACCELEROMETER = ("ACL", ReadingType.DataType.NUMERIC, -1.0, 1.0, 3, "|")
    MAGNETOMETER = ("MAG", ReadingType.DataType.NUMERIC, None, None, 3, "|")
    GYROSCOPE = ("GYR", ReadingType.DataType.NUMERIC, None, None, 3, "|")
    STEPS = ("STP", ReadingType.DataType.NUMERIC)
    HEARTRATE = ("BPM", ReadingType.DataType.NUMERIC, 0.0, 1000.0)
    CALORIES = ("KCAL", ReadingType.DataType.NUMERIC, 0.0, 10000.0)
    GENERIC = ("GEN", ReadingType.DataType.NUMERIC)
    AIR_QUALITY = ("O", ReadingType.DataType.NUMERIC, 0.0, 10000.0)

class RawReading():
    """ Free form reading with reference, value and timestamp
    """
    def __init__(self, reference, value, timestamp=None):
        self.reference = reference
        self.value = value
        self.timestamp = timestamp

class Reading():
    """ Reading with SensorType and float values list
    """
    def __init__(self, sensorType, values, times=1.0, timestamp=None):
        self.sensorType = sensorType
        self.readingValues = values
        self.times = times
        self.timestamp = timestamp

    def setReadingValue(self, value):
        """ Set reading value
        """
        self.readingValues = [value]

    def setReadingValues(self, values):
        """ Set reading values
        """
        self.readingValues = values
    
    def setTimestamp(self, timestamp):
        self.timestamp = timestamp

    def __str__(self):
        return "Reading sensor type={0} values={1}, timestamp={2}, times={3}".format(self.sensorType, self.readingValues, self.timestamp, self.times)

    def asRawReading(self):
        return RawReading(self.sensorType.reference, self.value, self.timestamp)


class TemperatureReading(Reading):
    """ Temperature reading in Celsius degrees
    """
    def __init__(self, temperature=None, timestamp=None):
        super().__init__(SensorType.TEMPERATURE, [temperature], 10.0, timestamp)


class PressureReading(Reading):
    """ Pressure reading in mbar
    """
    def __init__(self, pressure=None, timestamp=None):
        super().__init__(SensorType.PRESSURE, [pressure], 10.0, timestamp)


class HumidityReading(Reading):
    """ Humidity reading in %
    """
    def __init__(self, humidity=None, timestamp=None):
        super().__init__(SensorType.HUMIDITY, [humidity], 10.0, timestamp)

class AirQualityReading(Reading):
    """ Air quality reading in ppm
    """
    def __init__(self, air_quality=None, timestamp=None):
        super().__init__(SensorType.AIR_QUALITY, [air_quality], 1.0, timestamp)

class LightReading(Reading):
    """ Light reading in %
    """
    def __init__(self, light=None, timestamp=None):
        super().__init__(SensorType.LIGHT, [light], 10.0, timestamp)


class StepsReading(Reading):
    """ Steps reading
    """
    def __init__(self, steps=None, timestamp=None):
        super().__init__(SensorType.STEPS, [steps], 1.0, timestamp)


class HeartrateReading(Reading):
    """ Heartrate reading in bpm
    """
    def __init__(self, heartrate=None, timestamp=None):
        super().__init__(SensorType.HEARTRATE, [heartrate], 1.0, timestamp)


class CaloriesReading(Reading):
    """ Calories reading in kcal
    """
    def __init__(self, calories=None, timestamp=None):
        super().__init__(SensorType.CALORIES, [calories], 1.0, timestamp)


class GenericReading(Reading):
    """ Generic reading (no unit)
    """
    def __init__(self, generic=None, times=10.0, timestamp=None):
        super().__init__(SensorType.GENERIC, [generic], times, timestamp)


class _XYZReading(Reading):
    """ Reading with x, y and z axis
    """
    def __init__(self, readingType, xValue=None, yValue=None, zValue=None, times=1.0, timestamp=None):
        super().__init__(readingType, [xValue, yValue, zValue], times, timestamp)


class AccelerometerReading(_XYZReading):
    """ Accelerometer reading with x, y and z axis in G
    """
    def __init__(self, xValue=None, yValue=None, zValue=None, times=10.0, timestamp=None):
        super().__init__(SensorType.ACCELEROMETER, xValue, yValue, zValue, times, timestamp)


class MagnetometerReading(_XYZReading):
    """ Magnetometer reading with x, y and z axis in uT
    """
    def __init__(self, xValue=None, yValue=None, zValue=None, times=10.0, timestamp=None):
        super().__init__(SensorType.MAGNETOMETER, xValue, yValue, zValue, times, timestamp)


class GyroReading(_XYZReading):
    """ Gyro reading with x, y and z axis in deg/sec
    """
    def __init__(self, xValue=None, yValue=None, zValue=None, times=10.0, timestamp=None):
        super().__init__(SensorType.GYROSCOPE, xValue, yValue, zValue, times, timestamp)

class ReadingsWithTimestamp():
    """ List of readings for defined timestamp
    """
    def __init__(self, timestamp=None):
        self.readings = []
        self.timestamp = timestamp

    # def __init__(self, reading, timestamp=None):
    #     self.readings = [reading]
    #     self.timestamp = timestamp

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
    def __init__(self):
        self.readings = []

    # def __init__(self, readings):
    #     self.readings = [readings]

    def addReadings(self, readings):
        """ Add readings
        """
        self.readings.append(readings)

    def addListOfReadings(self, readings):
        """ Add list of readings
        """
        self.readings.extend(readings)
