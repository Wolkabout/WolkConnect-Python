"""Minimal example of periodically sending data to WolkAbout IoT Platform."""
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
    wolk_device = wolk.WolkConnect(device, host="insert_host", port=80, ca_cert="PATH/TO/YOUR/CA.CRT/FILE")

    # Establish a connection to the WolkAbout IoT Platform
    wolk_device.connect()

    publish_period_seconds = 60

    while True:
        try:
            # Generate a random value
            temperature = random.randint(-20, 80)

            # Add a feed reading to the message queue
            wolk_device.add_feed_value(("T", temperature))

            print(f'Publishing "T": {temperature}')
            wolk_device.publish()
            time.sleep(publish_period_seconds)
        except KeyboardInterrupt:
            print("\tReceived KeyboardInterrupt. Exiting script")
            wolk_device.disconnect()
            return


if __name__ == "__main__":
    main()
