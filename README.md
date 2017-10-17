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
   device = WolkDevice(device_key, password, serializer, sensors=sensors, actuators=actuators, alarms=alarms)

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

LICENSE
-------

This software is released under the Apache License version 2.0. See LICENSE for details.
