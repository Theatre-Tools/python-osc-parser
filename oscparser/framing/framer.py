from typing import Iterator, Protocol


class Framer(Protocol):
    """Protocol for OSC framers."""

    @staticmethod
    def frame(packet: bytes) -> bytes:
        """Frame an OSC packet for transport."""
        ...

    def feed(self, data: bytes) -> Iterator[bytes]:
        """Feed data into the framer and yield complete packets."""
        ...

    def clear_buffer(self) -> None:
        """Clear the internal receive buffer."""
        ...
