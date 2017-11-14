""" Example of using WolkConnect library
"""

import logging
import time
import WolkConnect

logger = logging.getLogger("WolkConnect")
WolkConnect.setupLoggingLevel(logging.DEBUG)

# Device parameters
serial = "serial"
password = "password"

# Setup sensors, actuators and alarms
temperature = WolkConnect.Sensor("T", WolkConnect.DataType.NUMERIC, minValue=-40.0, maxValue=80.0)
pressure = WolkConnect.Sensor("P", WolkConnect.DataType.NUMERIC, minValue=900.0, maxValue=1100.0)
humidity = WolkConnect.Sensor("H", WolkConnect.DataType.NUMERIC, minValue=0.0, maxValue=100.0)
sensors = [temperature, pressure, humidity]

switch = WolkConnect.Actuator("SW", WolkConnect.DataType.BOOLEAN, value=True)
slider = WolkConnect.Actuator("SL", WolkConnect.DataType.NUMERIC)
slider.setValue(20.0)
actuators = [switch, slider]

humidityHighAlarm = WolkConnect.Alarm("HH", True)
alarms = [humidityHighAlarm]

def mqttMessageHandler(wolkDevice, message):
    """ Handle single MQTT message from MQTT broker
        See WolkDevice._mqttResponseHandler for further explanations
    """
    actuator = wolkDevice.getActuator(message.ref)
    
    if not actuator:
        logger.warning("%s could not find actuator with ref %s", wolkDevice.serial, message.ref)
        return

    logger.info("%s received message %s", wolkDevice.serial, message)
    if message.wolkCommand == WolkConnect.WolkCommand.SET:
        actuator.value = message.value
        wolkDevice.publishActuator(actuator)
    elif message.wolkCommand == WolkConnect.WolkCommand.STATUS:
        wolkDevice.publishActuator(actuator)
    else:
        logger.warning("Unknown command %s", message.wolkCommand)


try:
    serializer = WolkConnect.WolkSerializerType.JSON_MULTI
    device = WolkConnect.WolkDevice(serial, password, serializer=serializer, responseHandler=mqttMessageHandler, sensors=sensors, actuators=actuators, alarms=alarms)
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
            wolkBuffer = WolkConnect.WolkReadingsBuffer()
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
            dummyReading = WolkConnect.RawReading("T", 17.9, timestamp)
            wolkBuffer.addReading(dummyReading)

            # persist buffer to file
            WolkConnect.serializeBufferToFile(wolkBuffer, "buffer.bfr")

            # create new buffer from file
            newBuffer = WolkConnect.deserializeBufferFromFile("buffer.bfr")

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
            wolkAlarmsBuffer = WolkConnect.WolkAlarmsBuffer()
            wolkAlarmsBuffer.addAlarms(deviceAlarms)

            # add new alarm to buffer
            humidityHighAlarm.resetAlarm()
            humidityHighAlarm.setTimestamp(time.time() + 1)
            wolkAlarmsBuffer.addAlarm(humidityHighAlarm)

            # persist buffer to file
            WolkConnect.serializeBufferToFile(wolkAlarmsBuffer, "alarms_buffer.bfr")

            # create new buffer from file
            newAlarmsBuffer = WolkConnect.deserializeBufferFromFile("alarms_buffer.bfr")

            # publish alarms from buffer
            device.publishBufferedAlarms(newAlarmsBuffer)

            # clear buffer
            newAlarmsBuffer.clear()

        elif option.upper() == "R":
            # publish raw Temperature 17.9
            device.publishRawReading(WolkConnect.RawReading("T", 17.9))
        elif option.upper() == "Q":
            print("quitting...")
            device.disconnect()
            exit(0)

except WolkConnect.WolkMQTT.WolkMQTTClientException as e:
    print("WolkMQTTClientException occured with value: " + e.value)
