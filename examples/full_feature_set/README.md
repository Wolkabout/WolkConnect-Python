# WolkConnect-Python
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

Create a device on WolkAbout IoT platform by importing [full-example-manifest.json](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/full_feature_set/full-example-manifest.json) .<br />
This manifest fits [wolk_example.py](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/full_feature_set/wolk_example.py) and demonstrates all the functionality of WolkConnect-Python library.

```python
# Setup device credentials which you got
# when the device was created on the platform
device = wolk.Device(
    key="device_key",
    password="some_password",
    actuator_references=["ACTUATOR_REFERENCE_ONE", "ACTUATOR_REFERENCE_TWO"]
)

# Provide implementation of a way to read actuator status
class ActuatorStatusProviderImpl(wolk.ActuatorStatusProvider):
    def get_actuator_status(self, reference):
        if reference == "ACTUATOR_REFERENCE_ONE":
            return wolk.ACTUATOR_STATE_READY, actuator_1.value
        elif reference == "ACTUATOR_REFERENCE_TWO":
            return wolk.ACTUATOR_STATE_READY, actuator_2.value


# Provide implementation of an actuation handler
class ActuationHandlerImpl(wolk.ActuationHandler):
    def handle_actuation(self, reference, value):
        print("Setting actuator " + reference + " to value: " + str(value))
        if reference == "ACTUATOR_REFERENCE_ONE":
            actuator_1.value = value

        elif reference == "ACTUATOR_REFERENCE_TWO":
            actuator_2.value = value

# Provide implementation of a configuration handler
class ConfigurationHandlerImpl(wolk.ConfigurationHandler):

    def handle_configuration(self, configuration):
        for key, value in configuration.items():
            if key == "config_1":
                configuration_1.value = value
            elif key == "config_2":
                configuration_2.value = value
            elif key == "config_3":
                configuration_3.value = value
            elif key == "config_4":
                configuration_4.value = value

# Provide a way to read current device configuration
class ConfigurationProviderImpl(wolk.ConfigurationProvider):

    def get_configuration(self):
        configuration = dict()
        configuration['config_1'] = configuration_1.value
        configuration['config_2'] = configuration_2.value
        configuration['config_3'] = configuration_3.value
        configuration['config_4'] = configuration_4.value
        return configuration

# Pass your device, actuation handler and actuator status provider
# Pass configuration handler and provider
wolk_device = wolk.WolkConnect(
    device=device,
    actuation_handler=ActuationHandlerImpl(),
    actuator_status_provider=ActuatorStatusProviderImpl(),
    configuration_handler=ConfigurationHandlerImpl(),
    configuration_provider=ConfigurationProviderImpl()
)

wolk_device.connect()
```

**Publishing sensor readings:**
```python
wolk_device.add_sensor_reading("T", 26.93)

# Multi-value sensor reading
wolk_device.add_sensor_reading("ACL", (4, 2, 0))
```

**Publishing events:**
```python
# Activate alarm
wolk_device.add_alarm("ALARM_REFERENCE", True)
# Disable alarm
wolk_device.add_alarm("ALARM_REFERENCE", False)
```

**Publishing actuator statuses:**
```python
wolk_device.publish_actuator_status("ACTUATOR_REFERENCE_ONE")
```
This will call the `ActuatorStatusProvider` to read the actuator status, and publish actuator status.


**Publishing configuration**
```python
wolk_device.publish_configuration()
```
This will call the `ConfigurationProvider` to read the current configuration and publish it to the platform


**Data publish strategy:**

Stored sensor readings and alarms, as well as current actuator statuses are pushed to WolkAbout IoT platform on demand by calling:
```python
wolk_device.publish()
```

Whereas actuator statuses are published automatically by calling:

```python
wolk_device.publish_actuator_status("ACTUATOR_REFERENCE_ONE")
```

**Disconnecting from the platform:**
```python
wolk_device.disconnect()
```

**Data persistence:**

WolkAbout Python Connector provides a mechanism for persisting data in situations where readings can not be sent to WolkAbout IoT platform.

Persisted readings are sent to WolkAbout IoT platform once connection is established.
Data persistence mechanism used **by default** stores data in-memory by using `collections.deque`.

In cases when provided in-file persistence is suboptimal, one can use custom persistence by implementing `OutboundMessageQueue`, and forwarding it to the constructor in the following manner:

```python
wolk_device = wolk.WolkConnect(
    device=device,
    actuation_handler=ActuationHandlerImpl(),
    actuator_status_provider=ActuatorStatusProviderImpl(),
    outbound_message_queue=custom_queue
)
wolk_device.connect()
```

For more info on persistence mechanism see `OutboundMessageQueue` class


**Firmware update:**

WolkAbout Python Connector provides a mechanism for updating device firmware.
By default this feature is disabled. See code snippet below on how to enable device firmware update.

```python
# Extend this class to handle the installing of the firmware file
class MyFirmwareInstaller(wolk.FirmwareInstaller):

    def __init__(self):
        pass

    def install_firmware(self, firmware_file_path):
        """
        Handle the installing of the firmware file here
        """
        print("Updating firmware with file '{}'".format(firmware_file_path))
        # Handle the installation process


# Enable firmware update on your device
# Implement wolk.FirmwareURLDownloadHandler to enable URL download
firmware_handler = wolk.FileSystemFirmwareHandler(
    version="1.0",
    chunk_size=1024 * 1024,
    max_file_size=100 * 1024 * 1024,
    download_location='',
    firmware_installer=MyFirmwareInstaller(),
    firmware_url_download_handler=None
)

# Pass your device, actuation handler and actuator status provider
# Enable firmware update by passing a firmware handler
wolk_device = wolk.WolkConnect(
    device=device,
    actuation_handler=ActuationHandlerImpl(),
    actuator_status_provider=ActuatorStatusProviderImpl(),
    firmware_handler=firmware_handler
)
```

**Keep Alive Mechanism:**

WolkAbout Python Connector by default uses Keep Alive mechanism to notify WolkAbout IoT Platform that device is still connected. Keep alive message is sent to WolkAbout IoT Platform every 10 minutes.

To reduce network usage Keep Alive mechanism can be disabled in following manner:

```python
wolk_device = wolk.WolkConnect(
    device=device,
    actuation_handler=ActuationHandlerImpl(),
    actuator_status_provider=ActuatorStatusProviderImpl(),
    keep_alive_enabled=False
)
```

**Debugging:**
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
