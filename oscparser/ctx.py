class DataBuffer:
    def __init__(self, data: bytes):
        self.data = data

    def startswith(self, prefix: bytes) -> bool:
        return self.data.startswith(prefix)

    def read(self, n: int) -> bytes:
        chunk = self.data[:n]
        self.data = self.data[n:]
        return chunk

    def write(self, data: bytes) -> None:
        self.data += data

    def remaining(self) -> int:
        return len(self.data)
