"""Example of registering a new feed and attribute on WolkAbout IoT Platform."""
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
import random
import sys
import time

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


def main() -> None:
    """Connect to WolkAbout IoT Platform and send a random feed reading."""
    # Insert the device credentials received
    # from WolkAbout IoT Platform when creating the device
    device = wolk.Device(key="device_key", password="some_password")

    # Create a WolkConnect object and pass your device
    # NOTE: Change Platform instance with host:str, port:int, ca_cert:str
    wolk_device = wolk.WolkConnect(device)

    # Establish a connection to the WolkAbout IoT Platform
    wolk_device.connect()

    # Example of registering a new feed on the device
    # NOTE: See wolk.Unit and wolk.FeedType for more options.
    wolk_device.register_feed(
        name="New Feed",  # Name that will be displayed on the UI
        reference="NF",  # Per-device unique feed ID
        feed_type=wolk.FeedType.IN,  # uni (IN) or bi-directional feed (In/Out)
        unit=wolk.Unit.NUMERIC,  # Measurement unit for this feed
        # NOTE: Custom instance defined unit can be specified as string
    )

    # Example of registering device attribute
    # NOTE: See wolk.DataType for more options
    wolk_device.register_attribute(
        name="Device activation timestamp",  # Name that will be displayed
        data_type=wolk.DataType.NUMERIC,  # Type of data attribute will hold
        value=str(int(time.time())),  # Value, always sent as string
    )

    publish_period_seconds = 60

    while True:
        try:
            # Generate random value for the newly registered feed
            new_feed = random.randint(0, 100)
            # Add feed value reading of the new feed to message queue
            wolk_device.add_feed_value(("NF", new_feed))
            print(f'Publishing "NF": {new_feed}')
            # Publish queued messages
            wolk_device.publish()
            time.sleep(publish_period_seconds)
        except KeyboardInterrupt:
            print("\tReceived KeyboardInterrupt. Exiting script")
            wolk_device.disconnect()
            return


if __name__ == "__main__":
    main()
