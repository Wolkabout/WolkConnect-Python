
#   Copyright 2016 WolkAbout Technology s.r.o.
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

import http.client
import json

class WolkSenseDevice:
    """ WolkSenseDevice class
    """

    def __init__(self, name = "", serial = "", password=""):
        self.name = name
        self.serial = serial
        self.password = password
        self.publishTopic = "sensors/" + serial

class WolkSenseWebClientException(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

class WolkSenseWebClient:
    """ WolkSenseWebClient class
    """

    HTTP_OK = 200
    HTTP_UNAUTHORIZED = 401
    HTTP_CONFLICT = 409
    WolkSenseWebAPIBaseURL = "api.wolksense.com"

    @classmethod
    def getAccessToken(cls, userEmail, userPassword):
        """ Get access token for WolkSense user. userEmail and userPassword are WolkSense credentials
            Returned accessToken should be used for subsequent calls to web api.
        """

        conn = http.client.HTTPSConnection(cls.WolkSenseWebAPIBaseURL)
        payload = '{"email":"' + userEmail + '","password":"' + userPassword + '"}'

        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        conn.request("POST", "/api/signIn", payload, headers)

        res = conn.getresponse()
        if res.status == cls.HTTP_UNAUTHORIZED:
            raise WolkSenseWebClientException("Wrong credentials")
        elif res.status != cls.HTTP_OK:
            raise WolkSenseWebClientException("Error authenticating user")


        data = res.read()
        return cls._getValueForKeyFromJSON(data, 'accessToken')

    @classmethod
    def getRandomSerial(cls, accessToken):
        """ Returns randomly generated serial number which should be used
            for device activation
        """

        conn = http.client.HTTPSConnection(cls.WolkSenseWebAPIBaseURL)

        headers = {
            'authorization': accessToken,
            'cache-control': "no-cache"
        }

        conn.request("GET", "/api/v3/devices/random_serial", headers=headers)

        res = conn.getresponse()
        if res.status == cls.HTTP_UNAUTHORIZED:
            raise WolkSenseWebClientException("User is not authorized to get a random serial for device")
        elif res.status != cls.HTTP_OK:
            raise WolkSenseWebClientException("Error getting random serial for device")

        data = res.read()
        return cls._getValueForKeyFromJSON(data, 'serial')

    @classmethod
    def activateDevice(cls, deviceName, deviceSerial, accessToken):
        """ Activates device with deviceName and deviceSerial.
            Upon activation a password is returned.
            The password will be used in client authentication on mqtt broker (for specified deviceSerial)
        """

        conn = http.client.HTTPSConnection(cls.WolkSenseWebAPIBaseURL)

        payload = '{"name":"' + deviceName + '"}'

        headers = {
            'content-type': "application/json",
            'authorization': accessToken,
            'cache-control': "no-cache"
        }

        conn.request("POST", "/api/v2/devices/{0}".format(deviceSerial), payload, headers)

        res = conn.getresponse()
        if res.status == cls.HTTP_UNAUTHORIZED:
            raise WolkSenseWebClientException("User is not authorized to activate device")
        elif res.status == cls.HTTP_CONFLICT:
            raise WolkSenseWebClientException("Device with name '{0}' already exists.".format(deviceName))
        elif res.status != cls.HTTP_OK:
            raise WolkSenseWebClientException("Error activating device")

        data = res.read()
        return cls._getValueForKeyFromJSON(data, 'password')

    @classmethod
    def _getValueForKeyFromJSON(cls, data, key):
        if data is None:
            return None

        jsonString = data.decode("utf-8")

        dict = json.loads(jsonString)
        value = dict.get(key)
        if value is None:
            raise WolkSenseWebClientException("Internal error. No value for key:" + key)

        return value

    @classmethod
    def activateDeviceForUser(cls, userEmail, userPassword, deviceName, deviceSerial = ""):
        """ Activates a new device (with deviceName) for WolkSense user
            (whose credentials are userEmail and userPassword)
            If deviceSerial is empty, a new serial will be generated and assigned to
            activated device
        """

        if not userEmail:
            raise WolkSenseWebClientException("userEmail is mandatory")

        if not userPassword:
            raise WolkSenseWebClientException("userPassword is mandatory")

        if not deviceName:
            raise WolkSenseWebClientException("deviceName is mandatory")

        at = cls.getAccessToken(userEmail, userPassword)
        if at is None:
            raise WolkSenseWebClientException("Wrong credentials, please try again")

        if not deviceSerial:
            serial = cls.getRandomSerial(at)
            if serial is None:
                raise WolkSenseWebClientException("Device could not be activated because serial number is not generated. Please try again.")

        password = cls.activateDevice(deviceName, serial, at)
        if password is None:
            raise WolkSenseWebClientException("Device not activated")

        return WolkSenseDevice(deviceName, serial, password)
