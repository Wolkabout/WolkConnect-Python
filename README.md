```console

██╗    ██╗ ██████╗ ██╗     ██╗  ██╗ ██████╗ ██████╗ ███╗   ██╗███╗   ██╗███████╗ ██████╗████████╗
██║    ██║██╔═══██╗██║     ██║ ██╔╝██╔════╝██╔═══██╗████╗  ██║████╗  ██║██╔════╝██╔════╝╚══██╔══╝
██║ █╗ ██║██║   ██║██║     █████╔╝ ██║     ██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██║        ██║   
██║███╗██║██║   ██║██║     ██╔═██╗ ██║     ██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██║        ██║   
╚███╔███╔╝╚██████╔╝███████╗██║  ██╗╚██████╗╚██████╔╝██║ ╚████║██║ ╚████║███████╗╚██████╗   ██║   
 ╚══╝╚══╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝ ╚═════╝   ╚═╝   
                                                                                                 
                                           ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗ 
                                           ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║ 
                                     █████╗██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║ 
                                     ╚════╝██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║ 
                                           ██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║ 
                                           ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ 
                                                                                                 

```
----
WolkAbout Python Connector library for connecting devices to [WolkAbout IoT Platform](https://demo.wolkabout.com/#/login).

Supported device communication protocols:
* WolkAbout Protocol

## Prerequisite


* Python 3.7
* Python 3.7 pip


## Installation

There are two ways to install this package

### Installing with pip
```console
python3.7 -m pip install wolk-connect
```

### Installing from source

Clone this repository from the command line using:
```console
git clone https://github.com/Wolkabout/WolkConnect-Python.git
```

Install dependencies by invoking `python3.7 -m pip install -r requirements.txt`

Install the package by running:
```console
python3.7 setup.py install
```

## Example Usage

### Establishing connection with WolkAbout IoT platform

Create a device on WolkAbout IoT platform by importing [Simple-example-deviceTemplate.json](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/simple/Simple-example-deviceTemplate.json).<br />
This template fits [main.py](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/simple/main.py) and demonstrates the sending of a temperature sensor reading.

```python
import wolk

# Setup the device credentials which you received
# when the device was created on the platform
device = wolk.Device(key="device_key", password="some_password")

# Pass your device and server information
# defaults to secure connection to Demo instance - comment out host, port and ca_cert
wolk_device = wolk.WolkConnect(
    device, host="api-demo.wolkabout.com", port=8883, ca_cert="path/to/ca.crt"
)

wolk_device.connect()
```

### Adding sensor readings

```python
wolk_device.add_sensor_reading("T", 26.93)

# Multi-value sensor reading
wolk_device.add_sensor_reading("ACL", (4, 2, 0))
```
or multiple sensors at once with `add_sensor_readings`:
```python
wolk_device.add_sensor_readings({"T": 26.93, "ACL": (4, 2, 0)})
```

Optionally pass a `timestamp` as `int(round(time.time() * 1000))`.  
This is useful for maintaining data history when readings are not published immediately after adding them to storage.
If `timestamp` is not provided, the Platform will assign a timestamp once it receives the reading.

### Data publish strategy

Stored sensor readings are pushed to WolkAbout IoT platform on demand by calling:
```python
wolk_device.publish()
```

### Publishing device status

Every time the device publishes data to the Platform it is considered to be in the `CONNECTED` state, so it doesn't need to be sent explicitly.

When the device works on a principle of only connecting periodically to the Platform to publish stored data, then prior to disconnecting from the Platform the device should publish the `SLEEP` state.  
This state is considered as a controlled offline state.

Should the device need to perform any maintenance or any other action during which it would deviate from its default behavior, the device should publish the `SERVICE_MODE` state.  
This state implies that the device is unable to respond to commands issued from the Platform.

If the device is going to terminate its connection to the Platform for an unforeseeable period of time, then the device should send the `OFFLINE` state prior to disconnecting.  

In the case of an unexpected termination of connection to the Platform, the device will be declared offline.

Publishing device status can be done by calling:
```python
wolk_device.publish_device_status(wolk.DeviceState.SLEEP)
```

### Disconnecting from the platform

```python
wolk_device.disconnect()
```

## Additional functionality

WolkConnect-Python library has integrated additional features which can perform full WolkAbout IoT platform potential. Read more about full feature set example [HERE](https://github.com/Wolkabout/WolkConnect-Python/tree/master/examples/full_feature_set).