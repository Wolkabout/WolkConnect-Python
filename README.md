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
[![Build Status](https://travis-ci.com/Wolkabout/WolkConnect-Python.svg?branch=master)](https://travis-ci.com/Wolkabout/WolkConnect-Python) [![PyPI version](https://badge.fury.io/py/wolk-connect.svg)](https://badge.fury.io/py/wolk-connect) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wolk-connect) ![GitHub](https://img.shields.io/github/license/wolkabout/WolkConnect-Python) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/) [![Documentation Status](https://readthedocs.org/projects/wolkconnect-python/badge/?version=latest)](https://wolkconnect-python.readthedocs.io/en/latest/?badge=latest)
----
WolkAbout Python Connector library for connecting devices to [WolkAbout IoT Platform](https://demo.wolkabout.com/#/login).

Supported device communication protocols:
* WolkAbout Protocol

## Prerequisite


* Python 3.7+


## Installation

There are two ways to install this package

### Installing with pip
```console
python3 -m pip install wolk-connect
```

### Installing from source

Clone this repository from the command line using:
```console
git clone https://github.com/Wolkabout/WolkConnect-Python.git
```

Install dependencies by invoking `python3 -m pip install -r requirements.txt`

Install the package by running:
```console
python3 setup.py install
```

## Example Usage

### Establishing connection with WolkAbout IoT platform

Create a device on WolkAbout IoT Platform by using the *Simple example* device type that is available on the platform.
This device type fits [main.py](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/simple/main.py) and demonstrates the periodic sending of a temperature sensor reading.

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

Optionally pass a `timestamp` as `round(time.time()) * 1000`.
This is useful for maintaining data history when readings are not published immediately after adding them to storage.
If `timestamp` is not provided, the library will assign a timestamp before placing the reading into storage.


### Data publish strategy

Stored sensor readings are pushed to WolkAbout IoT platform on demand by calling:
```python
wolk_device.publish()
```

### Disconnecting from the platform

```python
wolk_device.disconnect()
```

## Additional functionality

WolkConnect-Python library has integrated additional features which can perform full WolkAbout IoT platform potential. Read more about full feature set example [HERE](https://github.com/Wolkabout/WolkConnect-Python/tree/master/examples/full_feature_set).
