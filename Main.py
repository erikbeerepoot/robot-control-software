from threading import Thread
from time import sleep

import tenacity
from numpy import *

from comm.SerialPort import SerialPort
from scan.plot.ScanPlotter import ScanPlotter
from scan.tools.ScanParser import ScanParser
from scan.tools.ScanReaderWriter import ScanReaderWriter


class SimulatedScanStreamer(Thread):

    def __init__(self, read_callback):
        super().__init__()
        self.terminate = False
        self.scans = SimulatedScanStreamer.load_scans_from_file()
        self.read_callback = read_callback

    def kill(self):
        self.terminate = True

    @staticmethod
    def load_scans_from_file():
        scan_r_w = ScanReaderWriter("~/Documents/scans.dat")
        scans, _ = scan_r_w.load_scans()
        return scans

    def run(self):
        while not self.terminate:
            for scan in self.scans:
                self.read_callback(scan)
                sleep(0.05)

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
scan_count = 0

def plot_scan(scan):
    global scan_count
    plotter.plot_scan(scan)

def process_scan_data(new_data):
    global data, scan_count
    scans, remaining_data = parser.parse_scan_data(str(new_data))
    data = data + str(remaining_data)
    scan_count += len(scans)

    if len(scans) > 0:
        plotter.plot_scan(scans[0])
    # [ for scan in scans]


if __name__ == "__main__":
    simulated = True
    if simulated:
        # Non-functional
        streamer = SimulatedScanStreamer(plot_scan)
        streamer.start()

        plotter.configure_traits()

        streamer.kill()
        streamer.join()
    else:
        # reader = SerialReader("/dev/tty.usbserial-FTVWEM2P", process_scan_data)
        reader = SerialReader("/dev/tty.robot-RNI-SPP", process_scan_data)
        reader.start()

        plotter.configure_traits()

        reader.kill()
        reader.join()

    print(f"Processed {scan_count} scans.")
    print("Done.")
