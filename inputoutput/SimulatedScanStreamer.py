from threading import Thread
from time import sleep

from inputoutput.ScanReaderWriter import ScanReaderWriter


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
