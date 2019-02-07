import multiprocessing as mp
import functools

from view.ScanPlotter import ScanPlotter
from inputoutput.ScanParser import ScanParser

from view.MainWindow import MainWindow
from inputoutput.ProcessSerialReader import ProcessSerialReader
from inputoutput.SimulatedScanStreamer import SimulatedScanStreamer



data = ''
scan_count = 0


def plot_scan(plotter, scan):
    global scan_count
    plotter.plot_scan(scan)


if __name__ == "__main__":
    mp.set_start_method('spawn')

    window = MainWindow()

    simulated = True
    # if simulated:
    #     # Non-functional
    #     streamer = SimulatedScanStreamer(functools.partial(plot_scan, window.scan_plot))
    #     streamer.start()
    #
    #     window.configure_traits()
    #
    #     streamer.kill()
    #     streamer.join()
    # else:
    window.configure_traits()
    window.terminate()




    print(f"Processed {scan_count} scans.")
    print("Done.")
