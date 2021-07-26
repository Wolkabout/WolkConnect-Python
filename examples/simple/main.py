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

module_path = os.sep + ".." + os.sep + ".." + os.sep
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + module_path)
import wolk  # noqa

# NOTE: Enable debug logging by uncommenting the following line
# Optionally, as a second argument pass a file name
wolk.logging_config("debug")


def main():
    """Connect to WolkAbout IoT Platform and send a random sensor reading."""
    # Insert the device credentials received
    # from WolkAbout IoT Platform when creating the device
    device = wolk.Device(
        key="danilo_pull_dev",
        password="AIGAYDA51S",
        data_delivery=wolk.DataDelivery.PULL,
    )

    def incoming_feed_value_handler(feed_values):
        for feed_value in feed_values:
            for reference, value in feed_value.items():
                if reference == "timestamp":
                    continue

                if reference == "SL":
                    print("[dummy] setting SL to: " + value)

    wolk_device = wolk.WolkConnect(
        device,
        host="10.0.50.168",
        port=1883,
    ).with_incoming_feed_value_handler(incoming_feed_value_handler)

    # Establish a connection to the WolkAbout IoT Platform
    print("Connecting to WolkAbout IoT Platform")
    wolk_device.connect()

    # NOTE: Connect calls these implicitly
    # wolk_device.pull_parameters()
    # wolk_device.pull_feed_values()

    publish_period_seconds = 45

    while True:
        try:
            slider = random.randint(-20, 80)
            wolk_device.add_feed_value("SL", slider)
            print('Publishing "SL": ' + str(slider))
            wolk_device.publish()
            time.sleep(publish_period_seconds)
        except KeyboardInterrupt:
            print("\tReceived KeyboardInterrupt. Exiting script")
            wolk_device.disconnect()
            sys.exit()


if __name__ == "__main__":
    main()
