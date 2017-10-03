""" Initialize WolkConnect
"""
import logging

logger = logging.getLogger(__package__)

def setupLoggingLevel(level=logging.INFO):
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
