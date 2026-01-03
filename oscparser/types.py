"""OSC 1.0 / 1.1 data types.

This module defines Python classes and type aliases that model the
Open Sound Control 1.0 atomic types, composite types (messages and
bundles), and the additional recommended argument tags listed in the
specification (often referred to as "OSC 1.1").

It does **not** implement parsing or encoding; it is purely types.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Tuple, Union

from pydantic import BaseModel


class _FrozenModel(BaseModel):
    """Base class for immutable OSC value types."""

    class Config:
        frozen = True


class OSCInt(_FrozenModel):
    """32-bit signed integer argument (tag 'i')."""

    TAG: Literal["i"] = "i"
    value: int

    @classmethod
    def new(cls, value: int) -> OSCInt:
        """Create a new OSCInt instance."""

        return cls(value=value)


class OSCFloat(_FrozenModel):
    """32-bit IEEE 754 floating point argument (tag 'f')."""

    TAG: Literal["f"] = "f"
    value: float

    @classmethod
    def new(cls, value: float) -> OSCFloat:
        """Create a new OSCFloat instance."""

        return cls(value=value)


class OSCString(_FrozenModel):
    """OSC string argument (tag 's')."""

    TAG: Literal["s"] = "s"
    value: str

    @classmethod
    def new(cls, value: str) -> OSCString:
        """Create a new OSCString instance."""

        return cls(value=value)


class OSCBlob(_FrozenModel):
    """OSC blob argument (tag 'b')."""

    TAG: Literal["b"] = "b"
    value: bytes

    @classmethod
    def new(cls, value: bytes) -> OSCBlob:
        """Create a new OSCBlob instance."""

        return cls(value=value)


class OSCTrue(_FrozenModel):
    """Boolean true argument (tag 'T')."""

    TAG: Literal["T"] = "T"

    @classmethod
    def new(cls) -> OSCTrue:
        """Create a new OSCTrue instance."""

        return cls()


class OSCFalse(_FrozenModel):
    """Boolean false argument (tag 'F')."""

    TAG: Literal["F"] = "F"

    @classmethod
    def new(cls) -> OSCFalse:
        """Create a new OSCFalse instance."""

        return cls()


class OSCNil(_FrozenModel):
    """Nil / null argument (tag 'N')."""

    TAG: Literal["N"] = "N"

    @classmethod
    def new(cls) -> OSCNil:
        """Create a new OSCNil instance."""

        return cls()


class OSCInt64(_FrozenModel):
    """64-bit signed integer argument (tag 'h')."""

    TAG: Literal["h"] = "h"
    value: int

    @classmethod
    def new(cls, value: int) -> OSCInt64:
        """Create a new OSCInt64 instance."""

        return cls(value=value)


class OSCDouble(_FrozenModel):
    """64-bit IEEE 754 floating point argument (tag 'd')."""

    TAG: Literal["d"] = "d"
    value: float

    @classmethod
    def new(cls, value: float) -> OSCDouble:
        """Create a new OSCDouble instance."""

        return cls(value=value)


class OSCTimeTag(_FrozenModel):
    """OSC timetag argument (tag 't'), represented as a datetime."""

    TAG: Literal["t"] = "t"
    value: datetime

    @classmethod
    def new(cls, value: datetime) -> OSCTimeTag:
        """Create a new OSCTimeTag instance."""

        return cls(value=value)


class OSCChar(_FrozenModel):
    """Single ASCII / UTF-8 character argument (tag 'c')."""

    TAG: Literal["c"] = "c"
    value: str  # usually length 1

    @classmethod
    def new(cls, value: str) -> OSCChar:
        """Create a new OSCChar instance."""

        return cls(value=value)


class OSCSymbol(_FrozenModel):
    """Symbol argument (tag 'S'), semantically distinct from a string."""

    TAG: Literal["S"] = "S"
    value: str

    @classmethod
    def new(cls, value: str) -> OSCSymbol:
        """Create a new OSCSymbol instance."""

        return cls(value=value)


class OSCRGBA(_FrozenModel):
    """RGBA color argument (tag 'r')."""

    TAG: Literal["r"] = "r"
    r: int
    g: int
    b: int
    a: int

    @classmethod
    def new(cls, r: int, g: int, b: int, a: int) -> OSCRGBA:
        """Create a new OSCRGBA instance."""

        return cls(r=r, g=g, b=b, a=a)


class OSCMidi(_FrozenModel):
    """MIDI message argument (tag 'm').

    Bytes from MSB to LSB are:
    - port_id
    - status
    - data1
    - data2
    """

    TAG: Literal["m"] = "m"

    port_id: int
    status: int
    data1: int
    data2: int

    @classmethod
    def new(cls, port_id: int, status: int, data1: int, data2: int) -> OSCMidi:
        """Create a new OSCMidi instance."""

        return cls(port_id=port_id, status=status, data1=data1, data2=data2)


class OSCImpulse(_FrozenModel):
    """Impulse / infinitum / bang argument (tag 'I').

    There is no payload; the presence of this value is the data.
    """

    TAG: Literal["I"] = "I"

    # No fields

    @classmethod
    def new(cls) -> OSCImpulse:
        """Create a new OSCImpulse instance."""

        return cls()


# Singleton instance that can be reused for all impulse arguments.
OSC_IMPULSE = OSCImpulse()


class OSCArray(_FrozenModel):
    """Array argument (tags '[' ... ']').

    Contains a sequence of other OSC arguments, which may themselves be
    arrays (nested arrays are allowed by the 1.0 spec).
    """

    items: tuple["OSCArg", ...]

    OPEN_TAG: Literal["["] = "["
    CLOSE_TAG: Literal["]"] = "]"

    @classmethod
    def new(cls, items: Tuple["OSCArg", ...]) -> OSCArray:
        """Create a new OSCArray instance.

        Args:
            items: Sequence of OSCArg items to include in the array

        Returns:
            An OSCArray instance containing the provided items
        """
        return cls(items=items)


# === Composite packet types (messages and bundles) ===


OSCAtomic = Union[
    OSCInt,
    OSCFloat,
    OSCString,
    OSCBlob,
    OSCTrue,
    OSCFalse,
    OSCNil,
    OSCInt64,
    OSCDouble,
    OSCTimeTag,
    OSCChar,
    OSCSymbol,
    OSCRGBA,
    OSCMidi,
    OSCImpulse,
]

OSCArg = Union[OSCAtomic, OSCArray]


class OSCMessage(_FrozenModel):
    """OSC message: address pattern + typed argument list.

    - ``address`` is an OSC Address Pattern beginning with '/'.
    - ``args`` is a sequence of OSCArg values.
    """

    address: str
    args: Tuple[OSCArg, ...]


class OSCBundle(_FrozenModel):
    """OSC bundle containing messages and/or sub-bundles.

    - ``timetag`` is a 64-bit OSC timetag (NTP). 0 means "immediately".
    - ``elements`` is a sequence of OSCMessage or nested OSCBundle.
    """

    timetag: int
    elements: Tuple[OSCPacket, ...]


OSCPacket = Union["OSCMessage", "OSCBundle"]

__all__ = [
    "OSCRGBA",
    "OSC_IMPULSE",
    "OSCArg",
    "OSCArray",
    "OSCAtomic",
    "OSCBlob",
    "OSCBundle",
    "OSCChar",
    "OSCDouble",
    "OSCFalse",
    "OSCImpulse",
    "OSCInt",
    "OSCInt64",
    "OSCMessage",
    "OSCMidi",
    "OSCNil",
    "OSCPacket",
    "OSCString",
    "OSCSymbol",
    "OSCTimeTag",
    "OSCTrue",
]
