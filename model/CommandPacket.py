from PyCRC.CRC32 import CRC32


class CommandPacket:
    crc = CRC32()
    command = ""
    payload = ""
    checksum = 0

    def __init__(self):
        pass

    def construct_bytes(self):
        return f"{self.command}\n{self.payload}\n{self.construct_checksum()}\n\n".encode("UTF-8")

    def construct_checksum(self):
        return self.crc.calculate(self.payload)


class VelocityPacket(CommandPacket):
    def __init__(self, v_x, v_y):
        super().__init__()
        self.command = "CV"
        self.payload = f"{v_x:+1.03f}{v_y:+1.03f}"


class ToggleScanPacket(CommandPacket):
    def __init__(self, state):
        super().__init__()
        self.command = "CS"
        self.payload = "1" if state else "0"

