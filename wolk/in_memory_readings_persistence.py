"""Persistence for readings that uses local memory (volatile storage)."""
#   Copyright 2023 WolkAbout Technology s.r.o.
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
from time import time
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from wolk import logger_factory
from wolk.interface.message_factory import OutgoingDataTypes
from wolk.interface.message_factory import Reading
from wolk.interface.readings_persistence import ReadingsPersistence


class InMemoryReadingsPersistence(ReadingsPersistence):
    """Persistence for readings that uses local memory (volatile storage)."""

    def __init__(self):  # type: ignore
        """Create the dictionary to store readings."""
        self.dict: Dict[int, Dict[str, OutgoingDataTypes]] = {}
        self.logger = logger_factory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )

    def store_reading(
        self,
        reading: Union[Reading, List[Reading]],
        timestamp: Optional[int] = None,
    ) -> bool:
        """
        Stores the readings from the user in the persistence.

        Groups up with other readings based on the timestamp.

        :param reading: The reading(s) that should be stored in persistence.
        :type reading: Union[Reading, Dict[str, Reading]]
        :param timestamp: The timestamp of when the readings were current.
        :type timestamp: Optional[int]
        :returns: Whether the data was successfully stored.
        :rtype: bool
        """
        self.logger.debug("Storing readings in persistence.")

        # Skip execution if the list is empty
        if isinstance(reading, List) and len(reading) == 0:
            self.logger.warning(
                "Skipping reading storing as the readings list is empty."
            )
            return False

        # Resolve the timestamp if it isn't passed
        timestamp = (
            timestamp if timestamp is not None else round(time() * 1000)
        )

        # If there isn't an entry for the timestamp, create one
        if timestamp not in self.dict.keys():
            self.dict[timestamp] = {}

        # Append all the values into the dictionary
        if isinstance(reading, List):
            for entry in reading:
                self.dict[timestamp][entry[0]] = entry[1]
        else:
            self.dict[timestamp][reading[0]] = reading[1]

        # List out all the members
        return True

    def obtain_readings(self) -> Dict[int, Dict[str, OutgoingDataTypes]]:
        """
        Return everything from the dictionary.

        :returns: The entire content of the reading dictionary.
        :rtype: Dict[int, Dict[str, Reading]]
        """
        return self.dict

    def obtain_readings_count(self) -> int:
        """
        Return count of readings in dictionary.

        :returns: Total count of readings.
        :rtype: int
        """
        count = 0
        for [_, readings] in self.dict.items():
            count += len(readings)
        return count

    def clear_readings(self) -> bool:
        """
        Clears the entire map of readings.

        :returns: Whether the clear was successful.
        :rtype: bool
        """
        self.dict.clear()
        return True
