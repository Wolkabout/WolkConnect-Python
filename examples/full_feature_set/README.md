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

Create a device on WolkAbout IoT Platform by using the *Full example* device type that is available on the platform. Note that device type can be created by importing `full_feature_set.json` file as new Device Type.
This device type fits [main.py](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/full_feature_set/main.py) and demonstrates all the functionality of WolkConnect-Python library.

```python
    # Insert the device credentials received
# from WolkAbout IoT Platform when creating the device
device = wolk.Device(key="device_key", password="some_password")

# Create an InOut feed and define a function that will handle updating its
# value when the appropriate message has been received from the Platform
switch_feed = InOutFeedExample("SW", False)
heart_beat = InOutFeedExample("HB", 120)

def incoming_feed_value_handler(
        feed_values: List[Dict[str, Union[bool, int, float, str]]]
) -> None:
    for feed_value in feed_values:
        for reference, value in feed_value.items():
            if reference == switch_feed.reference:
                print(f"Setting '{reference}' to: {value}")
                switch_feed.value = value
                break

            if reference == heart_beat.reference:
                print(f"Setting '{reference}' to: {value}")
                heart_beat.value = value
                break

            print(f"Unhandled feed value '{reference}': {value}")

# Pass device and optionally connection details
# Enable file management and firmware update via their respective methods
wolk_device = (
    wolk.WolkConnect(device, host="insert_host", port=80, ca_cert="PATH/TO/YOUR/CA.CRT/FILE")
    .with_file_management(
        file_directory="files",
        preferred_package_size=1000,  # NOTE: size in kilobytes
    )
    .with_firmware_update(firmware_handler=DummyFirmwareInstaller())
    .with_incoming_feed_value_handler(incoming_feed_value_handler)
    # NOTE: Possibility to provide custom implementations for some features
    # .with_custom_protocol(message_factory, message_deserializer)
    # .with_custom_connectivity(connectivity_service)
    # .with_custom_message_queue(message_queue)
)
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

### Adding feed values 'separated'

When adding feed values, the values themselves are persisted, which means when publishing all values will be placed
in a single message and published as a single message.

If you would like to ensure different behavior, where you can add feed values that will be sent as a separate message
from any other feed values, use the alternative method:

```python
# Method arguments are exactly the same as for the `add_feed_value`
wolk_device.add_feed_value_separated([("T", 12.34), ("H", 56.78), ("P", 1022.00)], 1658315834000)
```

### Disconnecting from the platform

```python
wolk_device.disconnect()
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
By default, this feature is disabled. Firmware update requires that a file management module is enabled.
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
but if the default implementation is not satisfactory, then this function can be overridden like so:

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
