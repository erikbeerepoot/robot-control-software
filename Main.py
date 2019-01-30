import multiprocessing as mp
import functools

from view.ScanPlotter import ScanPlotter
from inputoutput.ScanParser import ScanParser

from view.MainWindow import MainWindow
from inputoutput.ProcessSerialReader import ProcessSerialReader
from inputoutput.SimulatedScanStreamer import SimulatedScanStreamer


parser = ScanParser()
data = ''
scan_count = 0


def plot_scan(plotter, scan):
    global scan_count
    plotter.plot_scan(scan)


def process_scan_data(plotter, new_data):
    global data, scan_count
    scans, remaining_data = parser.parse_scan_data(str(new_data))
    data = data + str(remaining_data)
    scan_count += len(scans)

    if len(scans) > 0:
        plotter.plot_scan(scans[-1])


if __name__ == "__main__":
    mp.set_start_method('spawn')

    window = MainWindow()



    simulated = True
    if simulated:
        # Non-functional
        streamer = SimulatedScanStreamer(functools.partial(plot_scan, window.scan_plot))
        streamer.start()

        window.configure_traits()

        streamer.kill()
        streamer.join()
    else:
        reader = ProcessSerialReader("/dev/tty.usbserial-FTVWEM2P", process_scan_data)
        # reader = ProcessSerialReader("/dev/tty.robot-RNI-SPP", process_scan_data)

        # plotter.configure_traits()
        window.configure_traits()

        reader.kill()

    print(f"Processed {scan_count} scans.")
    print("Done.")
