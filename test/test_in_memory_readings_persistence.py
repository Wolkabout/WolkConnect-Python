"""Tests for InMemoryReadingsPersistence."""
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
import unittest
from time import time

from wolk.in_memory_readings_persistence import InMemoryReadingsPersistence


class TestInMemoryReadingsPersistence(unittest.TestCase):
    """Tests for InMemoryReadingsPersistence class."""

    def test_adding_empty_list(self):
        """Test adding a single reading to the persistence."""
        self.persistence = InMemoryReadingsPersistence()
        self.assertFalse(self.persistence.store_reading([]))
        self.assertEqual(len(self.persistence.obtain_readings()), 0)

    def test_adding_single_int_reading(self):
        """Test adding a single int reading to the persistence."""
        self.persistence = InMemoryReadingsPersistence()
        self.assertTrue(self.persistence.store_reading(("T", 123)))
        self.assertEqual(len(self.persistence.obtain_readings()), 1)

    def test_adding_multiple_int_readings(self):
        """Test adding a list of int readings to the persistence."""
        self.persistence = InMemoryReadingsPersistence()
        self.assertTrue(
            self.persistence.store_reading(
                [("A", 123), ("B", 456), ("C", 789)]
            )
        )
        self.assertEqual(len(self.persistence.obtain_readings()), 1)

    def test_add_multiple_readings_at_different_times_and_clean(self):
        """Test adding a lot of different readings at different times."""
        self.persistence = InMemoryReadingsPersistence()
        self.assertTrue(
            self.persistence.store_reading(
                [("A", 1), ("B", 2)], round(time() * 1000) + 123511
            )
        )
        self.assertTrue(
            self.persistence.store_reading(
                [("B", 3), ("C", 4)], round(time() * 1000) + 871265
            )
        )
        self.assertTrue(
            self.persistence.store_reading(
                [("C", 5), ("A", 6)], round(time() * 1000) + 839681
            )
        )
        self.assertEqual(len(self.persistence.obtain_readings()), 3)

        self.assertTrue(self.persistence.clear_readings())
        self.assertEqual(len(self.persistence.obtain_readings()), 0)
