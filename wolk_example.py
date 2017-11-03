""" Example of using WolkConnect library
"""

import logging
import WolkConnect
import WolkConnect.Sensor as Sensor
import WolkConnect.Actuator as Actuator
import WolkConnect.Alarm as Alarm
import WolkConnect.WolkDevice as WolkDevice
import WolkConnect.Serialization.WolkMQTTSerializer as WolkMQTTSerializer
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
# actuators = []

# movementAlarm = Alarm.MovementAlarm(True)
# alarms = [movementAlarm]

humidityHighAlarm = Alarm.HumidityHighAlarm(True)
alarms = [humidityHighAlarm]


# print("print(ReadingType.ReadingType.__members__)")
# print(ReadingType.ReadingType.__members__.items())
# print(Sensor.SensorType.__members__.items())
# print(Alarm.AlarmType.__members__.items())
# print(Actuator.ActuatorType.__members__.items())

for name, member in ReadingType.ReadingType.__members__.items():
    print("Reading type ", name, member)

try:
    serializer = WolkMQTTSerializer.WolkSerializerType.JSON_MULTI
    integration_host = "api-integration.wolksense.com"
    trust_insecure_cert = True
    device = WolkDevice.WolkDevice(serial, password, host=integration_host, set_insecure=trust_insecure_cert,  serializer=serializer, sensors=sensors, actuators=actuators, alarms=alarms)
    device.connect()
    device.publishAll()
    while True:
        print("A to publish all readings and actuators")
        print("P to publish readings")
        print("H to publish humidity high alarm")
        # print("M to publish movement alarm")
        print("R to publish raw reading")
        print("Q to quit")
        option = input()
        if option.upper() == "A":
            device.publishAll()
        elif option.upper() == "P":
            device.publishAllReadings()
        # elif option.upper() == "M":
        #     device.publishAlarm(movementAlarm)
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
