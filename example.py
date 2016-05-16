from WolkSenseMQTT import WolkSenseMQTTClient, WolkSenseMQTTClientException
from WolkSenseMQTT import TemperatureReading, PressureReading, HumidityReading
from WolkSenseMQTT import AccelerometerReading, MagnetometerReading, GyroReading
from WolkSenseMQTT import StepsReading, HeartrateReading, CaloriesReading, LightReading
from WolkSenseMQTT import ReadingsWithTimestamp, ReadingsCollection
import WolkSenseWebClient as WebAPI
import time

# Create device for user
userEmail = "sombody@domain.ext"
userPassword = "somesecretpassword"
deviceName = "somedevicename"

try:
    print("Activating {0} ...".format(deviceName))
    newDevice = WebAPI.WolkSenseWebClient.activateDeviceForUser(userEmail, userPassword, deviceName)
except WebAPI.WolkSenseWebClientException as e:
    print("WolkSenseWebClientException occured with value: " + e.value)
else:
    print("{0} activated with serial:{1} password:{2}".format(newDevice.name, newDevice.serial, newDevice.password))
    print("--------------------------")

    # Setup some readings...
    r0 = TemperatureReading(24.3)
    r1 = PressureReading(1003.1)
    r2 = HumidityReading(37.4)
    r3 = LightReading(15.0)
    r4 = AccelerometerReading(0.3, 0.4, 0.5)
    r5 = MagnetometerReading(-0.3, -0.4, -0.5)
    r6 = GyroReading(23.4, 56.7, 89.9)
    r7 = StepsReading(10)
    r8 = HeartrateReading(67)
    r9 = CaloriesReading(13)

    readings = [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9]
    rs = ReadingsWithTimestamp(readings, None) # None for timestamp will use the current time
    rc = ReadingsCollection(rs)

    # Setup some more readings with specific timestamp
    r10 = TemperatureReading(25.3)
    r11 = PressureReading(1005.1)
    r12 = HumidityReading(35.4)
    r13 = LightReading(55.0)
    r14 = AccelerometerReading(0.5, 0.5, 0.5)
    r15 = MagnetometerReading(-0.5, -0.5, -0.5)
    r16 = GyroReading(25.4, 55.7, 85.9)
    r17 = StepsReading(15)
    r18 = HeartrateReading(65)
    r19 = CaloriesReading(15)

    readings1 = [r10, r11, r12, r13, r14, r15, r16, r17, r18, r19]
    lastMinuteTime = time.time() - 60.0
    rs1 = ReadingsWithTimestamp(readings1, lastMinuteTime)
    rc.addReadings(rs1)

    # Add some more readings with specific timestamp
    r20 = TemperatureReading(22.3)
    r21 = PressureReading(1002.1)
    r22 = HumidityReading(32.4)
    r23 = LightReading(52.0)
    readings2 = [r20, r21, r22, r23]
    last10MinuteTime = time.time() - 600.0
    rs2 = ReadingsWithTimestamp(readings2, last10MinuteTime)

    # add single reading
    r24 = AccelerometerReading(0.2, 0.2, 0.2)
    rs2.addReading(r24)

    # add list of readings
    r25 = MagnetometerReading(-0.2, -0.2, -0.2)
    r26 = GyroReading(22.4, 52.7, 82.9)
    r27 = StepsReading(12)
    r28 = HeartrateReading(62)
    r29 = CaloriesReading(12)
    rs2.addReadings([r25, r26, r27, r28, r29])

    rc.addReadings(rs2)

    # Setup MQTT Client for new device
    mqttClient = WolkSenseMQTTClient(newDevice)

    # NOTE:
    # Once we activate a device, we should keep serial and password
    #
    # In order to publish data for already activated device
    # we should instantiate WolkSenseDevice with serial and password we got
    # during activation
    #
    # for example:
    # someDevice = WebAPI.WolkSenseDevice(serial="someSerial", password="somePassword")
    # and then instatiate WolkSenseMQTTClient with someDevice
    # mqttClient = WolkSenseMQTTClient(someDevice)

    # Publish readings
    try:
        print("")
        print("Publishing readings for {0} ...".format(deviceName))
        mqttClient.publishReadings(rc)
    except WolkSenseMQTTClientException as e:
        print("WolkSenseMQTTClientException occured with value: " + e.value)
    else:
        print("Successfully published " + rc.asMQTTString())
        print("--------------------------")
