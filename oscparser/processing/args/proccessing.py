from typing import Any, Protocol, cast

from oscparser.ctx import DataBuffer


class ArgHandler[T: object = object](Protocol):
    @classmethod
    def from_dispatcher(cls, dispatcher: "ArgDispatcher") -> "ArgHandler[T]": ...

    def encode(self, arg: T, message_body: DataBuffer, typetag: DataBuffer): ...

    def decode(self, message_body: DataBuffer, typetag: DataBuffer) -> T: ...


class ArgDispatcher:
    def __init__(self):
        self._tag_handlers: dict[bytes, ArgHandler[Any]] = {}
        self._object_handlers: dict[type, ArgHandler[Any]] = {}

    def register_handler[T: type](self, obj: T, tag: bytes, handler: type[ArgHandler[T]]) -> None:
        handler_inst = handler.from_dispatcher(self)
        self._tag_handlers[tag] = handler_inst
        self._object_handlers[obj] = handler_inst

    def get_handler_by_tag(self, tag: bytes) -> ArgHandler:
        return self._tag_handlers[tag]

    def get_handler_by_object[T](self, obj: type[T]) -> ArgHandler[T]:
        return cast(ArgHandler[T], self._object_handlers[obj])
