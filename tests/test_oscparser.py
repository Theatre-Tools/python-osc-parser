"""Tests for oscparser encode/decode functionality with real binary OSC data.

This test suite uses real OSC binary datagrams from various sources to ensure
compatibility and correctness of the oscparser implementation.
"""

import unittest

from oscparser import (
    OSCArray,
    OSCBlob,
    OSCBundle,
    OSCDecoder,
    OSCEncoder,
    OSCFalse,
    OSCFloat,
    OSCFraming,
    OSCInt,
    OSCInt64,
    OSCMessage,
    OSCModes,
    OSCNil,
    OSCString,
    OSCTrue,
)
from oscparser.ctx import DataBuffer
from oscparser.processing.osc.handlers import register_osc_handlers
from oscparser.processing.osc.processing import OSCDispatcher

# Real OSC datagrams from Reaktor 5.8 by Native Instruments
_DGRAM_KNOB_ROTATES = b"/FB\x00,f\x00\x00>xca=q"

_DGRAM_SWITCH_GOES_OFF = b"/SYNC\x00\x00\x00,f\x00\x00\x00\x00\x00\x00"

_DGRAM_SWITCH_GOES_ON = b"/SYNC\x00\x00\x00,f\x00\x00?\x00\x00\x00"

_DGRAM_NO_PARAMS = b"/SYNC\x00\x00\x00"

_DGRAM_ALL_STANDARD_TYPES_OF_PARAMS = (
    b"/SYNC\x00\x00\x00"
    b",ifsb\x00\x00\x00"
    b"\x00\x00\x00\x03"  # 3
    b"@\x00\x00\x00"  # 2.0
    b"ABC\x00"  # "ABC"
    b"\x00\x00\x00\x08stuff\x00\x00\x00"
)  # b"stuff\x00\x00\x00"

_DGRAM_ALL_NON_STANDARD_TYPES_OF_PARAMS = (
    b"/SYNC\x00\x00\x00"
    b",TFN[]th\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\xe8\xd4\xa5\x10\x00"  # 1000000000000
)

_DGRAM_COMPLEX_ARRAY_PARAMS = (
    b"/SYNC\x00\x00\x00"
    b",[i][[ss]][[i][i[s]]]\x00\x00\x00"
    b"\x00\x00\x00\x01"  # 1
    b"ABC\x00"  # "ABC"
    b"DEF\x00"  # "DEF"
    b"\x00\x00\x00\x02"  # 2
    b"\x00\x00\x00\x03"  # 3
    b"GHI\x00"
)  # "GHI"

# Bundle datagrams
_DGRAM_KNOB_ROTATES_BUNDLE = (
    b"#bundle\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x14/LFO_Rate\x00\x00\x00,f\x00\x00>\x8c\xcc\xcd"
)

_DGRAM_SWITCH_GOES_OFF_BUNDLE = (
    b"#bundle\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x10/SYNC\x00\x00\x00,f\x00\x00\x00\x00\x00\x00"
)

_DGRAM_TWO_MESSAGES_IN_BUNDLE = (
    b"#bundle\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x01"
    # First message.
    b"\x00\x00\x00\x10"
    b"/SYNC\x00\x00\x00"
    b",f\x00\x00"
    b"?\x00\x00\x00"
    # Second message, same.
    b"\x00\x00\x00\x10"
    b"/SYNC\x00\x00\x00"
    b",f\x00\x00"
    b"?\x00\x00\x00"
)

_DGRAM_BUNDLE_IN_BUNDLE = (
    b"#bundle\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x01"
    b"\x00\x00\x00("  # length of sub bundle: 40 bytes.
    b"#bundle\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x01"
    b"\x00\x00\x00\x10"
    b"/SYNC\x00\x00\x00"
    b",f\x00\x00"
    b"?\x00\x00\x00"
)


class TestOSCParserWithBinaryData(unittest.TestCase):
    """Test oscparser with real binary OSC data."""

    def setUp(self):
        """Set up decoder for tests."""
        self.dispatcher = OSCDispatcher()
        register_osc_handlers(self.dispatcher)

    def _decode_packet(self, dgram: bytes):
        """Helper to decode a raw OSC packet."""
        buffer = DataBuffer(dgram)
        handler = self.dispatcher.get_handler(buffer)
        return handler.decode(buffer)

    def test_decode_knob_rotates(self):
        """Test decoding a message with float parameter."""
        msg = self._decode_packet(_DGRAM_KNOB_ROTATES)
        self.assertIsInstance(msg, OSCMessage)
        self.assertEqual("/FB", msg.address)
        self.assertEqual(1, len(msg.args))
        self.assertIsInstance(msg.args[0], OSCFloat)

    def test_decode_switch_goes_off(self):
        """Test decoding a message with float 0.0."""
        msg = self._decode_packet(_DGRAM_SWITCH_GOES_OFF)
        self.assertIsInstance(msg, OSCMessage)
        self.assertEqual("/SYNC", msg.address)
        self.assertEqual(1, len(msg.args))
        self.assertIsInstance(msg.args[0], OSCFloat)
        self.assertAlmostEqual(0.0, msg.args[0].value)

    def test_decode_switch_goes_on(self):
        """Test decoding a message with float 0.5."""
        msg = self._decode_packet(_DGRAM_SWITCH_GOES_ON)
        self.assertIsInstance(msg, OSCMessage)
        self.assertEqual("/SYNC", msg.address)
        self.assertEqual(1, len(msg.args))
        self.assertIsInstance(msg.args[0], OSCFloat)
        self.assertAlmostEqual(0.5, msg.args[0].value)

    def test_decode_no_params(self):
        """Test decoding a message with no parameters."""
        msg = self._decode_packet(_DGRAM_NO_PARAMS)
        self.assertIsInstance(msg, OSCMessage)
        self.assertEqual("/SYNC", msg.address)
        self.assertEqual(0, len(msg.args))

    def test_decode_all_standard_types(self):
        """Test decoding message with int, float, string, and blob."""
        msg = self._decode_packet(_DGRAM_ALL_STANDARD_TYPES_OF_PARAMS)
        self.assertIsInstance(msg, OSCMessage)
        self.assertEqual("/SYNC", msg.address)
        self.assertEqual(4, len(msg.args))

        # Int
        self.assertIsInstance(msg.args[0], OSCInt)
        self.assertEqual(3, msg.args[0].value)

        # Float
        self.assertIsInstance(msg.args[1], OSCFloat)
        self.assertAlmostEqual(2.0, msg.args[1].value)

        # String
        self.assertIsInstance(msg.args[2], OSCString)
        self.assertEqual("ABC", msg.args[2].value)

        # Blob
        self.assertIsInstance(msg.args[3], OSCBlob)
        self.assertEqual(b"stuff\x00\x00\x00", msg.args[3].value)

    def test_decode_all_non_standard_params(self):
        """Test decoding message with True, False, Nil, empty array, timetag, and int64."""
        msg = self._decode_packet(_DGRAM_ALL_NON_STANDARD_TYPES_OF_PARAMS)
        self.assertIsInstance(msg, OSCMessage)
        self.assertEqual("/SYNC", msg.address)
        self.assertEqual(6, len(msg.args))

        # True
        self.assertIsInstance(msg.args[0], OSCTrue)

        # False
        self.assertIsInstance(msg.args[1], OSCFalse)

        # Nil
        self.assertIsInstance(msg.args[2], OSCNil)

        # Empty array
        self.assertIsInstance(msg.args[3], OSCArray)
        self.assertEqual(0, len(msg.args[3].items))

        # Timetag (skip for now - requires datetime handling)

        # Int64
        self.assertIsInstance(msg.args[5], OSCInt64)
        self.assertEqual(1000000000000, msg.args[5].value)

    def test_decode_complex_array_params(self):
        """Test decoding message with nested arrays."""
        msg = self._decode_packet(_DGRAM_COMPLEX_ARRAY_PARAMS)
        self.assertIsInstance(msg, OSCMessage)
        self.assertEqual("/SYNC", msg.address)
        self.assertEqual(3, len(msg.args))

        # [1]
        self.assertIsInstance(msg.args[0], OSCArray)
        self.assertEqual(1, len(msg.args[0].items))
        self.assertIsInstance(msg.args[0].items[0], OSCInt)
        self.assertEqual(1, msg.args[0].items[0].value)

        # [["ABC", "DEF"]]
        self.assertIsInstance(msg.args[1], OSCArray)
        self.assertEqual(1, len(msg.args[1].items))
        self.assertIsInstance(msg.args[1].items[0], OSCArray)
        self.assertEqual(2, len(msg.args[1].items[0].items))

        # [[2], [3, ["GHI"]]]
        self.assertIsInstance(msg.args[2], OSCArray)
        self.assertEqual(2, len(msg.args[2].items))

    def test_decode_bundle_knob_rotates(self):
        """Test decoding a bundle with one message."""
        bundle = self._decode_packet(_DGRAM_KNOB_ROTATES_BUNDLE)
        self.assertIsInstance(bundle, OSCBundle)
        self.assertEqual(1, len(bundle.elements))
        self.assertIsInstance(bundle.elements[0], OSCMessage)
        self.assertEqual("/LFO_Rate", bundle.elements[0].address)

    def test_decode_bundle_with_two_messages(self):
        """Test decoding a bundle with two messages."""
        bundle = self._decode_packet(_DGRAM_TWO_MESSAGES_IN_BUNDLE)
        self.assertIsInstance(bundle, OSCBundle)
        self.assertEqual(2, len(bundle.elements))
        self.assertIsInstance(bundle.elements[0], OSCMessage)
        self.assertIsInstance(bundle.elements[1], OSCMessage)
        self.assertEqual("/SYNC", bundle.elements[0].address)
        self.assertEqual("/SYNC", bundle.elements[1].address)

    def test_decode_bundle_in_bundle(self):
        """Test decoding nested bundles."""
        bundle = self._decode_packet(_DGRAM_BUNDLE_IN_BUNDLE)
        self.assertIsInstance(bundle, OSCBundle)
        self.assertEqual(1, len(bundle.elements))
        self.assertIsInstance(bundle.elements[0], OSCBundle)
        sub_bundle = bundle.elements[0]
        self.assertEqual(1, len(sub_bundle.elements))
        self.assertIsInstance(sub_bundle.elements[0], OSCMessage)

    def test_encode_decode_roundtrip_message(self):
        """Test encoding then decoding a message preserves data."""
        original = OSCMessage(
            address="/test/addr",
            args=(
                OSCInt(value=42),
                OSCFloat(value=3.14),
                OSCString(value="hello"),
                OSCBlob(value=b"binary\x00data"),
            ),
        )

        # Encode
        buffer = DataBuffer(b"")
        self.dispatcher.get_object_handler(OSCMessage).encode(original, buffer)
        encoded = buffer.data

        # Decode
        decoded = self._decode_packet(encoded)

        # Verify
        self.assertEqual(original.address, decoded.address)
        self.assertEqual(len(original.args), len(decoded.args))
        self.assertEqual(original.args[0].value, decoded.args[0].value)
        self.assertAlmostEqual(original.args[1].value, decoded.args[1].value, places=5)
        self.assertEqual(original.args[2].value, decoded.args[2].value)
        self.assertEqual(original.args[3].value, decoded.args[3].value)

    def test_encode_decode_roundtrip_bundle(self):
        """Test encoding then decoding a bundle preserves data."""
        msg1 = OSCMessage(address="/msg1", args=(OSCInt(value=1),))
        msg2 = OSCMessage(address="/msg2", args=(OSCFloat(value=2.0),))

        original = OSCBundle(timetag=0, elements=(msg1, msg2))

        # Encode
        buffer = DataBuffer(b"")
        self.dispatcher.get_object_handler(OSCBundle).encode(original, buffer)
        encoded = buffer.data

        # Decode
        decoded = self._decode_packet(encoded)

        # Verify
        self.assertIsInstance(decoded, OSCBundle)
        self.assertEqual(original.timetag, decoded.timetag)
        self.assertEqual(len(original.elements), len(decoded.elements))
        self.assertEqual(original.elements[0].address, decoded.elements[0].address)
        self.assertEqual(original.elements[1].address, decoded.elements[1].address)


class TestOSCEncoderDecoder(unittest.TestCase):
    """Test OSCEncoder and OSCDecoder classes."""

    def test_udp_encode_decode(self):
        """Test UDP encoding and decoding."""
        encoder = OSCEncoder(OSCModes.UDP, OSCFraming.OSC10)
        decoder = OSCDecoder(OSCModes.UDP, OSCFraming.OSC10)

        original = OSCMessage(address="/test", args=(OSCInt(value=123), OSCString(value="test")))

        # Encode
        encoded = encoder.encode(original)

        # Decode - feed returns a generator
        decoded_msgs = list(decoder.decode(encoded))
        self.assertEqual(1, len(decoded_msgs))
        decoded = decoded_msgs[0]

        # Verify
        self.assertEqual(original.address, decoded.address)
        self.assertEqual(len(original.args), len(decoded.args))

    def test_tcp_osc10_encode_decode(self):
        """Test TCP OSC 1.0 (length-prefixed) encoding and decoding."""
        encoder = OSCEncoder(OSCModes.TCP, OSCFraming.OSC10)
        decoder = OSCDecoder(OSCModes.TCP, OSCFraming.OSC10)

        original = OSCMessage(address="/tcp/test", args=(OSCFloat(value=1.5), OSCString(value="data")))

        # Encode
        encoded = encoder.encode(original)

        # Verify it has the 4-byte length prefix
        self.assertTrue(len(encoded) > 4)

        # Decode - feed returns a generator
        decoded_msgs = list(decoder.decode(encoded))
        self.assertEqual(1, len(decoded_msgs))
        decoded = decoded_msgs[0]

        # Verify
        self.assertEqual(original.address, decoded.address)
        self.assertEqual(len(original.args), len(decoded.args))

    def test_tcp_osc11_encode_decode(self):
        """Test TCP OSC 1.1 (SLIP) encoding and decoding."""
        encoder = OSCEncoder(OSCModes.TCP, OSCFraming.OSC11)
        decoder = OSCDecoder(OSCModes.TCP, OSCFraming.OSC11)

        original = OSCMessage(address="/slip/test", args=(OSCInt(value=999), OSCString(value="slip")))

        # Encode
        encoded = encoder.encode(original)

        # Verify SLIP framing (should start and end with 0xc0)
        self.assertEqual(0xC0, encoded[0])
        self.assertEqual(0xC0, encoded[-1])

        # Decode - feed returns a generator
        decoded_msgs = list(decoder.decode(encoded))
        self.assertEqual(1, len(decoded_msgs))
        decoded = decoded_msgs[0]

        # Verify
        self.assertEqual(original.address, decoded.address)
        self.assertEqual(len(original.args), len(decoded.args))

    def test_tcp_streaming_multiple_packets(self):
        """Test streaming multiple TCP packets."""
        encoder = OSCEncoder(OSCModes.TCP, OSCFraming.OSC10)
        decoder = OSCDecoder(OSCModes.TCP, OSCFraming.OSC10)

        msg1 = OSCMessage(address="/msg1", args=(OSCInt(value=1),))
        msg2 = OSCMessage(address="/msg2", args=(OSCInt(value=2),))
        msg3 = OSCMessage(address="/msg3", args=(OSCInt(value=3),))

        # Encode all messages
        encoded1 = encoder.encode(msg1)
        encoded2 = encoder.encode(msg2)
        encoded3 = encoder.encode(msg3)

        # Concatenate as if received in stream
        stream = encoded1 + encoded2 + encoded3

        # Decode stream
        decoded_msgs = list(decoder.decode(stream))

        # Verify
        self.assertEqual(3, len(decoded_msgs))
        self.assertEqual("/msg1", decoded_msgs[0].address)
        self.assertEqual("/msg2", decoded_msgs[1].address)
        self.assertEqual("/msg3", decoded_msgs[2].address)

    def test_tcp_streaming_partial_packets(self):
        """Test streaming with packets arriving in chunks."""
        encoder = OSCEncoder(OSCModes.TCP, OSCFraming.OSC10)
        decoder = OSCDecoder(OSCModes.TCP, OSCFraming.OSC10)

        msg = OSCMessage(address="/partial", args=(OSCString(value="test data"),))
        encoded = encoder.encode(msg)

        # Split encoded data into chunks
        chunk1 = encoded[: len(encoded) // 2]
        chunk2 = encoded[len(encoded) // 2 :]

        # Feed first chunk - should not yield anything
        msgs1 = list(decoder.decode(chunk1))
        self.assertEqual(0, len(msgs1))

        # Feed second chunk - should yield the complete message
        msgs2 = list(decoder.decode(chunk2))
        self.assertEqual(1, len(msgs2))
        self.assertEqual("/partial", msgs2[0].address)

    def test_bundle_encode_decode(self):
        """Test encoding and decoding bundles."""
        encoder = OSCEncoder(OSCModes.UDP, OSCFraming.OSC10)
        decoder = OSCDecoder(OSCModes.UDP, OSCFraming.OSC10)

        msg1 = OSCMessage(address="/a", args=(OSCInt(value=1),))
        msg2 = OSCMessage(address="/b", args=(OSCInt(value=2),))
        bundle = OSCBundle(timetag=1234567890, elements=(msg1, msg2))

        # Encode
        encoded = encoder.encode(bundle)

        # Decode - feed returns a generator
        decoded_bundles = list(decoder.decode(encoded))
        self.assertEqual(1, len(decoded_bundles))
        decoded = decoded_bundles[0]

        # Verify
        self.assertIsInstance(decoded, OSCBundle)
        self.assertEqual(bundle.timetag, decoded.timetag)
        self.assertEqual(2, len(decoded.elements))

    def test_binary_data_with_special_bytes(self):
        """Test encoding/decoding binary data containing SLIP special bytes."""
        encoder = OSCEncoder(OSCModes.TCP, OSCFraming.OSC11)
        decoder = OSCDecoder(OSCModes.TCP, OSCFraming.OSC11)

        # Create blob with SLIP special bytes (0xc0, 0xdb)
        special_data = b"\x00\xc0\xdb\xff\xc0\xdb\x00"
        msg = OSCMessage(address="/binary", args=(OSCBlob(value=special_data),))

        # Encode
        encoded = encoder.encode(msg)

        # Decode - feed returns a generator
        decoded_msgs = list(decoder.decode(encoded))
        self.assertEqual(1, len(decoded_msgs))
        decoded = decoded_msgs[0]

        # Verify binary data is preserved
        self.assertIsInstance(decoded.args[0], OSCBlob)
        self.assertEqual(special_data, decoded.args[0].value)


if __name__ == "__main__":
    unittest.main()
