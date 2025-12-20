# Python OSC Client

Open Sound Control client implementations.

## Current status

This library was developed following the
[OpenSoundControl Specification 1.0](https://opensoundcontrol.stanford.edu/spec-1_0.html)
and is currently in a stable state.

## Features

* UDP and TCP clients, including asyncio support
* TCP support for 1.0 and 1.1 protocol formats
* int, int64, float, string, double, MIDI, timestamps, blob, nil OSC arguments
* simple OSC address<->callback matching system
* support for sending responses from callback handlers in client and server
* extensive unit test coverage
* basic client examples

## Documentation

Available at In the documentation section of the gitlab repository.


## Examples

Please ignore these code snippets until current refractoring is done.

### Simple client

```python
"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time

from pythonosc import udp_client


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5005,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

  for x in range(10):
    client.send_message("/filter", random.random())
    time.sleep(1)
```


### Building bundles

```python
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder

bundle = osc_bundle_builder.OscBundleBuilder(
    osc_bundle_builder.IMMEDIATELY)
msg = osc_message_builder.OscMessageBuilder(address="/SYNC")
msg.add_arg(4.0)
# Add 4 messages in the bundle, each with more arguments.
bundle.add_content(msg.build())
msg.add_arg(2)
bundle.add_content(msg.build())
msg.add_arg("value")
bundle.add_content(msg.build())
msg.add_arg(b"\x01\x02\x03")
bundle.add_content(msg.build())

sub_bundle = bundle.build()
# Now add the same bundle inside itself.
bundle.add_content(sub_bundle)
# The bundle has 5 elements in total now.

bundle = bundle.build()
# You can now send it via a client with the `.send()` method:
client.send(bundle)
```

## License?

This software is licensed under the MIT License. See the LICENSE file for details.