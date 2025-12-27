from oscparser.decode import OSCDecoder
from oscparser.encode import OSCEncoder, OSCFraming, OSCModes
from oscparser.types import OSCArray, OSCFloat, OSCInt, OSCMessage, OSCString

message = OSCMessage(
    address="/test",
    args=(
        OSCArray(
            items=(
                OSCArray(
                    items=(
                        OSCInt(value=1),
                        OSCInt(value=2),
                        OSCInt(value=3),
                    )
                ),
                OSCArray(
                    items=(
                        OSCFloat(value=1.1),
                        OSCFloat(value=2.2),
                        OSCFloat(value=3.3),
                    )
                ),
                OSCString(value="hello"),
                OSCInt(value=42),
                OSCFloat(value=3.14),
            )
        ),
    ),
)


encoder = OSCEncoder(mode=OSCModes.TCP, framing=OSCFraming.OSC11)
encoded_data = encoder.encode(message)

print(encoded_data)
decoder = OSCDecoder(mode=OSCModes.TCP, framing=OSCFraming.OSC11)
index = 0
while 1:
    for message in decoder.decode(encoded_data[index : index + 10]):
        print(message)
        break
    else:
        index += 10
        print("Index:", index)
        continue
    break
