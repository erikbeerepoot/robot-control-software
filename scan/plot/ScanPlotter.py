import numpy as np
from chaco.api import ArrayPlotData, DataRange1D, Plot, LinearMapper
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View


class ScanPlotter(HasTraits):
    plot = Instance(Component)
    size = (600, 600)

    traits_view = View(
        Group(
            Item('plot', editor=ComponentEditor(size=size), show_label=False),
            orientation="vertical"
        ),
        resizable=True,
        width=size[0],
        height=size[1]
    )

    def __init__(self,
                 x_range=DataRange1D(low=-4000, high=4000),
                 y_range=DataRange1D(low=-4000, high=4000),
                 title="URG-04LX Laser Scan Live View"):
        '''
        Initializes the plotter
        :param x_range: The (min,max) range of the x values (+/- detection range)
        :param y_range: The (min,max) range of the y values (+/- detection range)
        '''
        super().__init__()
        self.x_range = x_range
        self.y_range = y_range
        self.plot = None
        self.title = title

    def convert_data(scan):
        '''
        Converts scan data from steps & distances to angles & distances
        :return: tuple containing the angles & distances in the form of lists
        '''
        ranges = []
        angles = []
        for step in range(0, len(scan.payload)):
            r = scan.payload[step]
            angle = scan.get_scan_angle(step)
            ranges.append(r)
            angles.append(angle)
        return angles, ranges

    def _plot_scan(self,
                   theta,
                   r,
                   marker_color='orange',
                   marker_size=1.0,
                   fill_color=(0, 1.0, 0, 0.8)):
        '''
        Plot a laser scan
        :param theta: The list of angles for this scan
        :param r: The list of ranges associated w/ the angles
        :param marker_color: The color of the marker indicating the "hit point"
        :param marker_size: The size of the marker indicating the "hit point"
        :param fill_color: The color of the polygon indicating the area swept out by the laser's rays
        '''
        index_data = r * np.cos(theta)
        value_data = r * np.sin(theta)
        plot_data = ArrayPlotData(index=index_data, value=value_data)

        if self.plot is None:
            # Create plot only once, update data otherwise and let
            # chaco handle the rest
            plot = Plot(plot_data)
            plot.range2d.x_range = self.x_range
            plot.range2d.y_range = self.y_range
            plot.x_mapper = LinearMapper(range=self.x_range)
            plot.y_mapper = LinearMapper(range=self.y_range)
            plot.title = self.title

            plot.plot(
                ('index', 'value'),
                type='scatter',
                marker='dot',
                marker_size=marker_size,
                color=marker_color
            )

            plot.plot(
                ('index', 'value'),
                type='polygon',
                marker="dot",
                marker_size=1,
                face_color=fill_color,
                edge_color=(0, 0, 0, 0.8),
            )

            self.plot = plot
        else:
            self.plot.data.set_data('index', plot_data["index"])
            self.plot.data.set_data('value', plot_data["value"])
            # self.plot.request_redraw()

    def plot_scan(self, scan):
        if scan is not None and scan.is_valid:
            theta, r = ScanPlotter.convert_data(scan)
            self._plot_scan(theta, r)
