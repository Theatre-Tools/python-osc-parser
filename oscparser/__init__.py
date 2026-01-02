"""oscparser - Open Sound Control (OSC) 1.0/1.1 parser library.

This module provides encoding and decoding for OSC packets with support for:
- OSC 1.0 (UDP and TCP with length-prefixed framing)
- OSC 1.1 (TCP with SLIP framing)

Basic usage:
    >>> from oscparser import OSCEncoder, OSCDecoder, OSCMessage, OSCInt, OSCModes, OSCFraming
    >>> encoder = OSCEncoder(OSCModes.UDP, OSCFraming.OSC10)
    >>> decoder = OSCDecoder(OSCModes.UDP, OSCFraming.OSC10)
    >>> msg = OSCMessage(address="/test", args=(OSCInt(42),))
    >>> encoded = encoder.encode(msg)
    >>> decoded = list(decoder.feed(encoded))[0]
"""

from oscparser.decode import OSCDecoder
from oscparser.encode import OSCEncoder, OSCFraming, OSCModes
from oscparser.types import (
    OSC_IMPULSE,
    OSCRGBA,
    OSCArg,
    OSCArray,
    OSCAtomic,
    OSCBlob,
    OSCBundle,
    OSCChar,
    OSCDouble,
    OSCFalse,
    OSCFloat,
    OSCImpulse,
    OSCInt,
    OSCInt64,
    OSCMessage,
    OSCMidi,
    OSCNil,
    OSCPacket,
    OSCString,
    OSCSymbol,
    OSCTimeTag,
    OSCTrue,
)

__all__ = [
    "OSCRGBA",
    "OSC_IMPULSE",
    "OSCArg",
    "OSCArray",
    "OSCAtomic",
    "OSCBlob",
    "OSCBundle",
    "OSCChar",
    "OSCDecoder",
    "OSCDouble",
    "OSCEncoder",
    "OSCFalse",
    "OSCFloat",
    "OSCFraming",
    "OSCImpulse",
    "OSCInt",
    "OSCInt64",
    "OSCMessage",
    "OSCMidi",
    "OSCModes",
    "OSCNil",
    "OSCPacket",
    "OSCString",
    "OSCSymbol",
    "OSCTimeTag",
    "OSCTrue",
]
