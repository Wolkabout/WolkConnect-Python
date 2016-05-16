from enum import Enum
from WolkSenseWebClient import WolkSenseDevice
import time
import paho.mqtt.client as mqtt

class ReadingType(Enum):
    TEMPERATURE = "T"
    PRESSURE = "P"
    HUMIDITY = "H"
    LIGHT = "LT"
    ACCELEROMETER = "ACL"
    MAGNETOMETER = "MAG"
    GYROSCOPE = "GYR"
    STEPS = "STP"
    HEARTRATE = "BPM"
    CALORIES = "KCAL"


class _Reading():
    """ Reading with type of ReadingType and float values list
    """

    def __init__(self, type, values, times=1.0):
        self.readingType = type
        self.readingValues = values
        self.times = times

    def asMQTTString(self):
        if len(self.readingValues) == 0:
            return ""

        listOfInt = [int(r * self.times) for r in self.readingValues]
        listOfStrings = []
        for i in listOfInt:
            if i >= 10:
                listOfStrings.append("{:+.0f}".format(i))
            else: # pad one digit numbers with leading 0 and keep sign prefix
                listOfStrings.append("{:+.0f}".format(i).zfill(3))

        correctedValues = "".join(listOfStrings)
        mqttString = self.readingType.value + ":" + correctedValues
        return mqttString


class TemperatureReading(_Reading):
    """ Temperature reading in Celsius degrees
    """
    def __init__(self, temperature):
        super().__init__(ReadingType.TEMPERATURE, [temperature], 10.0)


class PressureReading(_Reading):
    """ Pressure reading in mbar
    """
    def __init__(self, pressure):
        super().__init__(ReadingType.PRESSURE, [pressure], 10.0)


class HumidityReading(_Reading):
    """ Humidity reading in %
    """
    def __init__(self, humidity):
        super().__init__(ReadingType.HUMIDITY, [humidity], 10.0)


class LightReading(_Reading):
    """ Light reading in %
    """
    def __init__(self, light):
        super().__init__(ReadingType.LIGHT, [light], 10.0)


class StepsReading(_Reading):
    """ Steps reading
    """
    def __init__(self, steps):
        super().__init__(ReadingType.STEPS, [steps])


class HeartrateReading(_Reading):
    """ Heartrate reading in bpm
    """
    def __init__(self, heartrate):
        super().__init__(ReadingType.HEARTRATE, [heartrate])


class CaloriesReading(_Reading):
    """ Calories reading in kcal
    """
    def __init__(self, calories):
        super().__init__(ReadingType.CALORIES, [calories])


class _XYZReading(_Reading):
    """ Reading with x, y and z axis
    """
    def __init__(self, type, xValue, yValue, zValue, times=1.0):
        super().__init__(type, [xValue, yValue, zValue], times)


class AccelerometerReading(_XYZReading):
    """ Accelerometer reading with x, y and z axis in G
    """
    def __init__(self, xValue, yValue, zValue):
        super().__init__(ReadingType.ACCELEROMETER, xValue, yValue, zValue, 10.0)


class MagnetometerReading(_XYZReading):
    """ Magnetometer reading with x, y and z axis in uT
    """
    def __init__(self, xValue, yValue, zValue):
        super().__init__(ReadingType.MAGNETOMETER, xValue, yValue, zValue, 10.0)


class GyroReading(_XYZReading):
    """ Gyro reading with x, y and z axis in deg/sec
    """
    def __init__(self, xValue, yValue, zValue):
        super().__init__(ReadingType.GYROSCOPE, xValue, yValue, zValue, 10.0)


class ReadingsWithTimestamp():
    """ List of readings for defined timestamp
    """
    def __init__(self, timestamp):
        self.readings = []
        self.timestamp = timestamp

    def __init__(self, reading, timestamp):
        self.readings = [reading]
        self.timestamp = timestamp

    def __init__(self, readings, timestamp):
        self.readings = readings
        self.timestamp = timestamp

    def addReading(self, reading):
        self.readings.append(reading)

    def addReadings(self, readings):
        self.readings.extend(readings)

    def asMQTTString(self):
        publishString = ""
        if len(self.readings):
            list = [r.asMQTTString() for r in self.readings]
            READING_SEPARATOR = ","
            readingsList = READING_SEPARATOR.join(list)
            timestampString = ""
            if self.timestamp is None:
                timestampString = str(int(time.time()))
            else:
                timestampString = str(int(self.timestamp))

            publishString  = "R:" + timestampString + READING_SEPARATOR + readingsList

        return publishString

class ReadingsCollection():
    """ List of ReadingsWithTimestamp
    """
    def __init__(self):
        self.readings = []

    def __init__(self, readings):
        self.readings = [readings]

    def addReadings(self, readings):
        self.readings.append(readings)

    def addListOfReadings(self, readings):
        self.readings.extend(readings)

    def asMQTTString(self):
        publishString = ""
        if len(self.readings):
            list = [r.asMQTTString() for r in self.readings]
            READINGS_SEPARATOR = "|"
            readingsList = READINGS_SEPARATOR.join(list)
            timestampString = str(int(time.time()))

            READINGS_TERMINATOR = ";"
            publishString  = "RTC " + timestampString + READINGS_TERMINATOR + "READINGS " + readingsList + READINGS_TERMINATOR

        return publishString


class WolkSenseMQTTClientException(Exception):
    """ WolkSenseMQTTClientException raised whenever there is an error in
    communication with WolkSense mqtt broker
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class WolkSenseMQTTClient:
    """ WolkSenseMQTTClient for publishing readings to WolkSense cloud
    """

    def __init__(self, wolkSenseDevice):
        self.device = wolkSenseDevice
        # Setup MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self._on_mqtt_connect
        self.client.on_publish = self._on_mqtt_publish
        self.client.on_disconnect = self._on_mqtt_disconnect
        self.client.tls_set("ca.crt")
        self.client.username_pw_set(self.device.serial, self.device.password)
        self.host = "wolksense.com"
        self.port = 8883
        self.keepalive = 60

    # Setup MQTT callback handlers
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            payload = self.readingsCollection.asMQTTString()
            if len(payload):
                self.client.publish(self.device.publishTopic, payload)
            else:
                self.client.disconnect()
                raise WolkSenseMQTTClientException("No payload to publish. Disconnecting...")


    def _on_mqtt_publish(self, client, userdata, mid):
        self.client.disconnect()

    def _on_mqtt_disconnect(self, client, usedata, rc):
        self.readingsCollection = None
        if rc != 0:
            raise WolkSenseMQTTClientException("Disconnected with error code " + str(rc))


    def publishReadings(self, readingsCollection):
        """ publish ReadingsCollection to mqtt broker
        """
        if readingsCollection is None:
            raise WolkSenseMQTTClientException("No readings to publish")

        self.readingsCollection = readingsCollection
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.loop_forever()
