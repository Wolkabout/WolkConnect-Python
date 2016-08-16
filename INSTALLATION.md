# Preconditions

- You need a WolkSense account. You can create one at https://wolksense.com
- Make sure that python3 is installed on your computer.

# Installation guide

1. install paho mqtt client in your terminal.

 ```
    pip3 install paho-mqtt
 ```

 That will download the Paho MQTT library from the web repository and install it in your computer. If pip3 is not found, try with `pip` instead of `pip3`.

 To install manually, you can download the source code from https://pypi.python.org/pypi/paho-mqtt/1.1, extract it and in the terminal navigate to folder where paho-mqtt is extracted. Then type

 ```
    python3 setup.py install
 ```
 again if `python3` is not found, try `python` instead

2. Open example.py in a text editor
	- enter your own credentials for `userEmail`, `userPassword` and `deviceName` (lines 10-12)
    * userEmail and userPassword are WolkSense credentials,
    * deviceName will be name of the device that will be activated on WolkSense platform

3. login to https://wolksense.com and switch to 'Readings' tab


4. run python script:
 ```
     python3 example.py
```

5. upon successful execution you should see new device and new readings on https://wolksense.com
