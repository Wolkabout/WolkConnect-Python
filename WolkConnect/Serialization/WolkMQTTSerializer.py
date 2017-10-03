#   Copyright 2017 WolkAbout Technology s.r.o.
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

import abc
from enum import Enum, unique

class WolkMQTTSerializer(abc.ABC):
    """ Abstract MQTT serializer class
    """
    @abc.abstractmethod
    def serializeToMQTTMessage(self, obj):
        """ Abstract method to serialize obj
        """
        raise NotImplementedError

    @abc.abstractmethod
    def deserializeFromMQTTPayload(self, topic, payload):
        """ Abstract method to deserialize mqtt payload
            to protocol commands
        """
        raise NotImplementedError

    @abc.abstractmethod
    def extractSubscriptionTopics(self, device):
        """ Abstract method to extract subscription topics
            used in mqtt client to subscribe to mqtt broker
        """
        raise NotImplementedError


    def __init__(self, serialNumber, rootReadingsTopic, rootEventsTopic, rootActuatorsPublishTopic, rootActuatorsSubscribeTopic):
        super().__init__()
        self.serialNumber = serialNumber
        self.rootReadingsTopic = rootReadingsTopic
        self.rootEventsTopic = rootEventsTopic
        self.rootActuatorsPublishTopic = rootActuatorsPublishTopic
        self.rootActuatorsSubscribeTopic = rootActuatorsSubscribeTopic

@unique
class WolkCommand(Enum):
    SET = "SET"
    STATUS = "STATUS"

    @classmethod
    def isCommandRecognized(cls, command):
        """ True if command is any of WolkCommand
        """
        try:
            return cls[command] is not None
        except KeyError:
            return False

class WolkMQTTMessage():
    def __init__(self, topic):
        self.topic = topic

    def __str__(self):
        return "WolkMQTTMessage topic={0}".format(self.topic)



class WolkMQTTSubscribeMessage(WolkMQTTMessage):
    def __init__(self, topic, ref, wolkCommand, value=None):
        super().__init__(topic)
        self.ref = ref
        self.wolkCommand = wolkCommand
        self.value = value

    def __str__(self):
        return "WolkMQTTMessage topic={0} ref={1} wolkCommand={2} value={3}".format(self.topic, self.ref, self.wolkCommand, self.value)

class WolkMQTTPublishMessage(WolkMQTTMessage):
    def __init__(self, topic, payload):
        super().__init__(topic)
        self.payload = payload

    def __str__(self):
        return "WolkMQTTMessage topic={0} payload={1}".format(self.topic, self.payload)
