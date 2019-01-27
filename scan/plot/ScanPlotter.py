import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("macosx")

from time import sleep

#
class ScanPlotter(object):
    def __init__(self):
        self.fig = plt.figure(figsize=(6, 6))
        self.ax = plt.subplot(111, projection='polar')
        self.bars = None
        self.background = None
        self.index = 0

    def terminate(self):
        plt.close('all')

    def call_back(self):
        while self.pipe.poll():
            command = self.pipe.recv()
            if command is None:
                self.terminate()
                return False
            else:
                scan = command
                self.plot_scan(scan)

        return True

    def __call__(self, pipe):
        # print("Starting ScanPlotter in separate process...")
        self.pipe = pipe

        while True:
            self.call_back()

    def convert_data(scan):
        N = len(scan.payload)
        ranges = []
        angles = []
        for step in range(0, N):
            r = scan.payload[step]
            angle = scan.get_scan_angle(step)
            ranges.append(r)
            angles.append(angle)
        return angles, ranges

    def plot_scan(self, scan):
        angles, ranges = ScanPlotter.convert_data(scan)
        if self.bars is None:
            self.bars = self.ax.bar(angles, ranges, width=0.1)
            self.fig.canvas.draw()
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        else:
            self.fig.canvas.restore_region(self.background)
            for bar, r in zip(self.bars, ranges):
                bar.set_height(r)
                bar.set_facecolor('r')
                self.ax.draw_artist(bar)
            self.fig.canvas.draw()
        plt.pause(0.05)