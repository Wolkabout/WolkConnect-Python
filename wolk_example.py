""" Example of using WolkConnect library
"""

import logging
import WolkConnect
import WolkConnect.Sensor as Sensor
import WolkConnect.Actuator as Actuator
import WolkConnect.Alarm as Alarm
import WolkConnect.WolkDevice as WolkDevice
import WolkConnect.Serialization.WolkMQTTSerializer as WolkMQTTSerializer

logger = logging.getLogger("WolkConnect")
WolkConnect.setupLoggingLevel(logging.INFO)

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
    device = WolkDevice.WolkDevice(serial, password, serializer=serializer, sensors=sensors, actuators=actuators, alarms=alarms)
    device.connect()
    device.publishAll()
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

except WolkConnect.WolkMQTT.WolkMQTTClientException as e:
    print("WolkMQTTClientException occured with value: " + e.value)
