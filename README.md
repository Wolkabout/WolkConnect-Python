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
[![Tests and Coverage](https://github.com/Wolkabout/WolkConnect-Python/actions/workflows/tests-and-coverage.yml/badge.svg?branch=development)](https://github.com/Wolkabout/WolkConnect-Python/actions/workflows/tests-and-coverage.yml) [![PyPI version](https://badge.fury.io/py/wolk-connect.svg)](https://badge.fury.io/py/wolk-connect) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wolk-connect) ![GitHub](https://img.shields.io/github/license/wolkabout/WolkConnect-Python) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/) [![Documentation Status](https://readthedocs.org/projects/wolkconnect-python/badge/?version=latest)](https://wolkconnect-python.readthedocs.io/en/latest/?badge=latest)
----
WolkAbout Python Connector library for connecting devices to WolkAbout IoT platform instance.

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

Create a device on WolkAbout IoT Platform by using the *Simple example* device type that is available on the platform. ``Note that device type can be created by importing `simple_example.json` file as new Device Type.``
This device type fits [main.py](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/simple/main.py) and demonstrates the periodic sending of a temperature feed reading.

```python
import wolk

# Setup the device credentials which you received
# when the device was created on the platform
device = wolk.Device(key="device_key", password="some_password")

# Pass your device and server information
# defaults to secure connection to Demo instance - comment out host, port and ca_cert
wolk_device = wolk.WolkConnect(
    device, host="insert_host", port=80, ca_cert="PATH/TO/YOUR/CA.CRT/FILE"
)

wolk_device.connect()
```

### Adding feed values

```python
wolk_device.add_feed_value(("T", 26.93))

# or multiple feed value readings
wolk_device.add_feed_value([("T", 27.11), ("H", 54.34), ("P", 1002.3)])
```

Optionally pass a `timestamp` as `round(time.time()) * 1000`.
This is useful for maintaining data history when readings are not published immediately after adding them to storage.
If `timestamp` is not provided, the library will assign a timestamp before placing the reading into storage.

#### Adding feed values with timestamp
```python
# Add a signel feed reading to the message queue with the timestamp
wolk_device.add_feed_value(("T", 12.34), 1658315834000)

# Add a multi feed reading to the message queue with the timestamp
wolk_device.add_feed_value([("T", 12.34), ("H", 56.78), ("P", 1022.00)], 1658315834000)
```

### Data publish strategy

Stored feed values are pushed to WolkAbout IoT platform on demand by calling:
```python
wolk_device.publish()
```

### Disconnecting from the platform

```python
wolk_device.disconnect()
```

## Additional functionality

WolkConnect-Python library has integrated additional features which can perform full WolkAbout IoT platform potential. Explore the [examples](https://github.com/Wolkabout/WolkConnect-Python/tree/master/examples/) for more information.
