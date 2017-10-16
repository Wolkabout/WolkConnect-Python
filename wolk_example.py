""" Example of using WolkConnect library
"""

import logging
import Sensor
import Actuator
import Alarm
import WolkDevice
import WolkMQTT
import Serialization.WolkMQTTSerializer as WolkMQTTSerializer
from __init__ import setupLoggingLevel

logger = logging.getLogger("WolkConnect")
setupLoggingLevel(logging.INFO)

# Device parameters
serial = "serial"
password = "password"

# Setup sensors, actuators and alarms
temperature = Sensor.TemperatureReading()
pressure = Sensor.PressureReading()
humidity = Sensor.HumidityReading()
sensors = [temperature, pressure, humidity]

switch = Actuator.SwitchActuator(0)
slider = Actuator.SliderActuator(20.0)
actuators = [switch, slider]

humidityHigh = Alarm.HumidityHighAlarm(True)
alarms = [humidityHigh]

try:
    serializer = WolkMQTTSerializer.WolkSerializerType.JSON_MULTI
    device = WolkDevice.WolkDevice(serial, password, serializer, sensors, actuators, alarms)
    device.connect()
    while True:
        print("A to publish all readings and actuators")
        print("P to publish readings")
        print("H to publish alarm high")
        print("Q to quit")
        option = input()
        if option.upper() == "A":
            device.publishAll()
        elif option.upper() == "P":
            device.publishAllReadings()
        elif option.upper() == "H":
            device.publishAlarm(humidityHigh)
        elif option.upper() == "Q":
            print("quitting...")
            device.disconnect()
            exit(0)

except WolkMQTT.WolkMQTTClientException as e:
    print("WolkMQTTClientException occured with value: " + e.value)
