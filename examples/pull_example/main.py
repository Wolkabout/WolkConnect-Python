"""Example of a periodically connected device."""
#   Copyright 2021 WolkAbout Technology s.r.o.
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
import sys
import time
from typing import Dict
from typing import List
from typing import Union

try:
    import wolk  # noqa
except ModuleNotFoundError:
    print("Attempting to import wolk package from relative path")
    try:
        module_path = os.sep + ".." + os.sep + ".." + os.sep
        sys.path.append(
            os.path.dirname(os.path.realpath(__file__)) + module_path
        )
        import wolk
    except Exception as e:
        print(f"Failed to import wolk package: '{e}'")
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


def main() -> None:
    """Set up a device with a In/Out feed and periodically connect."""
    # Insert the device credentials received
    # from WolkAbout IoT Platform when creating the device

    # NOTE: Specify that this device has the data delivery type of "PULL"
    # when creating the device, to indicate that the Platform should
    # only send messages to this device when it has been explicitly requested
    device = wolk.Device(
        key="device_key",
        password="some_password",
        data_delivery=wolk.DataDelivery.PULL,
    )

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

    # Create a WolkConnect object and pass your device
    # and specify that this device has an incoming feed value handler
    # NOTE: Change Platform instance with host:str, port:int, ca_cert:str
    wolk_device = wolk.WolkConnect(device).with_incoming_feed_value_handler(
        incoming_feed_value_handler
    )

    # An example of how the function would be called
    # and setting the connection interval to start the loop
    incoming_feed_value_handler([{"SW": False}, {"HB": 120}])

    while True:
        try:
            # NOTE: Upon establishing the connection, the device will also
            # issue pull feed values & pull parameters messages
            wolk_device.connect()

            # Allow some time for responses to come in and then
            # publish current feed values, disconnect and sleep
            time.sleep(heart_beat.value / 10)

            wolk_device.add_feed_value(
                [
                    (switch_feed.reference, switch_feed.value),
                    (heart_beat.reference, heart_beat.value),
                ]
            )
            wolk_device.publish()

            wolk_device.disconnect()
            time.sleep(heart_beat.value * 0.9)
        except KeyboardInterrupt:
            print("\tReceived KeyboardInterrupt. Exiting script")
            wolk_device.disconnect()
            return


if __name__ == "__main__":
    main()
