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

**Establishing connection with WolkAbout IoT platform:**

Create a device on WolkAbout IoT Platform by using the *Full example* device type that is available on the platform.
This device type fits [main.py](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/full_feature_set/main.py) and demonstrates all the functionality of WolkConnect-Python library.

```python
import wolk

# Setup device credentials which you got
# when the device was created on the platform
device = wolk.Device(
    key="device_key", password="some_password", actuator_references=["SW", "SL"],
)


# Provide implementation of a way to read actuator status
def actuator_status_provider(reference):
    if reference == actuator_references[0]:
        return (wolk.State.READY, switch.value)
    elif reference == actuator_references[1]:
        return (wolk.State.READY, slider.value)

    return wolk.State.ERROR, None


# Provide implementation of a way to set actuator value
def actuation_handler(reference, value):
    print(f"Setting actuator '{reference}' to value: {value}")
    if reference == actuator_references[0]:
        switch.value = value

    elif reference == actuator_references[1]:
        slider.value = value


# Provide implementation of a way to set configuration values
def configuration_handler(configuration):
    for (reference, value) in configuration.items():
        configurations[reference] = value


# Provide a way to read current device configuration values
def configuration_provider():
    return configurations  # See main.py for details


# Pass your device, actuation handler and actuator status provider
# Pass configuration handler and provider
# Pass server info and path to ca.crt for secure connection
# defaults to secure connection to Demo instance - comment out host, port and ca_cert
wolk_device = (
    wolk.WolkConnect(
        device=device,
        host="api-demo.wolkabout.com",
        port=8883,
        ca_cert="path/to/ca.crt",
    )
    .with_actuators(
        actuation_handler=actuation_handler,
        actuator_status_provider=actuator_status_provider,
    )
    .with_configuration(
        configuration_handler=configuration_handler,
        configuration_provider=configuration_provider,
    )
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

### Adding events

```python
# Activate alarm
wolk_device.add_alarm("HH", True)
# Disable alarm
wolk_device.add_alarm("HH", False)
```

Optionally pass a `timestamp` as `round(time.time()) * 1000`.
This is useful for maintaining data history when readings are not published immediately after adding them to storage.
If `timestamp` is not provided, the library will assign a timestamp before placing the reading into storage.

### Data publish strategy

Stored sensor readings and alarms, as well as current actuator statuses are pushed to WolkAbout IoT platform on demand by calling:
```python
wolk_device.publish()
```

### Publishing actuator statuses

```python
wolk_device.publish_actuator_status("SW")
```
This will call the `actuator_status_provider` to read the actuator status, and publish actuator status.


### Publishing configuration

```python
wolk_device.publish_configuration()
```
This will call the `configuration_provider` to read the current configuration and publish it to the platform


### Disconnecting from the platform

```python
wolk_device.disconnect()
```

### Ping keep-alive service

By default, the library publishes a keep alive message every 60 seconds to the Platform, to update the device's last report for cases when the device doesn't publish data often.
This service can be disabled to reduce bandwidth or battery usage, or the interval can be modified:

```python
wolk_device = wolk.WolkConnect(device=device).with_keep_alive_service(
    enabled=True, interval=60
)
```

Additionally, if this service is enabled and the device establishes connection to the Platform, then each keep alive message sent will be responded with the current UTC timestamp on the Platform.

This timestamp will be saved and updated for each response, and can be accessed with:

```python
platform_timestamp = wolk_device.request_timestamp()
```

### Data persistence

WolkAbout Python Connector provides a mechanism for persisting data in situations where readings can not be sent to WolkAbout IoT platform.

Persisted readings are sent to WolkAbout IoT platform once connection is established.
Data persistence mechanism used **by default** stores data in-memory by using `collections.deque`.

In cases when provided in-file persistence is suboptimal, one can use custom persistence by implementing `MessageQueue`, and forwarding it to the constructor in the following manner:

```python
wolk_device = wolk.WolkConnect(device=device).with_custom_message_queue(
    custom_message_queue
)
wolk_device.connect()
```

For more info on persistence mechanism see `wolk.interface.message_queue.MessageQueue` class


### File management and Firmware update

WolkAbout Python Connector provides a mechanism for updating device firmware.
By default this feature is disabled. Firmware update requires that a file management module is enabled.
See code snippet below on how to enable the file management module and device firmware update.

```python
# Extend this class to handle the installing of the firmware file
class MyFirmwareHandler(wolk.FirmwareHandler):
    def install_firmware(self, firmware_file_path):
        """Handle the installing of the firmware file here."""
        print(f"Installing firmware from path: {firmware_file_path}")
        sys.exit(0)

    def get_current_version(self):
        """Return current firmware version."""
        return "1.0"


# Enable firmware update by passing a firmware handler
wolk_device = (
    wolk.WolkConnect(device=device)
    .with_file_management(
        preferred_package_size=1000 * 1000,
        max_file_size=100 * 1000 * 1000,
        file_directory="files",
    )
    .with_firmware_update(firmware_handler=MyFirmwareHandler())
)
```

File management can also perform downloads from a specified URL,
but if the default implementation is not satisfactory, then this function can be overriden like so:

```python
def url_download(file_url: str, file_path: str) -> bool:
    """
    Download file from specified URL.

    :param file_url: URL from which to download file
    :type file_url: str
    :param file_path: Path where to store file
    :type: file_path: str
    :returns: Successful download
    :rtype: bool
    """
    pass


wolk_device = (
    wolk.WolkConnect(device=device)
    .with_file_management(
        preferred_package_size=1000 * 1000,
        max_file_size=100 * 1000 * 1000,
        file_directory="files",
        custom_url_download=url_download,
    )
```

### Debugging

Logging is enabled by default to info level.

Call the following function to change logging level to:
 * info (default)
 * debug
 * notset

Optionally, specify a log file to which to store logging messages.

```python
# Enable debug logging to file
wolk.logging_config("debug", "wolk.log")
```
