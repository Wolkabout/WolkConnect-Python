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
from typing import List
from typing import Union

try:
    import wolk  # noqa
except ModuleNotFoundError:
    print("Attempting to import WolkConnect from relative path")
    try:
        module_path = os.sep + ".." + os.sep + ".." + os.sep
        sys.path.append(
            os.path.dirname(os.path.realpath(__file__)) + module_path
        )
        import wolk
    except Exception as e:
        print(f"Failed to import WolkConnect: '{e}'")
        raise e

# NOTE: Enable debug logging by uncommenting the following line
# Optionally, as a second argument pass a file name
# wolk.logging_config("debug")


class InOutFeedExample:
    """
    Holds a value that can be modified.

    Example of a feed that has its own data, as well as the ability
    to set this data to a specified value commanded from the Platform.
    """

    def __init__(
        self, reference: str, initial_value: Union[bool, int, float, str]
    ):
        """Set the value of the feed and store its reference."""
        print(
            f"Initializing InOut feed '{reference}' with value: {initial_value}"
        )
        self.reference = reference
        self.value = initial_value


firmware_version = "5.0"


# Extend this class to handle the installing of the firmware file
class DummyFirmwareInstaller(wolk.FirmwareHandler):
    """Example of a firmware installer implantation."""

    def install_firmware(self, firmware_file_path: str) -> None:
        """Handle the installing of the firmware file here."""
        print(f"Installing firmware from path: {firmware_file_path}")

    def get_current_version(self) -> str:
        """Return current firmware version."""
        return firmware_version


def main() -> None:
    """
    Demonstrate the full use of all Platform enabled devices.

    Includes a random temperature feed, an in/out switch feed,
    an in/out heart beat feed that controls publishing intervals,
    a random generic numeric in feed that has been registered by the device,
    and a registered device attribute that indicates activation time.

    The device also supports file management, reporting the content of
    a specified folder. It accepts commands to remove files or initiate
    a file transfer, either by MQTT packages of a specified size or
    by downloading from the specified URL.
    Provided URL download implementation is achieved using `requests`,
    this function can be overridden if necessary.

    On top of supporting file management, the device also supports firmware
    update capabilities. It will report its current firmware version as a
    part of its parameters update message upon connection. The device
    then complies with commands to attempt to install firmware from a file
    that is present on the device.

    Pass all of these to a WolkConnect class and start a loop.
    """
    # Insert the device credentials received
    # from WolkAbout IoT Platform when creating the device
    device = wolk.Device(key="danilo_dev", password="WPZCH0RLWE")

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
        wolk.WolkConnect(device)
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

    # An example of how the function would be called
    # and setting the connection interval to start the loop
    incoming_feed_value_handler([{"SW": False}, {"HB": 120}])

    # Establish a connection to the WolkAbout IoT Platform
    wolk_device.connect()

    # Example of registering a new feed on the device
    # NOTE: See wolk.Unit and wolk.FeedType for more options.
    wolk_device.register_feed(
        name="New Feed",
        reference="NF",
        feed_type=wolk.FeedType.IN,
        unit=wolk.Unit.NUMERIC,
        # NOTE: Custom instance defined unit can be specified as string
    )

    # Example of registering device attribute
    # NOTE: See wolk.DataType for more options
    wolk_device.register_attribute(
        name="Device activation timestamp",
        data_type=wolk.DataType.NUMERIC,
        value=str(int(time.time())),
    )

    while True:
        try:
            if not wolk_device.connectivity_service.is_connected():
                wolk_device.connect()

            wolk_device.add_feed_value(
                [
                    (switch_feed.reference, switch_feed.value),
                    (heart_beat.reference, heart_beat.value),
                ]
            )
            temperature = random.randint(-20, 80)
            wolk_device.add_feed_value(("T", temperature))
            new_feed = random.randint(0, 100)
            wolk_device.add_feed_value(("NF", new_feed))
            wolk_device.publish()
            time.sleep(heart_beat.value)
        except KeyboardInterrupt:
            print("\tReceived KeyboardInterrupt. Exiting script")
            wolk_device.disconnect()
            return


if __name__ == "__main__":
    main()
