from numpy import *

from comm.SerialReader import SerialReader
from scan.plot.ScanPlotter import ScanPlotter
from scan.tools.ScanParser import ScanParser
from scan.tools.SimulatedScanStreamer import SimulatedScanStreamer

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
