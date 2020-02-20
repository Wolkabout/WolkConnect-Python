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

**Establishing connection with WolkAbout IoT platform:**

Create a device on WolkAbout IoT platform by importing [Full-example-deviceTemplate.json](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/full_feature_set/Full-example-deviceTemplate.json) .<br />
This manifest fits [main.py](https://github.com/Wolkabout/WolkConnect-Python/blob/master/examples/full_feature_set/main.py) and demonstrates all the functionality of WolkConnect-Python library.

```python
import wolk

# Setup device credentials which you got
# when the device was created on the platform
device = wolk.Device(
    key="device_key",
    password="some_password",
    actuator_references=["SW", "SL"],
)


# Provide implementation of a way to read actuator status
def actuator_status_provider(reference):
    if reference == actuator_references[0]:
        return (wolk.ActuatorState.READY, switch.value)
    elif reference == actuator_references[1]:
        return (wolk.ActuatorState.READY, slider.value)

    return wolk.ActuatorState.ERROR, None


# Provide implementation of an actuation handler
def actuation_handler(reference, value):
    print(f"Setting actuator '{reference}' to value: {value}")
    if reference == actuator_references[0]:
        switch.value = value

    elif reference == actuator_references[1]:
        slider.value = value


# Provide implementation of a configuration handler
def configuration_handler(configuration):
    for (reference, value) in configuration.items():
        if reference in configurations:
            configurations[reference] = value


# Provide a way to read current device configuration
def configuration_provider():
    return configurations


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

Optionally pass a `timestamp` as `int(round(time.time() * 1000))`.  
This is useful for maintaining data history when readings are not published immediately after adding them to storage.
If `timestamp` is not provided, the Platform will assign a timestamp once it receives the reading.

### Adding events
```python
# Activate alarm
wolk_device.add_alarm("HH", True)
# Disable alarm
wolk_device.add_alarm("HH", False)
```

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

### Data persistence

WolkAbout Python Connector provides a mechanism for persisting data in situations where readings can not be sent to WolkAbout IoT platform.

Persisted readings are sent to WolkAbout IoT platform once connection is established.
Data persistence mechanism used **by default** stores data in-memory by using `collections.deque`.

In cases when provided in-file persistence is suboptimal, one can use custom persistence by implementing `MessageQueue`, and forwarding it to the constructor in the following manner:

```python
wolk_device = wolk.WolkConnect(
    device=device
).with_custom_message_queue(custom_message_queue)
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
    .with_firmware_update(
        firmware_handler=MyFirmwareHandler()
    )
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
