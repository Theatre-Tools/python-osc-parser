"""OSC 1.0 / 1.1 data types.

This module defines Python classes and type aliases that model the
Open Sound Control 1.0 atomic types, composite types (messages and
bundles), and the additional recommended argument tags listed in the
specification (often referred to as "OSC 1.1").

It does **not** implement parsing or encoding; it is purely types.
"""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Tuple, Union

from pydantic import BaseModel


class _FrozenModel(BaseModel):
    """Base class for immutable OSC value types."""

    class Config:
        frozen = True


class OSCInt(_FrozenModel):
    """32-bit signed integer argument (tag 'i')."""

    TAG: ClassVar[str] = "i"
    value: int


class OSCFloat(_FrozenModel):
    """32-bit IEEE 754 floating point argument (tag 'f')."""

    TAG: ClassVar[str] = "f"
    value: float


class OSCString(_FrozenModel):
    """OSC string argument (tag 's')."""

    TAG: ClassVar[str] = "s"
    value: str


class OSCBlob(_FrozenModel):
    """OSC blob argument (tag 'b')."""

    TAG: ClassVar[str] = "b"
    value: bytes


class OSCTrue(_FrozenModel):
    """Boolean true argument (tag 'T')."""

    TAG: ClassVar[str] = "T"


class OSCFalse(_FrozenModel):
    """Boolean false argument (tag 'F')."""

    TAG: ClassVar[str] = "F"


class OSCNil(_FrozenModel):
    """Nil / null argument (tag 'N')."""

    TAG: ClassVar[str] = "N"


class OSCInt64(_FrozenModel):
    """64-bit signed integer argument (tag 'h')."""

    TAG: ClassVar[str] = "h"
    value: int


class OSCDouble(_FrozenModel):
    """64-bit IEEE 754 floating point argument (tag 'd')."""

    TAG: ClassVar[str] = "d"
    value: float


class OSCTimeTag(_FrozenModel):
    """OSC timetag argument (tag 't'), represented as a datetime."""

    TAG: ClassVar[str] = "t"
    value: datetime


class OSCChar(_FrozenModel):
    """Single ASCII / UTF-8 character argument (tag 'c')."""

    TAG: ClassVar[str] = "c"
    value: str  # usually length 1


class OSCSymbol(_FrozenModel):
    """Symbol argument (tag 'S'), semantically distinct from a string."""

    TAG: ClassVar[str] = "S"
    value: str


class OSCRGBA(_FrozenModel):
    """RGBA color argument (tag 'r')."""

    TAG: ClassVar[str] = "r"
    r: int
    g: int
    b: int
    a: int


class OSCMidi(_FrozenModel):
    """MIDI message argument (tag 'm').

    Bytes from MSB to LSB are:
    - port_id
    - status
    - data1
    - data2
    """

    TAG: ClassVar[str] = "m"

    port_id: int
    status: int
    data1: int
    data2: int


class OSCImpulse(_FrozenModel):
    """Impulse / infinitum / bang argument (tag 'I').

    There is no payload; the presence of this value is the data.
    """

    TAG: ClassVar[str] = "I"

    # No fields
    pass


# Singleton instance that can be reused for all impulse arguments.
OSC_IMPULSE = OSCImpulse()


class OSCArray(_FrozenModel):
    """Array argument (tags '[' ... ']').

    Contains a sequence of other OSC arguments, which may themselves be
    arrays (nested arrays are allowed by the 1.0 spec).
    """

    OPEN_TAG: ClassVar[str] = "["
    CLOSE_TAG: ClassVar[str] = "]"
    items: tuple["OSCArg", ...]


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
