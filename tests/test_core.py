import datetime
import unittest

from byzantine_calendar import (
    to_byzantine,
    to_gregorian,
    ByzantineDate,
    InvalidDateError,
)


class TestToByzantine(unittest.TestCase):

    def test_before_new_year_boundary_aug31(self):
        # 31 August 2024 is still in Byzantine year 7532.
        result = to_byzantine(2024, 8, 31)
        self.assertEqual(result, ByzantineDate(7532, 8, 31))

    def test_new_year_sep1(self):
        # 1 September 2024 starts Byzantine year 7533.
        result = to_byzantine(2024, 9, 1)
        self.assertEqual(result, ByzantineDate(7533, 9, 1))

    def test_january_uses_offset_5508(self):
        result = to_byzantine(2024, 1, 1)
        self.assertEqual(result, ByzantineDate(7532, 1, 1))

    def test_december_uses_offset_5509(self):
        result = to_byzantine(2024, 12, 25)
        self.assertEqual(result, ByzantineDate(7533, 12, 25))

    def test_round_trip_gregorian_byzantine_gregorian(self):
        cases = [
            (2024, 9, 1),
            (2024, 8, 31),
            (2024, 1, 1),
            (2024, 12, 25),
            (1, 1, 1),
            (1, 9, 1),
        ]
        for y, m, d in cases:
            with self.subTest(date=(y, m, d)):
                b = to_byzantine(y, m, d)
                self.assertEqual(to_gregorian(b.year, b.month, b.day), (y, m, d))

    def test_byzantine_year_1_start(self):
        # 1 Sep 5509 BCE is the start of Byzantine year 1.
        # Proleptic Gregorian year -5508 corresponds to 5509 BCE.
        result = to_byzantine(-5508, 9, 1)
        self.assertEqual(result, ByzantineDate(1, 9, 1))

    def test_day_before_year_1_raises(self):
        with self.assertRaises(InvalidDateError):
            to_byzantine(-5508, 8, 31)

    def test_return_type_is_byzantine_date(self):
        result = to_byzantine(2024, 9, 1)
        self.assertIsInstance(result, ByzantineDate)

    def test_str_format(self):
        result = to_byzantine(2024, 9, 1)
        self.assertEqual(str(result), "7533-09-01")


class TestToGregorian(unittest.TestCase):

    def test_sep1(self):
        self.assertEqual(to_gregorian(7533, 9, 1), (2024, 9, 1))

    def test_aug31(self):
        self.assertEqual(to_gregorian(7532, 8, 31), (2024, 8, 31))

    def test_january(self):
        self.assertEqual(to_gregorian(7532, 1, 1), (2024, 1, 1))

    def test_year_too_small_raises(self):
        with self.assertRaises(InvalidDateError):
            to_gregorian(0, 1, 1)


class TestByzantineDate(unittest.TestCase):

    def test_to_gregorian_method(self):
        bd = ByzantineDate(7533, 9, 1)
        self.assertEqual(bd.to_gregorian(), (2024, 9, 1))

    def test_invalid_month(self):
        with self.assertRaises(ValueError):
            ByzantineDate(7533, 13, 1)

    def test_invalid_day(self):
        with self.assertRaises(ValueError):
            ByzantineDate(7533, 9, 32)

    def test_invalid_year(self):
        with self.assertRaises(ValueError):
            ByzantineDate(0, 1, 1)

    def test_frozen(self):
        bd = ByzantineDate(7533, 9, 1)
        with self.assertRaises(Exception):
            bd.year = 7534  # type: ignore[misc]


class TestConsistencyWithOrdinals(unittest.TestCase):
    """Dates before 1582 use the proleptic Gregorian calendar.
    We verify our manual ordinal computation against datetime for a
    positive BCE-ish boundary value that datetime can handle.
    """

    def test_positive_year_consistent_with_datetime(self):
        # datetime supports year 1 onward; ensure our helper agrees.
        for y, m, d in [(1, 1, 1), (1, 9, 1), (100, 2, 28), (1582, 10, 4)]:
            expected = datetime.date(y, m, d).toordinal()
            # Access internal helper for the cross-check.
            from byzantine_calendar.core import _to_ordinal
            self.assertEqual(_to_ordinal(y, m, d), expected)

    def test_round_trip_through_ordinal_helpers(self):
        from byzantine_calendar.core import _to_ordinal, _from_ordinal
        cases = [
            (-5508, 9, 1),
            (-5509, 8, 31),
            (2024, 9, 1),
            (1, 1, 1),
        ]
        for y, m, d in cases:
            with self.subTest(date=(y, m, d)):
                self.assertEqual(_from_ordinal(_to_ordinal(y, m, d)), (y, m, d))


if __name__ == "__main__":
    unittest.main()
