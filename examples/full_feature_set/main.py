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
import json
import os
import random
import sys
import time
from traceback import print_exc
from typing import Dict
from typing import Optional
from typing import Union

import requests


module_path = os.sep + ".." + os.sep + ".." + os.sep
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + module_path)
import wolk  # noqa

# Enable debug logging by uncommenting the following line
# wolk.logging_config("debug", "wolk.log")

firmware_version = "1.0"
configuration_file = "configuration.json"
configurations = {}

ConfigurationValue = Union[
    bool,
    int,
    float,
    str,
]


def configuration_handler(
    configuration: Dict[str, ConfigurationValue]
) -> None:
    """Provide a way to read device's configuration options."""
    global configurations
    try:
        with open(configuration_file, "r+", encoding="utf-8") as handle:
            stored = json.load(handle)
            for key, value in configuration.items():
                for stored_key, stored_value in stored.items():
                    if stored_key != key:
                        continue

                    if stored[stored_key] == value:
                        continue
                    if isinstance(value, str):
                        if "," in value:
                            if isinstance(stored_value, list):
                                stored_value = ",".join(value)
                                continue
                    stored_value = value

            handle.seek(0)
            json.dump(stored, handle, indent=4)
            handle.truncate()
            configurations = stored.copy()
    except Exception:
        print(
            "Error occurred when handling configuration"
            f" with file {configuration_file}"
        )
        print_exc()


def configuration_provider() -> Dict[str, ConfigurationValue]:
    """Provide a way to set device's configuration options."""
    with open(configuration_file, "r+", encoding="utf-8") as handle:
        loaded = json.load(handle)
        configurations: Dict[str, ConfigurationValue] = {}
        for reference, value in loaded.items():
            if isinstance(value, list):
                if len(value) == 0:
                    configurations.update({reference: []})
                elif isinstance(value[0], str):
                    value = ",".join(value)

            configurations.update({reference: value})

        return configurations


def main() -> None:
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
    # TODO: Update this example
    print("TODO: Update this example")
    return

    # Insert the device credentials received
    # from WolkAbout IoT Platform when creating the device
    device = wolk.Device(key="device_key", password="some_password")
    try:
        global configurations
        with open(configuration_file) as file:
            configurations = json.load(file)
        wolk.logging_config(configurations["LL"])  # Log level
    except Exception:
        print(
            "Failed load configuration options "
            f"from file '{configuration_file}'"
        )
        print_exc()
        raise RuntimeError

    class InOutFeed:
        def __init__(
            self, inital_value: Optional[Union[bool, int, float, str]]
        ):
            self.value = inital_value

    # The URL download implementation can be substituted
    # This is optional and passed as an argument when creating wolk_device
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
        response = requests.get(file_url)
        with open(file_path, "ab") as file:
            file.write(response.content)
            file.flush()
            os.fsync(file)  # type: ignore

        return os.path.exists(file_path)

    # Extend this class to handle the installing of the firmware file
    class MyFirmwareHandler(wolk.FirmwareHandler):
        def install_firmware(self, firmware_file_path: str) -> None:
            """Handle the installing of the firmware file here."""
            print(f"Installing firmware from path: {firmware_file_path}")
            time.sleep(5)
            sys.exit()

        def get_current_version(self) -> str:
            """Return current firmware version."""
            return firmware_version

    # Pass device and optionally connection details
    # Provided connection details are the default value
    # Provide actuation handler and actuator status provider via with_actuators
    # Provide configuration provider/handler via with_configuration
    # Enable file management and firmware update via their respective methods
    wolk_device = (
        wolk.WolkConnect(
            device=device,
            host="api-demo.wolkabout.com",
            port=8883,
            ca_cert=".." + os.sep + ".." + os.sep + "wolk" + os.sep + "ca.crt",
        )
        .with_file_management(
            preferred_package_size=1000 * 1000,
            max_file_size=100 * 1000 * 1000,
            file_directory="files",
            custom_url_download=url_download,
        )
        .with_firmware_update(firmware_handler=MyFirmwareHandler())
        # Possibility to provide custom implementations for some features
        # .with_custom_protocol(message_factory, message_deserializer)
        # .with_custom_connectivity(connectivity_service)
        # .with_custom_message_queue(message_queue)
    )

    # Establish a connection to the WolkAbout IoT Platform
    print("Connecting to WolkAbout IoT Platform")
    wolk_device.connect()

    publish_period_seconds = configurations["HB"]  # Heart beat

    while True:
        try:
            if wolk_device.connectivity_service.is_connected():
                timestamp = round(time.time()) * 1000
                # If unable to get system time use:
                # timestamp = wolk_device.request_timestamp()
                temperature = random.uniform(15, 30)
                humidity = random.uniform(10, 55)
                pressure = random.uniform(975, 1030)

                # Enabled feeds
                if "T" in configurations["EF"]:
                    wolk_device.add_sensor_reading("T", temperature, timestamp)
                if "H" in configurations["EF"]:
                    wolk_device.add_sensor_reading("H", humidity, timestamp)
                    if humidity > 50:
                        # Adds an alarm event to the queue
                        wolk_device.add_alarm("HH", True)
                    else:
                        wolk_device.add_alarm("HH", False)
                if "P" in configurations["EF"]:
                    wolk_device.add_sensor_reading("P", pressure, timestamp)

            else:
                wolk_device.connect()

            # Publishes all sensor readings and alarms from the queue
            # to the WolkAbout IoT Platform
            print("Publishing buffered messages")
            wolk_device.publish()
            publish_period_seconds = configurations["HB"]
            time.sleep(publish_period_seconds)
        except KeyboardInterrupt:
            print("\tReceived KeyboardInterrupt. Exiting script")
            wolk_device.disconnect()
            sys.exit()


if __name__ == "__main__":
    main()
