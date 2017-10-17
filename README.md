# WolkConnect-Python-

Connector library written in Python for WolkAbout platform.

Installation
------------
**Just run standard python dependency script**

 ```sh
    pip3 install -r requirements.txt
 ```

 That will download and install the Paho MQTT library from the web repository. If pip3 is not found, try with `pip` instead of `pip3`.


Example usage
-------------

Check wolk_example.py for a simple example how to connect a new device and send readings.

**Connecting device**
```sh
   # first setup device credentials which you got when device is created
   device_key = "device_key"
   password = "some_password"

   # setup sensors
   temperature = TemperatureReading()
   pressure = PressureReading()
   humidity = HumidityReading()
   sensors = [temperature, pressure, humidity]

   # setup actuators
   switch = SwitchActuator(0)
   slider = SliderActuator(20.0)
   actuators = [switch, slider]

   # setup alarms
   humidityHigh = HumidityHighAlarm(True)
   alarms = [humidityHigh]

   # create device
   serializer = WolkMQTTSerializer.WolkSerializerType.JSON_MULTI
   device = WolkDevice.WolkDevice(serial, password, serializer=serializer, sensors=sensors, actuators=actuators, alarms=alarms)

   device.connect()

```

**Publishing readings**
```sh
   # publish readings for all device sensors
   device.publishAllReadings()
   
   # publish one reading
   temperature.setReadingValue(25.6)
   device.publishReading(temperature)

   # publish more readings
   temperature.setReadingValue(26.7)
   pressure.setReadingValue(999.9)
   device.publishReadings([temperature, pressure])
```

**Publishing alarm**
```sh
   # publish alarm
   humidityHigh.setAlarm()
   device.publishAlarm(humidityHigh)
```

**Disconnect device**
```sh
   device.disconnect()
```

NOTE:
For WolkSense Sensor Data cloud connectivity please use [this version](https://github.com/Wolkabout/WolkConnect-Python-/releases/tag/WolkSense1.0.0)

HOW to ...
------------
**... set custom host, port and certificate for MQTT broker ?**

 ```sh
   ...
   # set custom host and port
   custom_host = "my.custom.host"
   custom_port = 12345
   # set custom certificate
   custom_certificate = "path/to/custom/certificate/file/ca.crt"
   trust_my_certificate = True # use this if certificate is not signed by a trusted authority but you want to trust it. (e.g. certificate is self signed)

   device = WolkDevice.WolkDevice(serial, password, host=custom_host, port=custom_port, certificate_file_path=custom_certificate, set_insecure=trust_my_certificate, sensors=sensors, actuators=actuators, alarms=alarms)
   ...
 ```

**... add new Sensor type ?**

 ```sh
   ...

   # Suppose new sensor is defined in the device manifest as:
   # Sensor reference = REF
   # Data type = NUMERIC
   # Data size = 1
   # Minimum = 0.0
   # Maximum = 100.0  

   # Edit Sensor.py and add new entry in SensorType enumeration

   NEW_SENSOR = ("REF", ReadingType.DataType.NUMERIC, 0.0, 100.0)

   # Add new class in Sensor.py

   class NewSensor(Reading):
   """ New Sensor
   """
   def __init__(self, newSensorValue=None, timestamp=None):
      super().__init__(SensorType.NEW_SENSOR, [newSensorValue], 1.0, timestamp)

   # Instantiate new sensor

   newSensor = Sensor.NewSensor()
   ...
 ```

**... add new Actuator type ?**

 ```sh
   ...

   # Suppose new actuator is defined in the device manifest as:
   # Actuator reference = ACT
   # Data type = NUMERIC
   # Data size = 1
   # Minimum = 0.0
   # Maximum = 100.0  

   # Edit Actuator.py and add new entry in ActuatorType enumeration

   NEW_ACTUATOR = ("ACT", DataType.NUMERIC, ActuatorState.READY)

   # Add new class in Actuator.py

   class NewActuator(Actuator):
   """ New Actuator
   """
   def __init__(self, newActuatorValue):
      super().__init__(ActuatorType.NEW_ACTUATOR, newActuatorValue)

   # Instantiate new actuator

   newActuator = Actuator.NewActuator()
   ...
 ```

**... add new Alarm type ?**

 ```sh
   ...

   # Suppose new alarm is defined in the device manifest as:
   # Alarm reference = ALM

   # Edit Alarm.py and add new entry in AlarmType enumeration

   NEW_ALARM = ("ALM", DataType.BOOLEAN)

   # Add new class in Alarm.py

   class NewAlarm(Alarm):
       """ New alarm
       """
       def __init__(self, isSet=False):
          super().__init__(AlarmType.NEW_ALARM, isSet)

   # Instantiate new alarm

   newAlarm = Alarm.NewAlarm(True)
   ...
 ```



LICENSE
-------

This software is released under the Apache License version 2.0. See LICENSE for details.
