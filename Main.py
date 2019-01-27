import multiprocessing as mp

import tenacity
from pynput import keyboard

from scan.plot.ScanPlotter import ScanPlotter
from scan.tools.ScanParser import ScanParser
from scan.tools.ScanReaderWriter import ScanReaderWriter
from comm.SerialPort import  SerialPort

break_loop = False


class ScanPipe:
    def __init__(self):
        mp.set_start_method('spawn')

        self.parent_connection, self.child_connection = mp.Pipe()
        self.plotter = ScanPlotter()
        self.plot_process = mp.Process(
            target=self.plotter,
            args=(self.child_connection,)

        )
        self.plot_process.start()

    def plot(self, new_scans, finished=False):
        send = self.parent_connection.send
        if finished:
            send(None)
        else:
            [send(scan) for scan in new_scans]

    def terminate(self):
        self.plot_process.join()


def on_release(key):
    global break_loop
    if key == keyboard.Key.esc:
        # Stop listener
        break_loop = True
        return False


def plot_scans_from_file():
    scan_r_w = ScanReaderWriter("~/Documents/scans.dat")
    scans, _ = scan_r_w.load_scans()


if __name__ == "__main__":
    # plot_scans_from_file()

    port = SerialPort()
    plotter = ScanPlotter()
    pipe = ScanPipe()
    try:
        # Open bluetooth port to stream scans
        # port_name = "/dev/tty.robot-RNI-SPP"
        port_name = "/dev/tty.usbserial-FTVWEM2P"
        port.open(port_name)

        parser = ScanParser()
        data = ''
        if port.port.is_open:
            while True:
                if break_loop:
                    break

                if not port.port.is_open:
                    port.open(port_name)

                serial_data = port.read_all()

                # Process scans in the buffer, and return the remaining data for the next loop
                try:
                    data = str(serial_data.decode("UTF-8"))

                    scans, data = parser.parse_scan_data(data)

                    if len(scans) > 0:
                        plotter.plot_scan(scans[0])

                except UnicodeDecodeError:
                    continue

        port.close()
        # pipe.terminate()
    except tenacity.RetryError:
        print("Maximum number of retries exceeded. Giving up.")
    finally:
        print("Done.")
