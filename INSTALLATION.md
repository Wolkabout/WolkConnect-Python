# Preconditions

- To use example you need a WolkSense account. You can create one at https://wolksense.com
- Make sure that python3 is installed on your computer.

# Installation guide

1. install paho mqtt client in your terminal type:

 ```
    pip3 install paho-mqtt
 ```

 That will download paho library from the web repository and install in your computer. If you can't install paho with the previous command, try with `pip` instead of `pip3`.

 If pip installation fails, download the source code from https://pypi.python.org/pypi/paho-mqtt/1.1, extract it and in the terminal navigate to folder where paho-mqtt is extracted. Then type

 ```
    python3 setup.py install
 ```

2. open script example.py in editor
	- in the script set proper `userEmail`, `userPassword` and `deviceName` (lines 10-12)

    * userEmail and userPassword are WolkSense credentials,
    * deviceName will be name of the device that will be activated on WolkSense platform

3. login to https://wolksense.com and switch to 'Readings' tab


4. run python script:
 ```
     python3 example.py
```

5. upon successful execution you should see new device and new readings on https://wolksense.com
