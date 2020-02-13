"""Example that covers all the functionality of WolkConnect-Python."""
#   Copyright 2020 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import os
import random
import sys
import time
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union


module_path = os.sep + ".." + os.sep + ".." + os.sep
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + module_path)
import wolk  # noqa

# Enable debug logging by uncommenting the following line
# wolk.logging_config("debug", "wolk.log")


def main():
    """
    Demonstrate all functionality of wolk module.

    Create actuation handler and actuator status provider
    for switch and slider actuators.

    Create configuration handler and configuration provider
    for 4 types of configuration options.

    Create a firmware installer and handler
    for enabling firmware update.

    Pass all of these to a WolkConnect class
    and start a loop to send different types of random readings.
    """
    # Insert the device credentials received
    # from WolkAbout IoT Platform when creating the device
    # List actuator references included on your device
    actuator_references = ["SW", "SL"]
    device = wolk.Device(
        key="device_key",
        password="some_password",
        actuator_references=actuator_references,
    )
    file_management_configuration = {
        "preferred_package_size": 1024 * 1024,
        "max_file_size": 100 * 1024 * 1024,
        "file_directory": "files",
    }
    firmware_version = "1.0"

    class Actuator:
        def __init__(
            self, inital_value: Optional[Union[bool, int, float, str]]
        ):
            self.value = inital_value

    switch = Actuator(False)
    slider = Actuator(0)

    ConfigurationValue = Union[
        bool,
        int,
        Tuple[int, int],
        Tuple[int, int, int],
        float,
        Tuple[float, float],
        Tuple[float, float, float],
        str,
        Tuple[str, str],
        Tuple[str, str, str],
    ]

    configurations: Dict[str, ConfigurationValue] = {
        "config_1": 0,
        "config_2": False,
        "config_3": "configuration_3",
        "config_4": (
            "configuration_4a",
            "configuration_4b",
            "configuration_4c",
        ),
    }

    # Provide a way to read actuator status if your device has actuators
    def actuator_status_provider(
        reference: str,
    ) -> Tuple[wolk.ActuatorState, Optional[Union[bool, int, float, str]]]:
        if reference == actuator_references[0]:
            return wolk.ActuatorState.READY, switch.value
        elif reference == actuator_references[1]:
            return wolk.ActuatorState.READY, slider.value

        return wolk.ActuatorState.ERROR, None

    # Provide an actuation handler if your device has actuators
    def actuation_handler(
        reference: str, value: Union[bool, int, float, str]
    ) -> None:
        print(f"Setting actuator '{reference}' to value: {value}")
        if reference == actuator_references[0]:
            switch.value = value

        elif reference == actuator_references[1]:
            slider.value = value

    # Provide a configuration handler if your device has configuration options
    def configuration_handler(
        configuration: Dict[str, ConfigurationValue]
    ) -> None:
        for reference, value in configuration.items():
            if reference in configurations:
                configurations[reference] = value

    # Provide a way to read current device configuration
    def configuration_provider() -> Dict[str, ConfigurationValue]:
        return configurations

    # Extend this class to handle the installing of the firmware file
    class MyFirmwareHandler(wolk.FirmwareHandler):
        def __init__(self):
            pass

        def install_firmware(self, firmware_file_path: str) -> None:
            """Handle the installing of the firmware file here."""
            print("Installing firmware from path: " + firmware_file_path)
            time.sleep(5)
            sys.exit()

        def get_current_version(self) -> str:
            """Return current firmware version."""
            return firmware_version

    # Pass your device, actuation handler and actuator status provider
    # Pass configuration handler and provider
    # Enable file management by setting setting preferred sizes in bytes
    # Enable firmware update by passing a firmware handler
    wolk_device = wolk.WolkConnect(
        device=device,
        actuation_handler=actuation_handler,
        actuator_status_provider=actuator_status_provider,
        configuration_handler=configuration_handler,
        configuration_provider=configuration_provider,
        file_management_configuration=file_management_configuration,
        firmware_handler=MyFirmwareHandler(),
        host="api-demo.wolkabout.com",
        port=8883,
        ca_cert=".." + os.sep + ".." + os.sep + "wolk" + os.sep + "ca.crt",
    )

    # Establish a connection to the WolkAbout IoT Platform
    print("Connecting to WolkAbout IoT Platform")
    wolk_device.connect()

    wolk_device.publish_configuration()
    wolk_device.publish_actuator_status("SW")
    wolk_device.publish_actuator_status("SL")

    publish_period_seconds = 5

    while True:
        try:
            timestamp = int(round(time.time() * 1000))
            temperature = random.uniform(15, 30)
            humidity = random.uniform(10, 55)
            pressure = random.uniform(975, 1030)
            accelerometer = (
                random.uniform(0, 100),
                random.uniform(0, 100),
                random.uniform(0, 100),
            )
            if humidity > 50:
                # Adds an alarm event to the queue
                wolk_device.add_alarm("HH", True)
            else:
                wolk_device.add_alarm("HH", False)
            # Adds a sensor reading to the queue
            wolk_device.add_sensor_reading("T", temperature, timestamp)
            wolk_device.add_sensor_reading("H", humidity, timestamp)
            wolk_device.add_sensor_reading("P", pressure, timestamp)
            wolk_device.add_sensor_reading("ACL", accelerometer, timestamp)

            # Publishes all sensor readings and alarms from the queue
            # to the WolkAbout IoT Platform
            print("Publishing buffered messages")
            wolk_device.publish()
            time.sleep(publish_period_seconds)
        except KeyboardInterrupt:
            print("\tReceived KeyboardInterrupt. Exiting script")
            wolk_device.publish_device_status(wolk.DeviceState.OFFLINE)
            wolk_device.disconnect()
            sys.exit()


if __name__ == "__main__":
    main()
