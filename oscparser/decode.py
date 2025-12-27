from typing import Iterator, cast

from oscparser.ctx import DataBuffer
from oscparser.encode import OSCFraming, OSCModes
from oscparser.framing.framer import Framer
from oscparser.framing.fullframer import FullFramer
from oscparser.framing.osc10 import OSC10Framer
from oscparser.framing.osc11 import OSC11Framer
from oscparser.processing.osc.handlers import register_osc_handlers
from oscparser.processing.osc.processing import OSCDispatcher
from oscparser.types import OSCPacket


class OSCDecoder:
    """Decoder for OSC packets."""

    def __init__(self, mode: OSCModes, framing: OSCFraming):
        """Initialize the decoder.

        Args:
            mode: Transport mode, either 'udp' or 'tcp'
            framing: Framing type, either 'osc10' or 'osc11'
        """
        self.framer = self.get_framer(mode, framing)
        self.decoder = self.get_decoder()

    @staticmethod
    def get_decoder() -> OSCDispatcher:
        """Get an OSCDispatcher configured with standard handlers.

        Returns:
            An OSCDispatcher instance with registered handlers
        """
        dispatcher = OSCDispatcher()
        register_osc_handlers(dispatcher)
        return dispatcher

    @staticmethod
    def get_framer(mode: OSCModes, framing: OSCFraming) -> Framer:
        """Get the appropriate framer class based on mode and framing.

        Args:
            mode: Transport mode (UDP or TCP)
            framing: Framing type (OSC10 or OSC11)

        Returns:
            The corresponding framer instance
        """
        if mode == OSCModes.UDP:
            return FullFramer()
        elif mode == OSCModes.TCP:
            if framing == OSCFraming.OSC10:
                return OSC10Framer()
            elif framing == OSCFraming.OSC11:
                return OSC11Framer()
        raise ValueError("Unsupported mode or framing type")

    def decode(self, data: bytes) -> Iterator[OSCPacket]:
        """Feed data into the decoder and yield decoded OSC packets.

        For streaming TCP connections where data arrives in chunks.

        Args:
            data: Raw bytes received from socket

        Yields:
            Decoded OSC packets
        """
        # Unframe the data to get complete OSC packets
        for packet_data in self.framer.feed(data):
            # Decode each complete packet
            data_buffer = DataBuffer(packet_data)
            handler = self.decoder.get_handler(data_buffer)
            yield cast(OSCPacket, handler.decode(data_buffer))

    def clear_buffer(self) -> None:
        """Clear the internal framer buffer.

        Useful when resetting the connection or recovering from errors.
        """
        if hasattr(self.framer, "clear_buffer"):
            self.framer.clear_buffer()
