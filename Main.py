from threading import Thread

import tenacity
from numpy import *
from pynput import keyboard

from comm.SerialPort import SerialPort
from scan.plot.ScanPlotter import ScanPlotter
from scan.tools.ScanParser import ScanParser
from scan.tools.ScanReaderWriter import ScanReaderWriter


def on_release(key):
    global break_loop
    if key == keyboard.Key.esc:
        # Stop listener
        break_loop = True
        return False


def load_scans_from_file():
    scan_r_w = ScanReaderWriter("~/Documents/scans.dat")
    scans, _ = scan_r_w.load_scans()
    return scans

    # plotter.plot_scan(scans[0])
    # for scan in scans:


class SerialReader(Thread):
    def __init__(self, port_name, read_callback):
        super().__init__()
        self.terminate = False
        self.port = SerialPort(port_name)
        self.read_callback = read_callback

    def kill(self):
        self.terminate = True

    def run(self):
        if not self.open_serial_gracefully():
            return

        while not self.terminate:
            if not self.port.is_open and not self.open_serial_gracefully():
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

    def open_serial_gracefully(self):
        print("Opening serial port...", end='', flush=True)
        try:
            self.port.open()
        except tenacity.RetryError:
            pass

        print(f"{'success' if self.port.is_open else 'failure'}.")
        return self.port.is_open


plotter = ScanPlotter()
parser = ScanParser()
data = ''


def process_scan_data(new_data):
    global data
    scans, remaining_data = parser.parse_scan_data(str(new_data))
    data = data + str(remaining_data)
    [plotter.plot_scan(scan) for scan in scans]


if __name__ == "__main__":
    reader = SerialReader("/dev/tty.usbserial-FTVWEM2P", process_scan_data)
    reader.start()

    plotter.configure_traits()
    reader.kill()
    reader.join()
    print("Done.")
