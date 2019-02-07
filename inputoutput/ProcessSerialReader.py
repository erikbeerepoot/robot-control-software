import multiprocessing as mp
from threading import Thread
from time import sleep

from inputoutput.SerialPort import SerialPort


class ProcessSerialReader:
    def __init__(self, port, read_callback):
        self.parent_conn, child_conn = mp.Pipe()
        self.process = mp.Process(target=ProcessSerialReader.read_serial, args=(child_conn, port))
        self.reader = ReaderThread(read_callback, self.parent_conn)
        self.reader.start()
        self.process.start()

    @staticmethod
    def read_serial(conn, port):
        print("Started reader process.")
        if not port.open_serial_gracefully():
            return

        while True:
            if conn.poll(timeout=0.02):
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
            except BrokenPipeError:
                break

        port.close()
        print("SerialReader thread exited..")

    def kill(self):
        self.parent_conn.send(False)
        # self.sp.conn.send(True)
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
                try:
                    received = self.conn.recv()
                    if received is not None:
                        self.read_callback(received)
                except EOFError:
                    break
            else:
                sleep(0.1)
        print("Exited reader thread.")

    def kill(self):
        self.terminate = True

# Process-based implementation
# class ScanProcessor:
#     def __init__(self, read_callback, serial_conn):
#         self.conn, term_conn = mp.Pipe()
#         self.process = mp.Process(target=self.busy_read, args=(serial_conn, term_conn, read_callback))
#         self.process.start()
#
#     @property
#     def get_conn(self):
#         return self.conn
#
#     @staticmethod
#     def busy_read(serial_conn, term_conn, read_callback):
#         print("Starting read loop.")
#         while True:
#             if serial_conn.poll():
#                 received = serial_conn.recv()
#                 if received is not None:
#                     read_callback(received)
#
#             if term_conn.poll():
#                 received = term_conn.recv()
#                 if received:
#                     break
#
#         print("Exited read loop.")

