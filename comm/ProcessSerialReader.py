import multiprocessing as mp
from threading import Thread

from comm.SerialPort import SerialPort

class ProcessSerialReader:
    def __init__(self, port_name, read_callback):
        self.parent_conn, child_conn = mp.Pipe()

        port = SerialPort(port_name)
        self.process = mp.Process(target=ProcessSerialReader.read_serial, args=(child_conn, port))


        # self.read_callback = read_callback

        self.reader = ReaderThread(read_callback, self.parent_conn)
        self.reader.start()
        self.process.start()

    @staticmethod
    def read_serial(conn, port):
        print("Started reader process.")
        if not port.open_serial_gracefully():
            return

        while True:
            if conn.poll(timeout=0.01):
                received = conn.recv()
                if not received:
                    break

            if not port.is_open and not port.open_serial_gracefully():
                return

            try:
                serial_data = port.read_all()
                decoded_data = str(serial_data.decode("UTF-8"))
                conn.send(decoded_data)
            except UnicodeDecodeError:
                print("Unable to decode scan.")
                continue

        port.close()
        print("SerialReader thread exited..")

    def kill(self):
        self.parent_conn.send(False)
        self.reader.kill()
        self.reader.join()


class ReaderThread(Thread):
    terminate = False

    def __init__(self, read_callback, conn):
        super().__init__()
        self.read_callback = read_callback
        self.conn = conn

    def run(self):
        print("Started reader thread.")
        while not self.terminate:
            if self.conn.poll():
                received = self.conn.recv()
                if received is not None:
                    self.read_callback(received)

        print("Exited reader thread.")

    def kill(self):
        self.terminate = True
3