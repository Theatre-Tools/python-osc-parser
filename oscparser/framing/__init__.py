"""OSC framing support for OSC 1.0 (UDP) and OSC 1.1 (TCP/SLIP)."""

from oscparser.framing.osc10 import OSC10Framer
from oscparser.framing.osc11 import OSC11Framer

__all__ = ["OSC10Framer", "OSC11Framer"]
