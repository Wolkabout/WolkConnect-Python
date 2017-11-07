""" Example of using WolkConnect library
"""

import logging
import time
import WolkConnect
import WolkConnect.Sensor as Sensor
import WolkConnect.Actuator as Actuator
import WolkConnect.Alarm as Alarm
import WolkConnect.WolkDevice as WolkDevice
import WolkConnect.Serialization.WolkMQTTSerializer as WolkMQTTSerializer
import WolkConnect.Serialization.WolkBufferSerialization as WolkBufferSerialization
import WolkConnect.ReadingType as ReadingType

logger = logging.getLogger("WolkConnect")
WolkConnect.setupLoggingLevel(logging.DEBUG)

# Device parameters
serial = "PYTHONJSON000001"
password = "69b17b3c-44b8-42d8-8270-91fc926ddc21"

# Setup sensors, actuators and alarms
temperature = Sensor.TemperatureReading()
pressure = Sensor.PressureReading()
humidity = Sensor.HumidityReading()
sensors = [temperature, pressure, humidity]

switch = Actuator.SwitchActuator(0)
slider = Actuator.SliderActuator(20.0)
actuators = [switch, slider]

humidityHighAlarm = Alarm.HumidityHighAlarm(True)
alarms = [humidityHighAlarm]

try:
    serializer = WolkMQTTSerializer.WolkSerializerType.JSON_MULTI
    integration_host = "api-integration.wolksense.com"
    trust_insecure_cert = True
    device = WolkDevice.WolkDevice(serial, password, host=integration_host, set_insecure=trust_insecure_cert,  serializer=serializer, sensors=sensors, actuators=actuators, alarms=alarms)
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
                randomValues = sensor.sensorType.generateRandomValues()
                sensor.setReadingValues(randomValues)
                sensor.setTimestamp(timestamp)

            # create a buffer with list of sensors
            wolkBuffer = WolkBufferSerialization.WolkReadingsBuffer(sensors)

            # set random values to sensors with timestamp for one minute in past
            timestamp = timestamp - 60
            for sensor in sensors:
                randomValues = sensor.sensorType.generateRandomValues()
                sensor.setReadingValues(randomValues)
                sensor.setTimestamp(timestamp)

            # add new sensors values to the buffer
            wolkBuffer.addReadings(sensors)

            # set random values to sensors with timestamp for two minute in past
            timestamp = timestamp - 60
            for sensor in sensors:
                randomValues = sensor.sensorType.generateRandomValues()
                sensor.setReadingValues(randomValues)
                sensor.setTimestamp(timestamp)

            # add new sensors values to the buffer
            wolkBuffer.addReadings(sensors)

            # add raw reading to buffer
            # i.e. it is possible to mix objects of type RawReadings and Readings in the buffer
            timestamp = timestamp - 60
            dummyReading = Sensor.RawReading("T",17.9, timestamp)
            wolkBuffer.addReading(dummyReading)

            # persist buffer to file
            wolkBuffer.serializeToFile("buffer.bfr")
            
            # create new buffer from file
            newBuffer = WolkBufferSerialization.WolkReadingsBuffer()
            newBuffer.deserializeFromFile("buffer.bfr")

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
        elif option.upper() == "R":
            # publish raw Temperature 17.9
            device.publishRawReading(Sensor.RawReading("T","17.9"))
        elif option.upper() == "Q":
            print("quitting...")
            device.disconnect()
            exit(0)

except WolkConnect.WolkMQTT.WolkMQTTClientException as e:
    print("WolkMQTTClientException occured with value: " + e.value)
