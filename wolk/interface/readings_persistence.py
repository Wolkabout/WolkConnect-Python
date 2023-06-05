"""Persistence storing readings for grouped publishing."""
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
from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from wolk.interface.message_factory import OutgoingDataTypes
from wolk.interface.message_factory import Reading


class ReadingsPersistence(ABC):
    """Persistence storing readings for grouped publishing."""

    @abstractmethod
    def store_reading(
        self,
        reading: Union[Reading, List[Reading]],
        timestamp: Optional[int] = None,
    ) -> bool:
        """
        Store the reading in persistence.

        :param reading: The reading(s) that should be added into persistence for specific timestamp.
        :type reading: Union[Reading, List[Reading]]
        :param timestamp: The time at which these readings were current/up-to-date data.
        :type timestamp: Optional[int]
        :returns: Whether the data was successfully stored.
        :rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def obtain_readings(self) -> Dict[int, Dict[str, OutgoingDataTypes]]:
        """
        Obtain all the readings from the persistence.

        :returns: The dictionary containing all readings, grouped by timestamp.
        :rtype: Dict[int, List[Reading]]
        """
        raise NotImplementedError()

    @abstractmethod
    def obtain_readings_count(self) -> int:
        """
        Obtain the count of all readings stored in persistence.

        :returns: The count of all readings.
        :rtype: int
        """
        raise NotImplementedError()

    @abstractmethod
    def clear_readings(self) -> bool:
        """
        Clear the entire set of readings currently stored in the persistence.

        :returns: Whether the persistence was successfully cleared.
        :rtype: bool
        """
        raise NotImplementedError()
