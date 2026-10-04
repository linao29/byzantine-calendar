"""Core conversion logic for the Byzantine calendar.

The Byzantine (Constantinopolitan) calendar numbers years from the
creation of the world ("Indiction" era), traditionally placed on
1 September 5509 BCE. The Byzantine year begins on 1 September and
runs through 31 August of the following Gregorian year.

A Byzantine year B therefore overlaps two Gregorian years:
  B = Gregorian_year + 5509   for 1 Sep .. 31 Dec
  B = Gregorian_year + 5508   for 1 Jan .. 31 Aug

This module uses the proleptic Gregorian calendar for all input dates,
including those before 1582. We picked the proleptic Gregorian rather
than the Julian because the brief is ambiguous; a single, well-defined
calendar is easier to test and reason about than a hybrid.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass


class InvalidDateError(ValueError):
    """Raised when a date is outside the supported range."""


_START_MONTH = 9  # September
_START_DAY = 1
_OFFSET_BEFORE_NEW_YEAR = 5509  # Gregorian year + 5509 on/after Sep 1
_OFFSET_AFTER_NEW_YEAR = 5508   # Gregorian year + 5508 before Sep 1


def _to_ordinal(year: int, month: int, day: int) -> int:
    """Return the proleptic Gregorian ordinal for (year, month, day).

    datetime.date.toordinal works on the proleptic Gregorian calendar,
    accepting year 1 and later. We extend to non-positive years (BCE)
    by computing the ordinal manually, using the standard formula for
    the proleptic Gregorian calendar where year 0 = 1 BCE, year -1 = 2 BCE.
    """
    if year > 0:
        return datetime.date(year, month, day).toordinal()

    # Manual proleptic Gregorian ordinal for non-positive years.
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _from_ordinal(ordinal: int) -> tuple[int, int, int]:
    """Return (year, month, day) for a proleptic Gregorian ordinal."""
    if ordinal >= 1:
        d = datetime.date.fromordinal(ordinal)
        return d.year, d.month, d.day

    a = ordinal + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return year, month, day


def to_byzantine(year: int, month: int, day: int) -> "ByzantineDate":
    """Convert a proleptic Gregorian date to a Byzantine date.

    Raises InvalidDateError for dates before 1 Sep 5509 BCE, which is
    the start of Byzantine year 1.
    """
    ordinal = _to_ordinal(year, month, day)
    byz_year_1_start = _to_ordinal(-5508, _START_MONTH, _START_DAY)
    if ordinal < byz_year_1_start:
        raise InvalidDateError(
            f"Date {year:04d}-{month:02d}-{day:02d} is before the start of "
            "Byzantine year 1 (1 September 5509 BCE)."
        )

    offset = _OFFSET_BEFORE_NEW_YEAR if month > _START_MONTH or (
        month == _START_MONTH and day >= _START_DAY
    ) else _OFFSET_AFTER_NEW_YEAR
    byz_year = year + offset
    return ByzantineDate(byz_year, month, day)


def to_gregorian(byz_year: int, month: int, day: int) -> tuple[int, int, int]:
    """Convert a Byzantine date to a (year, month, day) Gregorian tuple.

    Raises InvalidDateError for byz_year < 1.
    """
    if byz_year < 1:
        raise InvalidDateError(f"Byzantine year must be >= 1, got {byz_year}.")

    if month > _START_MONTH or (month == _START_MONTH and day >= _START_DAY):
        greg_year = byz_year - _OFFSET_BEFORE_NEW_YEAR
    else:
        greg_year = byz_year - _OFFSET_AFTER_NEW_YEAR
    return greg_year, month, day


@dataclass(frozen=True)
class ByzantineDate:
    """An immutable Byzantine calendar date."""

    year: int
    month: int
    day: int

    def __post_init__(self) -> None:
        if not (1 <= self.month <= 12):
            raise ValueError(f"Month must be 1..12, got {self.month}.")
        if not (1 <= self.day <= 31):
            raise ValueError(f"Day must be 1..31, got {self.day}.")
        if self.year < 1:
            raise ValueError(f"Year must be >= 1, got {self.year}.")

    def to_gregorian(self) -> tuple[int, int, int]:
        """Return the corresponding Gregorian (year, month, day)."""
        return to_gregorian(self.year, self.month, self.day)

    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
