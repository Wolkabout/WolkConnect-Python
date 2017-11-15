# WolkConnect-Python-

Connector library written in Python3 for WolkAbout platform.

Installation
------------
**Just run standard python dependency script**

 ```sh
    pip3 install -r requirements.txt
 ```

 That will download and install the Paho MQTT library from the web repository. If pip3 is not found, try with `pip` instead of `pip3`.

NOTE:
For WolkSense Sensor Data cloud connectivity please use [this version](https://github.com/Wolkabout/WolkConnect-Python-/releases/tag/WolkSense1.0.0)


Example usage
-------------

Check wolk_example.py for a simple example how to connect a new device and send readings.

**Connecting device**
```sh
    # first setup device credentials which you got when device is created
    device_key = "device_key"
    password = "some_password"
    
    # setup sensors
    temperature = WolkConnect.Sensor("T", WolkConnect.DataType.NUMERIC, minValue=-40.0, maxValue=80.0)
    pressure = WolkConnect.Sensor("P", WolkConnect.DataType.NUMERIC, minValue=900.0, maxValue=1100.0)
    humidity = WolkConnect.Sensor("H", WolkConnect.DataType.NUMERIC, minValue=0.0, maxValue=100.0)
    sensors = [temperature, pressure, humidity]

    # setup actuators
    switch = WolkConnect.Actuator("SW", WolkConnect.DataType.BOOLEAN, value=True)
    slider = WolkConnect.Actuator("SL", WolkConnect.DataType.NUMERIC)
    slider.setValue(20.0)
    actuators = [switch, slider]

    # setup alarms
    humidityHighAlarm = WolkConnect.Alarm("HH", True)
    alarms = [humidityHigh]

    # create device with message handler for actuators
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


    serializer = WolkConnect.WolkSerializerType.JSON_MULTI
    device = WolkConnect.WolkDevice(serial, password, serializer=serializer, responseHandler=mqttMessageHandler, sensors=sensors, actuators=actuators, alarms=alarms)

    device.connect()

```

**Publishing readings**
```sh
    # set sensor values
    # and publish all sensors for the device for the current time
    temperature.setReadingValue(23.4)
    pressure.setReadingValue(999.9)
    humidity.setReadingValue(50.0)
    device.publishSensors(useCurrentTimestamp=True)

    # publish reading value from one sensor with the current time
    temperature.setReadingValue(25.6)
    temperature.setTimestamp(time.time())
    device.publishSensor(temperature)

    # publish raw reading
    # Reference = T, Value = 17.9
    # value is represented as string
    rawTemperature = WolkConnect.RawReading("T", "17.9") 
    device.publishRawReading(rawTemperature)

    # publish random readings for the device (suitable for simulators)
    device.publishRandomReadings()

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

Buffering
---------

Buffers are designed to serve two purposes:
  - collect and store more readings/alarms over time
  - save/load readings to/from persistent storage

Buffers are suitable in situations when internet connectivity is not stable and readings/alarms could not be sent at the time.
Collected readings/alarms may be stored in a buffer and persisted, and when circumstances become favorable, loaded from storage to a buffer and sent to the platform.

Persisting a buffer is not obligatory. All different kind of readings/alarms from the buffer may be sent to the platform at your will.

**Creating a buffer**
```sh
    # create an empty buffer
    wolkBuffer = WolkConnect.WolkReadingsBuffer()

    # create a buffer with list of sensors
    sensors = device.getSensors()
    wolkBuffer = WolkConnect.WolkReadingsBuffer(sensors)

```

**Add sensors and readings to a buffer**
```sh
    # add readings to the buffer
    temperature.setReadingValue(23.4)
    pressure.setReadingValue(999.9)
    humidity.setReadingValue(50.0)
    wolkBuffer.addReadings([temperature, pressure, humidity])

    # add a single reading to the buffer
    temperature.setReadingValue(16.7)
    temperature.setTimestamp(time.time())
    wolkBuffer.addReading(temperature)

    # add a raw reading to the buffer
    rawTemperature = WolkConnect.RawReading("T", 17.9) 
    wolkBuffer.addReading(rawTemperature)

    # add sensors from the device to the buffer 
    # this will add the current reading values of the sensors to the buffer
    sensors = device.getSensors()
    wolkBuffer.addReadings(sensors)
```

**Persisting and loading a buffer**
```sh
    # persist buffer to file
    WolkConnect.serializeBufferToFile(wolkBuffer, "buffer.bfr")

    # create new buffer from file
    newBuffer = WolkConnect.deserializeBufferFromFile("buffer.bfr")
```

**Publish readings from the buffer**
```sh
    # publish readings from buffer
    device.publishBufferedReadings(newBuffer)
```

**Clearing buffer**
```sh
    # clear buffer
    newBuffer.clear()
```

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

    device = WolkConnect.WolkDevice(serial, password, host=custom_host, port=custom_port, certificate_file_path=custom_certificate, set_insecure=trust_my_certificate, serializer=serializer, responseHandler=mqttMessageHandler, sensors=sensors, actuators=actuators, alarms=alarms)
    ...
 ```

**... add new Sensor ?**

 ```sh
    ...

    # Suppose new sensor is defined in the device manifest as:
    # Sensor reference = REF
    # Data type = NUMERIC
    # Data size = 1
    # Minimum = 0.0
    # Maximum = 100.0  

    # Instantiate new sensor
    newSensor = WolkConnect.Sensor("REF", WolkConnect.DataType.NUMERIC, minValue=0.0, maxValue=100.0)
    ...
 ```

**... add new Actuator ?**

 ```sh
    ...

    # Suppose new actuator is defined in the device manifest as:
    # Actuator reference = ACT
    # Data type = NUMERIC

    # Instantiate new actuator
    newActuator = WolkConnect.Actuator("ACT", WolkConnect.DataType.NUMERIC)

    # or
    newActuator = WolkConnect.Actuator("ACT", WolkConnect.DataType.NUMERIC, value=20.0)

    # Set actutor value
    newActuator.setValue(20.0)

    ...
 ```

**... add new Alarm type ?**

 ```sh
    ...

    # Suppose new alarm is defined in the device manifest as:
    # Alarm reference = ALM

    # Instantiate new alarm
    newAlarm = WolkConnect.Alarm("ALM", True)

    ...
 ```

**... send raw readings ?**

 ```sh
    ...

    # If you would like to avoid creating Sensors and Alarms
    # and just want to send raw readings, as pairs of reference and value
    # then do the following

    # Instantiate raw reading    
    rawReading = WolkConnect.RawReading("T", 17.9) # optionally, add timestamp
    
    # publish raw Temperature 17.9
    device.publishRawReading(rawReading)

    ...
 ```


LICENSE
-------

This software is released under the Apache License version 2.0. See LICENSE for details.
