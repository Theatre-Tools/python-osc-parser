from enum import Enum

from oscparser.ctx import DataBuffer
from oscparser.framing.framer import Framer
from oscparser.framing.fullframer import FullFramer
from oscparser.framing.osc10 import OSC10Framer
from oscparser.framing.osc11 import OSC11Framer
from oscparser.processing.osc.handlers import register_osc_handlers
from oscparser.processing.osc.processing import OSCDispatcher
from oscparser.types import OSCPacket


class OSCModes(Enum):
    UDP = "udp"
    TCP = "tcp"


class OSCFraming(Enum):
    OSC10 = "osc10"
    OSC11 = "osc11"


class OSCEncoder:
    """Encoder for OSC packets."""

    def __init__(self, mode: OSCModes, framing: OSCFraming):
        """Initialize the framer.

        Args:
            mode: Transport mode, either 'udp' or 'tcp'
        """
        self.framer = self.get_framer(mode, framing)
        self.encoder = self.get_encoder()

    @staticmethod
    def get_encoder() -> OSCDispatcher:
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
            The corresponding framer class
        """
        if mode == OSCModes.UDP:
            return FullFramer()
        elif mode == OSCModes.TCP:
            if framing == OSCFraming.OSC10:
                return OSC10Framer()
            elif framing == OSCFraming.OSC11:
                return OSC11Framer()
        raise ValueError("Unsupported mode or framing type")

    def encode(self, packet: OSCPacket) -> bytes:
        """Encode and frame an OSC packet.

        Args:
            packet: The OSC packet to encode
        Returns:
            Framed OSC packet bytes
        """
        data_buffer = DataBuffer(b"")
        handler = self.encoder.get_object_handler(type(packet))
        handler.encode(packet, data_buffer)
        framed_packet = self.framer.frame(data_buffer.data)
        return framed_packet
