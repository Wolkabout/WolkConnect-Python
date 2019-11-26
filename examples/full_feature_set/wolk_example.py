#   Copyright 2018 WolkAbout Technology s.r.o.
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
from typing import Dict, Union, Tuple


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
    device = wolk.Device(
        key="device_key",
        password="some_password",
        actuator_references=["SW", "SL"],
    )

    class ActuatorSimulator:
        def __init__(self, inital_value: Union[bool, int, float, str]):
            self.value = inital_value

    switch = ActuatorSimulator(False)
    slider = ActuatorSimulator(0)

    class ConfigurationSimulator:
        def __init__(
            self,
            inital_value: Union[
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
            ],
        ):
            self.value = inital_value

    configuration_1 = ConfigurationSimulator(0)
    configuration_2 = ConfigurationSimulator(False)
    configuration_3 = ConfigurationSimulator("configuration_3")
    configuration_4 = ConfigurationSimulator(
        ("configuration_4a", "configuration_4b", "configuration_4c")
    )

    # Provide a way to read actuator status if your device has actuators
    def get_actuator_status(
        reference: str
    ) -> Tuple[wolk.ActuatorState, Union[bool, int, float, str]]:
        if reference == "SW":
            return wolk.ActuatorState.READY, switch.value
        elif reference == "SL":
            return wolk.ActuatorState.READY, slider.value

    # Provide an actuation handler if your device has actuators
    def handle_actuation(
        reference: str, value: Union[bool, int, float, str]
    ) -> None:
        print("Setting actuator " + reference + " to value: " + str(value))
        if reference == "SW":
            switch.value = value

        elif reference == "SL":
            slider.value = value

    # Provide a configuration handler if your device has configuration options
    def handle_configuration(
        configuration: Dict[
            str, Union[bool, int, float, str]
        ]  # Tuples of size 2 and 3 for int float and str types
    ) -> None:
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
    def get_configuration() -> dict:  # Same types as ConfigurationSimulator
        configuration = dict()
        configuration["config_1"] = configuration_1.value
        configuration["config_2"] = configuration_2.value
        configuration["config_3"] = configuration_3.value
        configuration["config_4"] = configuration_4.value
        return configuration

    # Extend this class to handle the installing of the firmware file
    class MyFirmwareHandler(wolk.FirmwareHandler):
        def __init__(self):
            pass

        def install_firmware(self, firmware_file_path: str) -> None:
            """Handle the installing of the firmware file here."""
            print("Installing firmware from path: " + firmware_file_path)
            os._exit(0)

        def get_current_version(self) -> str:
            """Return current firmware version."""
            return "1.0"

    # Pass your device, actuation handler and actuator status provider
    # Pass configuration handler and provider
    # Enable file management by setting setting preferred sizes in bytes
    # Enable firmware update by passing a firmware handler
    try:
        wolk_device = wolk.WolkConnect(
            device=device,
            actuation_handler=handle_actuation,
            actuator_status_provider=get_actuator_status,
            configuration_handler=handle_configuration,
            configuration_provider=get_configuration,
            file_management=wolk.OSFileManagement(
                preferred_package_size=1024 * 1024,
                max_file_size=100 * 1024 * 1024,
                download_location="downloads",
            ),
            firmware_update=wolk.OSFirmwareUpdate(MyFirmwareHandler()),
            host="api-demo.wolkabout.com",
            port=8883,
            ca_cert=".." + os.sep + ".." + os.sep + "wolk" + os.sep + "ca.crt",
        )
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)

    # Establish a connection to the WolkAbout IoT Platform
    print("Connecting to WolkAbout IoT Platform")
    try:
        wolk_device.connect()
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)

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
            print("Received KeyboardInterrupt, quitting")
            os._exit(0)


if __name__ == "__main__":
    main()
