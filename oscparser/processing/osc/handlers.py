import struct
from typing import Any, cast

from oscparser.ctx import DataBuffer
from oscparser.processing.args.args import (
    ArgDispatcher,
    _decode_string,
    _encode_string,
    create_arg_dispatcher,
)
from oscparser.processing.osc.processing import OSCDispatcher, OSCPacketHandler
from oscparser.types import OSCArg, OSCBundle, OSCMessage

_BUNDLE_PREFIX = b"#bundle\x00"


class OSCBundleHandler(OSCPacketHandler[OSCBundle]):
    """Handler for OSC bundles - timetag + nested elements."""

    def __init__(self, dispatcher: OSCDispatcher):
        self.dispatcher = dispatcher

    @classmethod
    def from_dispatcher(cls, dispatcher: OSCDispatcher, arg_dispatcher: ArgDispatcher) -> "OSCBundleHandler":
        return cls(dispatcher)

    def decode(self, ctx: DataBuffer) -> OSCBundle:
        """Decode an OSC bundle from data buffer.

        Format:
        - Bundle prefix "#bundle\\x00"
        - Timetag (64-bit NTP timestamp)
        - Elements (size + content pairs)
        """
        # Read and verify bundle prefix
        prefix = ctx.read(len(_BUNDLE_PREFIX))
        if prefix != _BUNDLE_PREFIX:
            raise ValueError(f"Invalid bundle prefix: {prefix!r}")

        # Read timetag (64-bit big-endian integer)
        timetag = struct.unpack(">Q", ctx.read(8))[0]

        # Parse bundle elements
        elements: list[Any] = []

        while ctx.remaining() > 0:
            # Read element size (32-bit big-endian integer)
            element_size = struct.unpack(">I", ctx.read(4))[0]

            # Read element data
            element_data = DataBuffer(ctx.read(element_size))

            # Recursively decode the element using dispatcher
            handler = self.dispatcher.get_handler(element_data)
            element = handler.decode(element_data)

            elements.append(element)

        return OSCBundle(timetag=timetag, elements=tuple(elements))

    def encode(self, packet: OSCBundle, buf: DataBuffer):
        """Encode an OSC bundle to bytes."""
        if not isinstance(packet, OSCBundle):
            raise TypeError(f"Expected OSCBundle, got {type(packet)}")

        # Write bundle prefix
        buf.write(_BUNDLE_PREFIX)

        # Write timetag
        buf.write(struct.pack(">Q", packet.timetag))

        # Encode each element
        for element in packet.elements:
            # Recursively encode element
            result = DataBuffer(b"")
            element_handler = self.dispatcher.get_object_handler(type(element))
            element_handler.encode(element, result)
            # Write element size
            buf.write(struct.pack(">I", len(result.data)))

            # Write element data
            buf.write(result.data)


class OSCMessageHandler(OSCPacketHandler[OSCMessage]):
    """Handler for OSC messages - address pattern + typed arguments."""

    def __init__(self, dispatcher: OSCDispatcher, arg_dispatcher: ArgDispatcher):
        self.dispatcher = dispatcher
        # Use the arg dispatcher for handling individual arguments
        self.arg_dispatcher = arg_dispatcher if arg_dispatcher is not None else create_arg_dispatcher()

    @classmethod
    def from_dispatcher(cls, dispatcher: OSCDispatcher, arg_dispatcher: ArgDispatcher) -> "OSCMessageHandler":
        return cls(dispatcher, arg_dispatcher)

    def decode(self, ctx: DataBuffer) -> OSCMessage:
        """Decode an OSC message from data buffer.

        Format:
        - Address pattern (string)
        - Type tag string (string starting with ',')
        - Arguments (based on type tags)
        """
        # Parse address pattern
        address = _decode_string(ctx)

        # Check if there are any bytes remaining
        if ctx.remaining() == 0:
            # No arguments
            return OSCMessage(address=address, args=())

        # Parse type tag string
        type_tag_string = _decode_string(ctx)

        if not type_tag_string.startswith(","):
            raise ValueError(f"Type tag string must start with ',': {type_tag_string!r}")

        # Remove the leading comma
        type_tags = type_tag_string[1:]

        # Parse arguments based on type tags
        args: list[OSCArg] = []

        typetag_ctx = DataBuffer(type_tags.encode("utf-8"))

        while typetag_ctx.remaining() > 0:
            tag = typetag_ctx.read(1)

            handler = self.arg_dispatcher.get_handler_by_tag(tag)
            arg = cast(OSCArg, handler.decode(ctx, typetag_ctx))
            args.append(arg)

        return OSCMessage(address=address, args=tuple(args))

    def encode(self, packet: OSCMessage, buf: DataBuffer):
        """Encode an OSC message to bytes."""
        if not isinstance(packet, OSCMessage):
            raise TypeError(f"Expected OSCMessage, got {type(packet)}")

        # Encode address pattern
        buf.write(_encode_string(packet.address))

        # Build type tag string and argument data
        typetag_ctx = DataBuffer(b"")
        args_ctx = DataBuffer(b"")

        # Start type tag string with comma
        typetag_ctx.write(b",")

        for arg in packet.args:
            handler = self.arg_dispatcher.get_handler_by_object(type(arg))
            handler.encode(arg, args_ctx, typetag_ctx)

        # Write type tag string
        buf.write(_encode_string(typetag_ctx.data.decode("utf-8")))

        # Write argument data
        buf.write(args_ctx.data)


def register_osc_handlers(dispatcher: OSCDispatcher) -> None:
    """Register OSC message and bundle handlers."""
    dispatcher.register_handler(OSCMessage, b"/", OSCMessageHandler)
    dispatcher.register_handler(OSCBundle, b"#bundle\x00", OSCBundleHandler)
