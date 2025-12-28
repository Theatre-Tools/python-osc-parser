from typing import Any, Protocol

from oscparser.ctx import DataBuffer
from oscparser.processing.args.args import create_arg_dispatcher
from oscparser.processing.args.proccessing import ArgDispatcher


class OSCPacketHandler[T: object = object](Protocol):
    """Protocol for OSC packet handlers (messages and bundles)."""

    @classmethod
    def from_dispatcher(cls, dispatcher: "OSCDispatcher", arg_dispatcher: ArgDispatcher) -> "OSCPacketHandler[T]": ...

    def decode(self, ctx: DataBuffer) -> T:
        """Decode OSC packet from data buffer."""
        ...

    def encode(self, packet: T, buf: DataBuffer):
        """Encode OSC packet to bytes."""
        ...


class OSCDispatcher:
    """Dispatcher for OSC packet types (messages and bundles)."""

    def __init__(self, arg_dispatcher: ArgDispatcher | None = None):
        self._handlers: dict[bytes, OSCPacketHandler[Any]] = {}
        self._object_handlers: dict[type, OSCPacketHandler[Any]] = {}
        self._arg_dispatcher = arg_dispatcher if arg_dispatcher is not None else create_arg_dispatcher()

    def register_handler[T: object](self, obj: type[T], handler_tag: bytes, handler: type[OSCPacketHandler[T]]) -> None:
        """Register a packet handler."""
        handler_inst = handler.from_dispatcher(self, self._arg_dispatcher)
        self._handlers[handler_tag] = handler_inst
        self._object_handlers[obj] = handler_inst

    def get_handler(self, data: DataBuffer) -> OSCPacketHandler:
        """Get appropriate handler for the given data."""
        for handler_tag, handler in self._handlers.items():
            if data.startswith(handler_tag):
                return handler
        raise ValueError("No handler found")

    def get_object_handler[T](self, obj: type[T]) -> OSCPacketHandler[T]:
        """Get handler for the given object type."""
        return self._object_handlers[obj]
