# Byzantine Calendar

A small Python library for converting between the proleptic Gregorian calendar and the Byzantine (Constantinopolitan) calendar, which numbers years from the creation of the world and begins each year on 1 September.

## Installation

No third-party dependencies. Place `src/` on your `PYTHONPATH`:

```bash
export PYTHONPATH=src
```

## Usage

```python
from byzantine_calendar import to_byzantine, to_gregorian, ByzantineDate, InvalidDateError

# Gregorian -> Byzantine
b = to_byzantine(2024, 9, 1)
print(b)  # 7533-09-01

# Byzantine -> Gregorian
g = to_gregorian(7533, 1, 1)
print(g)  # (2024, 1, 1)

# Using the dataclass directly
bd = ByzantineDate(7533, 9, 1)
print(bd.to_gregorian())  # (2024, 9, 1)
```

Exported names:

- `to_byzantine(year, month, day) -> ByzantineDate`
- `to_gregorian(byz_year, month, day) -> tuple[int, int, int]`
- `ByzantineDate` (frozen dataclass with `.to_gregorian()` method)
- `InvalidDateError` (subclass of `ValueError`)

## Why this exists

Converting historical dates referenced in Byzantine texts requires a clear rule: Byzantine year `B` corresponds to Gregorian year `G` such that `B = G + 5508` from 1 September through 31 December, and `B = G + 5509` from 1 January through 31 August. This library implements exactly that rule and nothing else.

The one trade-off: all input dates are treated as proleptic Gregorian, including those before 1582. The Julian calendar was historically used in the Byzantine world, so for scholarly work involving pre-1582 primary sources you may need an additional Julian conversion. We chose proleptic Gregorian because it removes the Julian/Gregorian switch ambiguity and makes the library fully deterministic.

## Edge cases

The Byzantine year boundary on 1 September is the awkward edge. A date like 31 August 2024 falls in Byzantine year 7532, while 1 September 2024 falls in 7533. This library handles that split correctly, but if you are computing year ranges by hand you must account for the September boundary yourself.

The earliest supported date is 1 September 5509 BCE (proleptic Gregorian), the first day of Byzantine year 1. Earlier dates raise `InvalidDateError`.

## Running tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

