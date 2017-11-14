""" Initialize WolkConnect
"""
import logging
from WolkConnect.Actuator import Actuator, ActuatorState, ActuationException
from WolkConnect.Alarm import Alarm
from WolkConnect.ReadingType import DataType, RawReading
from WolkConnect.Sensor import Sensor, ReadingsWithTimestamp, ReadingsCollection
from WolkConnect.WolkDevice import WolkDevice
from WolkConnect.Serialization.WolkMQTTSerializer import WolkMQTTSubscribeMessage, WolkSerializerType, WolkCommand
from WolkConnect.Serialization.WolkBufferSerialization import WolkAlarmsBuffer, WolkReadingsBuffer, serializeBufferToFile, deserializeBufferFromFile


logger = logging.getLogger(__package__)

def setupLoggingLevel(level=logging.INFO):
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
