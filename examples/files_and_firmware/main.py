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
    Demonstrate the file management and firmware update modules.

    Create a firmware installer and handler
    for enabling firmware update.

    Pass all of these to a WolkConnect class and start a loop.
    """
    # Insert the device credentials received
    # from WolkAbout IoT Platform when creating the device
    device = wolk.Device(key="device_key", password="some_password")

    # Pass device and optionally connection details
    # Enable file management and firmware update via their respective methods
    wolk_device = (
        wolk.WolkConnect(device=device)
        .with_file_management(
            file_directory="files",
            preferred_package_size=1000,  # NOTE: in kilobytes
        )
        .with_firmware_update(firmware_handler=DummyFirmwareInstaller())
        # NOTE: Possibility to provide custom implementations for some features
        # .with_custom_protocol(message_factory, message_deserializer)
        # .with_custom_connectivity(connectivity_service)
        # .with_custom_message_queue(message_queue)
    )

    # Establish a connection to the WolkAbout IoT Platform
    print("Connecting to WolkAbout IoT Platform")
    wolk_device.connect()

    publish_period_seconds = 30

    while True:
        try:
            if not wolk_device.connectivity_service.is_connected():
                wolk_device.connect()

            print("Publishing buffered messages")
            wolk_device.publish()
            time.sleep(publish_period_seconds)
        except KeyboardInterrupt:
            print("\tReceived KeyboardInterrupt. Exiting script")
            wolk_device.disconnect()
            return


if __name__ == "__main__":
    main()
