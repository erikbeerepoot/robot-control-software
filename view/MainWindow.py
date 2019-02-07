import functools

from traits.api import HasTraits, Instance
from traitsui.api import Item, View, HSplit

from view.RobotView import RobotView
from view.ScanPlotter import ScanPlotter

from inputoutput.SerialPort import SerialPort
from inputoutput.ProcessSerialReader import ProcessSerialReader
from inputoutput.ScanParser import ScanParser

from model.CommandPacket import *

class MainWindow(HasTraits):
    title = "ROBOT CONTROLS"
    robot_view = Instance(RobotView, ())
    scan_plot = Instance(ScanPlotter, ())

    view = View(
        HSplit(
            Item('scan_plot', style='custom'),
            Item('robot_view', style='custom'),
            show_labels=False,
        ),
        title="Robot Controls"
    )

    def __init__(self):
        super().__init__()
        # self.serial_port = SerialPort("/dev/tty.usbserial-FTVWEM2P")
        self.serial_port = SerialPort("/dev/tty.robot-RNI-SPP")
        self.scan_plot = ScanPlotter()
        self.robot_view = RobotView(velocity_callback=functools.partial(self.velocity_update, self.serial_port))

        self.reader = ProcessSerialReader(
            self.serial_port,
            functools.partial(self.process_scan_data, self.scan_plot)
        )
        self.parser = ScanParser()
        self.data = ''
        self.scan_count = 0

    def process_scan_data(self, plotter, new_data):
        self.data = self.data + str(new_data)
        scans, remaining_data = self.parser.parse_scan_data(str(self.data))
        self.data = str(remaining_data)

        if len(scans) > 0:
            plotter.plot_scan(scans[-1])

    def velocity_update(self, port, v_x, v_y):

        packet = VelocityPacket(v_x, v_y)
        data = packet.construct_bytes()
        port.send(data)

    def terminate(self):
        self.reader.kill()
        self.serial_port.close()
