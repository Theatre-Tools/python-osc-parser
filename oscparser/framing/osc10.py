"""OSC 1.0 framing for TCP transport.

OSC 1.0 over TCP uses length-prefixed framing: a 4-byte big-endian
integer indicating the packet size, followed by the packet data.
"""

import struct
from typing import Iterator

from oscparser.framing.framer import Framer


class OSC10Framer(Framer):
    """Framer for OSC 1.0 packets over TCP.

    Each packet is prefixed with a 4-byte big-endian size header.
    Complies with the Framer protocol.
    """

    def __init__(self):
        """Initialize the framer with an empty receive buffer."""
        self._buffer = bytearray()

    @staticmethod
    def frame(packet: bytes) -> bytes:
        """Frame an OSC packet for TCP transport.

        OSC 1.0 over TCP uses length-prefixed framing: a 4-byte big-endian
        integer indicating the packet size, followed by the packet data.

        Args:
            packet: Raw OSC packet bytes (message or bundle)

        Returns:
            Length-prefixed packet (4 bytes size + packet data)
        """
        size = len(packet)
        return struct.pack(">I", size) + packet

    def feed(self, data: bytes) -> Iterator[bytes]:
        """Feed data into the framer and yield complete packets.

        Buffers partial packets and yields complete packets as they arrive.

        Args:
            data: Raw bytes received from TCP socket

        Yields:
            Complete OSC packets (without size prefix)
        """
        self._buffer.extend(data)

        while len(self._buffer) >= 4:
            # Read the size prefix
            size = struct.unpack(">I", bytes(self._buffer[:4]))[0]

            # Check if we have the complete packet
            if len(self._buffer) < 4 + size:
                # Not enough data yet
                break

            # Extract the packet
            packet = bytes(self._buffer[4 : 4 + size])
            self._buffer = self._buffer[4 + size :]

            yield packet

    def clear_buffer(self) -> None:
        """Clear the internal receive buffer."""
        self._buffer.clear()
