import struct
from datetime import datetime

from oscparser.ctx import DataBuffer
from oscparser.processing.args.proccessing import ArgDispatcher, ArgHandler
from oscparser.types import (
    OSCRGBA,
    OSCArray,
    OSCBlob,
    OSCChar,
    OSCDouble,
    OSCFalse,
    OSCFloat,
    OSCImpulse,
    OSCInt,
    OSCInt64,
    OSCMidi,
    OSCNil,
    OSCString,
    OSCSymbol,
    OSCTimeTag,
    OSCTrue,
)


def _pad_to_multiple_of_4(length: int) -> int:
    """Return padding bytes needed to align to 4-byte boundary."""
    remainder = length % 4
    return 0 if remainder == 0 else 4 - remainder


def _encode_string(s: str) -> bytes:
    """Encode a string with null terminator and padding."""
    encoded = s.encode("utf-8") + b"\x00"
    padding = _pad_to_multiple_of_4(len(encoded))
    return encoded + b"\x00" * padding


def _decode_string(ctx: DataBuffer) -> str:
    """Decode a null-terminated string from context."""
    result = b""
    while True:
        byte = ctx.read(1)
        if byte == b"\x00":
            break
        result += byte
    # Skip padding
    padding = _pad_to_multiple_of_4(len(result) + 1)
    if padding > 0:
        ctx.read(padding)
    return result.decode("utf-8")


def _encode_blob(data: bytes) -> bytes:
    """Encode a blob with 4-byte size prefix and padding."""
    size = struct.pack(">I", len(data))
    padding = _pad_to_multiple_of_4(len(data))
    return size + data + b"\x00" * padding


def _decode_blob(ctx: DataBuffer) -> bytes:
    """Decode a blob from context."""
    size = struct.unpack(">I", ctx.read(4))[0]
    data = ctx.read(size)
    padding = _pad_to_multiple_of_4(size)
    if padding > 0:
        ctx.read(padding)
    return data


def _datetime_to_timetag(dt: datetime) -> int:
    """Convert datetime to NTP timetag (64-bit)."""
    # NTP epoch is 1900-01-01, Unix epoch is 1970-01-01
    NTP_DELTA = 2208988800
    timestamp = dt.timestamp()
    seconds = int(timestamp) + NTP_DELTA
    fraction = int((timestamp % 1) * (2**32))
    return (seconds << 32) | fraction


def _timetag_to_datetime(timetag: int) -> datetime:
    """Convert NTP timetag to datetime."""
    NTP_DELTA = 2208988800
    seconds = (timetag >> 32) - NTP_DELTA
    fraction = (timetag & 0xFFFFFFFF) / (2**32)
    return datetime.fromtimestamp(seconds + fraction)


# ============================================================================
# OSCInt Handler
# ============================================================================


class OSCIntHandler(ArgHandler[OSCInt]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCIntHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCInt]:
        return OSCInt

    def encode(self, arg: OSCInt, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"i")
        message_body.write(struct.pack(">i", arg.value))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCInt:
        value = struct.unpack(">i", message_body.read(4))[0]
        return OSCInt(value=value)


# ============================================================================
# OSCFloat Handler
# ============================================================================


class OSCFloatHandler(ArgHandler[OSCFloat]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCFloatHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCFloat]:
        return OSCFloat

    def encode(self, arg: OSCFloat, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"f")
        message_body.write(struct.pack(">f", arg.value))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCFloat:
        value = struct.unpack(">f", message_body.read(4))[0]
        return OSCFloat(value=value)


# ============================================================================
# OSCString Handler
# ============================================================================


class OSCStringHandler(ArgHandler[OSCString]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCStringHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCString]:
        return OSCString

    def encode(self, arg: OSCString, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"s")
        message_body.write(_encode_string(arg.value))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCString:
        value = _decode_string(message_body)
        return OSCString(value=value)


# ============================================================================
# OSCBlob Handler
# ============================================================================


class OSCBlobHandler(ArgHandler[OSCBlob]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCBlobHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCBlob]:
        return OSCBlob

    def encode(self, arg: OSCBlob, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"b")
        message_body.write(_encode_blob(arg.value))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCBlob:
        value = _decode_blob(message_body)
        return OSCBlob(value=value)


# ============================================================================
# OSCTrue Handler
# ============================================================================


class OSCTrueHandler(ArgHandler[OSCTrue]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCTrueHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCTrue]:
        return OSCTrue

    def encode(self, arg: OSCTrue, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"T")
        # No payload

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCTrue:
        return OSCTrue()


# ============================================================================
# OSCFalse Handler
# ============================================================================


class OSCFalseHandler(ArgHandler[OSCFalse]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCFalseHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCFalse]:
        return OSCFalse

    def encode(self, arg: OSCFalse, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"F")
        # No payload

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCFalse:
        return OSCFalse()


# ============================================================================
# OSCNil Handler
# ============================================================================


class OSCNilHandler(ArgHandler[OSCNil]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCNilHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCNil]:
        return OSCNil

    def encode(self, arg: OSCNil, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"N")
        # No payload

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCNil:
        return OSCNil()


# ============================================================================
# OSCInt64 Handler
# ============================================================================


class OSCInt64Handler(ArgHandler[OSCInt64]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCInt64Handler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCInt64]:
        return OSCInt64

    def encode(self, arg: OSCInt64, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"h")
        message_body.write(struct.pack(">q", arg.value))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCInt64:
        value = struct.unpack(">q", message_body.read(8))[0]
        return OSCInt64(value=value)


# ============================================================================
# OSCDouble Handler
# ============================================================================


class OSCDoubleHandler(ArgHandler[OSCDouble]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCDoubleHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCDouble]:
        return OSCDouble

    def encode(self, arg: OSCDouble, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"d")
        message_body.write(struct.pack(">d", arg.value))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCDouble:
        value = struct.unpack(">d", message_body.read(8))[0]
        return OSCDouble(value=value)


# ============================================================================
# OSCTimeTag Handler
# ============================================================================


class OSCTimeTagHandler(ArgHandler[OSCTimeTag]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCTimeTagHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCTimeTag]:
        return OSCTimeTag

    def encode(self, arg: OSCTimeTag, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"t")
        timetag = _datetime_to_timetag(arg.value)
        message_body.write(struct.pack(">Q", timetag))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCTimeTag:
        timetag = struct.unpack(">Q", message_body.read(8))[0]
        value = _timetag_to_datetime(timetag)
        return OSCTimeTag(value=value)


# ============================================================================
# OSCChar Handler
# ============================================================================


class OSCCharHandler(ArgHandler[OSCChar]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCCharHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCChar]:
        return OSCChar

    def encode(self, arg: OSCChar, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"c")
        # Encode as 4-byte ASCII value
        char_byte = arg.value.encode("utf-8")[0] if arg.value else 0
        message_body.write(struct.pack(">I", char_byte))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCChar:
        char_value = struct.unpack(">I", message_body.read(4))[0]
        value = chr(char_value) if char_value > 0 else ""
        return OSCChar(value=value)


# ============================================================================
# OSCSymbol Handler
# ============================================================================


class OSCSymbolHandler(ArgHandler[OSCSymbol]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCSymbolHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCSymbol]:
        return OSCSymbol

    def encode(self, arg: OSCSymbol, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"S")
        message_body.write(_encode_string(arg.value))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCSymbol:
        value = _decode_string(message_body)
        return OSCSymbol(value=value)


# ============================================================================
# OSCRGBA Handler
# ============================================================================


class OSCRGBAHandler(ArgHandler[OSCRGBA]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCRGBAHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCRGBA]:
        return OSCRGBA

    def encode(self, arg: OSCRGBA, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"r")
        message_body.write(struct.pack(">BBBB", arg.r, arg.g, arg.b, arg.a))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCRGBA:
        r, g, b, a = struct.unpack(">BBBB", message_body.read(4))
        return OSCRGBA(r=r, g=g, b=b, a=a)


# ============================================================================
# OSCMidi Handler
# ============================================================================


class OSCMidiHandler(ArgHandler[OSCMidi]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCMidiHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCMidi]:
        return OSCMidi

    def encode(self, arg: OSCMidi, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"m")
        message_body.write(struct.pack(">BBBB", arg.port_id, arg.status, arg.data1, arg.data2))

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCMidi:
        port_id, status, data1, data2 = struct.unpack(">BBBB", message_body.read(4))
        return OSCMidi(port_id=port_id, status=status, data1=data1, data2=data2)


# ============================================================================
# OSCImpulse Handler
# ============================================================================


class OSCImpulseHandler(ArgHandler[OSCImpulse]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCImpulseHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCImpulse]:
        return OSCImpulse

    def encode(self, arg: OSCImpulse, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"I")
        # No payload

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCImpulse:
        return OSCImpulse()


# ============================================================================
# OSCArray Handler
# ============================================================================


class OSCArrayHandler(ArgHandler[OSCArray]):
    def __init__(self, dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: ArgDispatcher) -> "OSCArrayHandler":
        return cls(dispatcher)

    @property
    def handles(self) -> type[OSCArray]:
        return OSCArray

    def encode(self, arg: OSCArray, message_body: DataBuffer, typetag: DataBuffer) -> None:
        typetag.write(b"[")
        for item in arg.items:
            handler = self.dispatcher.get_handler_by_object(type(item))
            handler.encode(item, message_body, typetag)
        typetag.write(b"]")

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> OSCArray:
        items = []
        while True:
            tag = typetag.read(1)
            if tag == b"]":
                break
            handler = self.dispatcher.get_handler_by_tag(tag)
            item = handler.decode(message_body, typetag)
            items.append(item)
        return OSCArray(items=tuple(items))


# ============================================================================
# Registry
# ============================================================================


def register_all_handlers(dispatcher: ArgDispatcher) -> None:
    """Register all OSC type handlers with the dispatcher."""
    handlers = [
        (OSCInt, b"i", OSCIntHandler),
        (OSCFloat, b"f", OSCFloatHandler),
        (OSCString, b"s", OSCStringHandler),
        (OSCBlob, b"b", OSCBlobHandler),
        (OSCTrue, b"T", OSCTrueHandler),
        (OSCFalse, b"F", OSCFalseHandler),
        (OSCNil, b"N", OSCNilHandler),
        (OSCInt64, b"h", OSCInt64Handler),
        (OSCDouble, b"d", OSCDoubleHandler),
        (OSCTimeTag, b"t", OSCTimeTagHandler),
        (OSCChar, b"c", OSCCharHandler),
        (OSCSymbol, b"S", OSCSymbolHandler),
        (OSCRGBA, b"r", OSCRGBAHandler),
        (OSCMidi, b"m", OSCMidiHandler),
        (OSCImpulse, b"I", OSCImpulseHandler),
        (OSCArray, b"[", OSCArrayHandler),
    ]

    for obj_type, tag, handler_cls in handlers:
        dispatcher.register_handler(obj_type, tag, handler_cls)


def create_arg_dispatcher() -> ArgDispatcher:
    """Create and return a fully configured argument dispatcher."""
    dispatcher = ArgDispatcher()
    register_all_handlers(dispatcher)
    return dispatcher
