from typing import Iterator

from oscparser.framing.framer import Framer


class FullFramer(Framer):
    """A framer that does not perform any framing.

    This class is useful for protocols that do not require framing,
    such as UDP transport of OSC packets.

    Complies with the Framer protocol.
    """

    @staticmethod
    def frame(packet: bytes) -> bytes:
        """Return the packet as-is without any framing.

        Args:
            packet: Raw OSC packet bytes (message or bundle)

        Returns:
            The same packet bytes without any framing
        """
        return packet

    def feed(self, data: bytes) -> Iterator[bytes]:
        """Yield the incoming data as a complete packet.

        Since there is no framing, each call to feed yields the entire data.

        Args:
            data: Raw bytes received from transport

        Yields:
            The entire data as a single OSC packet
        """
        yield data

    def clear_buffer(self) -> None:
        """No internal buffer to clear in this framer."""
        pass
