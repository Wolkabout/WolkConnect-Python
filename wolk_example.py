""" Example of using WolkConnect library
"""

import logging
import time
import WolkConnect
import WolkConnect.Sensor as Sensor
import WolkConnect.ReadingType as ReadingType
import WolkConnect.Actuator as Actuator
import WolkConnect.Alarm as Alarm
import WolkConnect.WolkDevice as WolkDevice
import WolkConnect.Serialization.WolkMQTTSerializer as WolkMQTTSerializer
import WolkConnect.Serialization.WolkBufferSerialization as WolkBufferSerialization

logger = logging.getLogger("WolkConnect")
WolkConnect.setupLoggingLevel(logging.DEBUG)

# Device parameters
serial = "serial"
password = "password"

# Setup sensors, actuators and alarms
temperature = Sensor.Sensor("T", ReadingType.DataType.NUMERIC, minValue=-40.0, maxValue=80.0)
pressure = Sensor.Sensor("P", ReadingType.DataType.NUMERIC, minValue=900.0, maxValue=1100.0)
humidity = Sensor.Sensor("H", ReadingType.DataType.NUMERIC, minValue=0.0, maxValue=100.0)
sensors = [temperature, pressure, humidity]

switch = Actuator.Actuator("SW", ReadingType.DataType.BOOLEAN, value=True)
slider = Actuator.Actuator("SL", ReadingType.DataType.NUMERIC)
slider.setValue(20.0)
actuators = [switch, slider]

humidityHighAlarm = Alarm.Alarm("HH", True)
alarms = [humidityHighAlarm]

try:
    serializer = WolkMQTTSerializer.WolkSerializerType.JSON_MULTI
    device = WolkDevice.WolkDevice(serial, password, serializer=serializer, sensors=sensors, actuators=actuators, alarms=alarms)
    device.connect()
    device.publishAll()
    while True:
        print("A to publish all sensors and actuators. Sensors will be set to default values (t=23.4℃, p=999.9mb, h=50.0%)")
        print("P to publish random reading values for each sensor.")
        print("C to publish current reading values of device sensors.")
        print("D to publish default reading values (t=23.4℃, p=999.9mb, h=50.0%) of device sensors for the current timestamp.")
        print("B to publish buffered readings.")
        print("O to publish one temperature reading t=23.4℃ for the current timestamp")
        print("H to publish humidity high alarm")
        print("X to publish buffered alarms")
        print("R to publish raw reading")
        print("Q to quit")
        option = input()
        if option.upper() == "A":
            temperature.setReadingValue(23.4)
            pressure.setReadingValue(999.9)
            humidity.setReadingValue(50.0)
            humidityHighAlarm.setAlarm()
            device.publishAll()
        elif option.upper() == "P":
            device.publishRandomReadings()
        elif option.upper() == "C":
            device.publishReadings()
        elif option.upper() == "D":
            temperature.setReadingValue(23.4)
            pressure.setReadingValue(999.9)
            humidity.setReadingValue(50.0)
            device.publishReadings(useCurrentTimestamp=True)
        elif option.upper() == "B":

            sensors = device.getSensors()
            # set random values to sensors
            timestamp = time.time()
            for sensor in sensors:
                randomValues = sensor.generateRandomValues()
                sensor.setReadingValues(randomValues)
                sensor.setTimestamp(timestamp)

            # create a buffer with list of sensors
            wolkBuffer = WolkBufferSerialization.WolkReadingsBuffer()
            wolkBuffer.addReadings(sensors)

            temperature.setReadingValue(23.4)
            pressure.setReadingValue(999.9)
            humidity.setReadingValue(50.0)
            wolkBuffer.addReadings([temperature, pressure, humidity])

            temperature.setReadingValue(16.7)
            temperature.setTimestamp(time.time())
            wolkBuffer.addReading(temperature)

            # set random values to sensors with timestamp for one minute in past
            timestamp = timestamp - 60
            for sensor in sensors:
                randomValues = sensor.generateRandomValues()
                sensor.setReadingValues(randomValues)
                sensor.setTimestamp(timestamp)

            # add new sensors values to the buffer
            wolkBuffer.addReadings(sensors)

            # set random values to sensors with timestamp for two minute in past
            timestamp = timestamp - 60
            for sensor in sensors:
                randomValues = sensor.generateRandomValues()
                sensor.setReadingValues(randomValues)
                sensor.setTimestamp(timestamp)

            # add new sensors values to the buffer
            wolkBuffer.addReadings(sensors)

            # add raw reading to buffer
            # i.e. it is possible to mix objects of type RawReadings and Readings in the buffer
            timestamp = timestamp - 60
            dummyReading = Sensor.RawReading("T", 17.9, timestamp)
            wolkBuffer.addReading(dummyReading)

            # persist buffer to file
            WolkBufferSerialization.serializeToFile(wolkBuffer, "buffer.bfr")

            # create new buffer from file
            newBuffer = WolkBufferSerialization.deserializeFromFile("buffer.bfr")

            # publish readings from buffer
            device.publishBufferedReadings(newBuffer)

            # clear buffer
            newBuffer.clear()

        elif option.upper() == "O":
            temperature.setReadingValue(23.4)
            temperature.setTimestamp(time.time())
            device.publishReading(temperature)
        elif option.upper() == "H":
            device.publishAlarm(humidityHighAlarm)
        elif option.upper() == "X":

            deviceAlarms = device.getAlarms()
            # set alarms
            timestamp = time.time()
            for alarm in deviceAlarms:
                alarm.setAlarm()
                alarm.setTimestamp(timestamp)

            # create a buffer with list of alarms
            wolkAlarmsBuffer = WolkBufferSerialization.WolkAlarmsBuffer()
            wolkAlarmsBuffer.addAlarms(deviceAlarms)

            # add new alarm to buffer
            humidityHighAlarm.resetAlarm()
            humidityHighAlarm.setTimestamp(time.time())
            wolkAlarmsBuffer.addAlarm(humidityHighAlarm)

            # persist buffer to file
            WolkBufferSerialization.serializeToFile(wolkAlarmsBuffer, "alarms_buffer.bfr")

            # create new buffer from file
            newAlarmsBuffer = WolkBufferSerialization.deserializeFromFile("alarms_buffer.bfr")

            # publish alarms from buffer
            device.publishBufferedAlarms(newAlarmsBuffer)

            # clear buffer
            newAlarmsBuffer.clear()

        elif option.upper() == "R":
            # publish raw Temperature 17.9
            device.publishRawReading(Sensor.RawReading("T", 17.9))
        elif option.upper() == "Q":
            print("quitting...")
            device.disconnect()
            exit(0)

except WolkConnect.WolkMQTT.WolkMQTTClientException as e:
    print("WolkMQTTClientException occured with value: " + e.value)
