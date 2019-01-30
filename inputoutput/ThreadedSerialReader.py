from threading import Thread

from inputoutput.SerialPort import SerialPort


class ThreadedSerialReader(Thread):
    def __init__(self, port_name, read_callback):
        super().__init__()
        self.terminate = False
        self.port = SerialPort(port_name)
        self.read_callback = read_callback

    def kill(self):
        self.terminate = True

    def run(self):
        if not self.port.open_serial_gracefully():
            return

        while not self.terminate:
            if not self.port.is_open and not self.port.open_serial_gracefully():
                return

            try:
                serial_data = self.port.read_all()
                decoded_data = str(serial_data.decode("UTF-8"))
                self.read_callback(decoded_data)
            except UnicodeDecodeError:
                print("Unable to decode scan.")
                continue

        print("SerialReader thread exiting...")
        self.port.close()
