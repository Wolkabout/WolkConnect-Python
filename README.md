```sh

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
WolkAbout Python Connector library for connecting devices to [WolkAbout IoT Platform](https://demo.wolkabout.com/#/login).

Supported device communication protocol(s):
* JsonSingleReferenceProtocol

Prerequisite
------------

* Python 3


Installation
------------

```sh
pip3 install wolk-connect
```

Installing from source
----------------------

This repository must be cloned from the command line using:
```sh
git clone --recurse-submodules https://github.com/Wolkabout/WolkConnect-Python.git
```

Install dependencies by invoking `pip3 install -r requirements.txt`

Install the package by running:
```python
py setup.py install
```

Example Usage
-------------
**Establishing connection with WolkAbout IoT platform:**

Create a device on WolkAbout IoT platform by importing [simple-example-manifest.json](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/simple/simple-example-manifest.json).<br />
This manifest fits [wolk_example.py](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/simple/wolk_example.py) and demonstrates the sending of a temperature sensor reading.

```python
# Setup the device credentials which you received
# when the device was created on the platform
device = wolk.Device(
    key="device_key",
    password="some_password"
)

# Pass your device
wolk_device = wolk.WolkConnect(device)

wolk_device.connect()
```

**Publishing sensor readings:**
```python
wolk_device.add_sensor_reading("T", 26.93)
```

**Data publish strategy:**

Stored sensor readings are pushed to WolkAbout IoT platform on demand by calling:
```python
wolk_device.publish()
```

**Disconnecting from the platform:**
```python
wolk_device.disconnect()
```

**Additional functionality**

WolkConnect-Python library has integrated additional features which can perform full WolkAbout IoT platform potential. Read more about full feature set example [HERE](https://github.com/Wolkabout/WolkConnect-Python/tree/master/examples/full_feature_set).