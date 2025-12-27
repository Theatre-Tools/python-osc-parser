"""OSC 1.1 framing for TCP transport using SLIP encoding.

OSC 1.1 adds support for stream-oriented transports like TCP. Since TCP is a
byte stream without inherent message boundaries, SLIP (Serial Line Internet
Protocol) encoding is used to frame OSC packets.

SLIP uses special bytes to delimit packets:
- END (0xC0): Packet boundary marker
- ESC (0xDB): Escape byte
- ESC_END (0xDC): Escaped END byte
- ESC_ESC (0xDD): Escaped ESC byte

Reference: RFC 1055, OSC 1.1 specification
"""

from typing import Iterator

from oscparser.framing.framer import Framer

# SLIP protocol constants
END = b"\xc0"
ESC = b"\xdb"
ESC_END = b"\xdc"
ESC_ESC = b"\xdd"


class SLIPError(ValueError):
    """Exception raised when SLIP protocol violations are detected."""

    pass


class OSC11Framer(Framer):
    """Framer for OSC 1.1 packets over TCP using SLIP encoding.

    This class handles:
    - Encoding OSC packets with SLIP framing for transmission
    - Decoding SLIP-framed packets from received byte streams
    - Buffering partial packets in stream-based reception

    Complies with the Framer protocol.
    """

    def __init__(self):
        """Initialize the framer with an empty receive buffer."""
        self._buffer = bytearray()

    @staticmethod
    def frame(packet: bytes) -> bytes:
        """Frame an OSC packet for TCP transport using SLIP encoding.

        The packet is escaped according to SLIP rules and wrapped with END bytes.

        SLIP encoding rules:
        - Replace ESC with ESC + ESC_ESC
        - Replace END with ESC + ESC_END
        - Wrap with END bytes (before and after)

        Args:
            packet: Raw OSC packet bytes (message or bundle)

        Returns:
            SLIP-encoded packet ready for transmission
        """
        if not packet:
            packet = b""

        # Escape special bytes
        encoded = packet.replace(ESC, ESC + ESC_ESC)
        encoded = encoded.replace(END, ESC + ESC_END)

        # Wrap with END bytes
        return END + encoded + END

    @staticmethod
    def _unframe(slip_packet: bytes) -> bytes:
        """Unframe a single SLIP-encoded packet.

        This decodes one complete SLIP packet. The packet must be a complete,
        properly framed SLIP packet (starting and ending with END bytes).

        Args:
            slip_packet: SLIP-encoded packet bytes

        Returns:
            Decoded OSC packet bytes

        Raises:
            SLIPError: If the packet is malformed or contains invalid sequences
        """
        if not OSC11Framer._is_valid_slip(slip_packet):
            raise SLIPError(f"Invalid SLIP packet: {slip_packet!r}")

        # Strip END bytes
        decoded = slip_packet.strip(END)

        # Replace escaped sequences
        decoded = decoded.replace(ESC + ESC_END, END)
        decoded = decoded.replace(ESC + ESC_ESC, ESC)

        return decoded

    def feed(self, data: bytes) -> Iterator[bytes]:
        """Feed data into the framer and yield complete packets.

        This method maintains an internal buffer to handle partial packets.
        As data arrives, it's buffered until complete SLIP-framed packets
        can be extracted.

        Args:
            data: Raw bytes received from TCP socket

        Yields:
            Complete OSC packets (SLIP-decoded)

        Raises:
            SLIPError: If malformed SLIP sequences are detected
        """
        self._buffer.extend(data)

        while True:
            # If buffer doesn't start with END, find first END and discard garbage
            try:
                first_end = self._buffer.index(END[0])
                # Discard everything before the first END as garbage/misalignment
                self._buffer = self._buffer[first_end:]
            except ValueError:
                # No END byte found, clear buffer and wait for more data
                break

            # Now buffer starts with END, find the closing END
            if len(self._buffer) < 2:
                # Need at least 2 bytes to have a complete packet
                break

            try:
                # Search for closing END (starting from position 1)
                closing_end = self._buffer.index(END[0], 1)
            except ValueError:
                # No closing END found yet, wait for more data
                break

            # Extract the complete SLIP packet (including both END bytes)
            slip_packet = bytes(self._buffer[: closing_end + 1])
            self._buffer = self._buffer[closing_end + 1 :]

            # Skip empty packets (double END bytes - these are packet separators)
            if slip_packet == END + END:
                # Add an END back to the buffer to maintain alignment
                self._buffer.insert(0, END[0])
                continue

            # Decode and yield the packet
            try:
                packet = self._unframe(slip_packet)
                if packet:  # Only yield non-empty packets
                    yield packet
            except SLIPError:
                # Skip malformed packets and continue processing
                continue

    def clear_buffer(self) -> None:
        """Clear the internal receive buffer.

        Useful when resetting the connection or recovering from errors.
        """
        self._buffer.clear()

    @staticmethod
    def _is_valid_slip(packet: bytes) -> bool:
        """Check if a packet is valid according to SLIP protocol.

        A valid SLIP packet:
        - Contains no unescaped END bytes except at boundaries
        - Each ESC byte is followed by ESC_END or ESC_ESC
        - Does not end with a trailing ESC byte

        Args:
            packet: SLIP packet to validate

        Returns:
            True if valid, False otherwise
        """
        # Strip boundary END bytes
        inner = packet.strip(END)

        # Check for unescaped END bytes in the middle
        if END[0] in inner:
            return False

        # Check for trailing ESC
        if inner.endswith(ESC):
            return False

        # Check that all ESC bytes are properly followed
        i = 0
        while i < len(inner):
            if inner[i : i + 1] == ESC:
                if i + 1 >= len(inner):
                    return False  # ESC at end
                next_byte = inner[i + 1 : i + 2]
                if next_byte not in (ESC_END, ESC_ESC):
                    return False  # Invalid escape sequence
                i += 2
            else:
                i += 1

        return True
