import numpy as np
from chaco.api import DataRange1D, Plot, LinearMapper, ArrayPlotData
from enable.api import ComponentEditor, Line
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View


class RobotView(HasTraits):
    size = (300, 300)
    traits_view = View(
        Group(
            Item('plot', editor=ComponentEditor(size=size), show_label=False),
            orientation="vertical"
        ),
        resizable=True,
        width=size[0],
        height=size[1]
    )

    wheel_line = Instance(Line, args=())

    def __init__(self,
                 x_range=DataRange1D(low=0, high=300),
                 y_range=DataRange1D(low=0, high=300), *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.robot_bounding_box = {
            "x": [100, 200, 200, 100],
            "y": [80, 80, 220, 220]
        }

        self.robot_wheels = [
            {  # Bottom-left
                "x": [90, 110, 110, 90],
                "y": [90, 90, 140, 140]
            },
            {  # Bottom-right
                "x": [190, 210, 210, 190],
                "y": [90, 90, 140, 140]
            },
            {  # Top-right
                "x": [90, 110, 110, 90],
                "y": [160, 160, 210, 210]
            },
            {  # Top-left
                "x": [190, 210, 210, 190],
                "y": [160, 160, 210, 210]
            },
        ]

        self.plot_data = ArrayPlotData(
            robot_x=self.robot_bounding_box['x'],
            robot_y=self.robot_bounding_box['y'],
            wheel_bl_x=self.robot_wheels[0]['x'],
            wheel_bl_y=self.robot_wheels[0]['y'],
            wheel_br_x=self.robot_wheels[1]['x'],
            wheel_br_y=self.robot_wheels[1]['y'],
            wheel_tr_x=self.robot_wheels[2]['x'],
            wheel_tr_y=self.robot_wheels[2]['y'],
            wheel_tl_x=self.robot_wheels[3]['x'],
            wheel_tl_y=self.robot_wheels[3]['y'],
            velocity_l=[0, 100, 200],
            velocity_r=[0, 100, 100],
            velocity_arrow_l=[150, 200],
            velocity_arrow_r=[150, 200]
        )

        self.x_range = x_range
        self.y_range = y_range
        self.plot = self.plot_robot()
        self.plot_velocity()

    def plot_robot(self):
        plot = Plot(self.plot_data)
        plot.range2d.x_range = self.x_range
        plot.range2d.y_range = self.y_range
        plot.x_mapper = LinearMapper(range=self.x_range)
        plot.y_mapper = LinearMapper(range=self.y_range)
        plot.title = "robot"

        plot.plot(
            ('robot_x', 'robot_y'),
            type='polygon',
            marker='dot',
            marker_size=1.0,
            color=(0, 0, 0, 0.8)
        )

        wheel_outline_color = (0, 0, 0, 1.0)
        wheel_color = (0, 0, 0, 0.8)
        plot.plot(
            ('wheel_bl_x', 'wheel_bl_y'),
            type='polygon',
            marker='dot',
            marker_size=1.0,
            face_color=wheel_color,
            color=wheel_outline_color
        )

        plot.plot(
            ('wheel_br_x', 'wheel_br_y'),
            type='polygon',
            marker='dot',
            marker_size=1.0,
            face_color=wheel_color,
            color=wheel_outline_color
        )

        plot.plot(
            ('wheel_tr_x', 'wheel_tr_y'),
            type='polygon',
            marker='dot',
            marker_size=1.0,
            face_color=wheel_color,
            color=wheel_outline_color
        )

        plot.plot(
            ('wheel_tl_x', 'wheel_tl_y'),
            type='polygon',
            marker='dot',
            marker_size=1.0,
            face_color=wheel_color,
            color=wheel_outline_color
        )
        return plot

    def plot_velocity(self):
        origin_x = self.size[0] / 2
        origin_y = self.size[1] / 2
        self.plot_arrow((origin_x, origin_y), (200, 200))
        pass

    def plot_arrow(self,
                   from_point,
                   to_point,
                   color=(1.0, 0.0, 0.0, 0.9)):
        """
        Plot an arrow between two points
        :param from_point: The starting point of the arrow
        :param to_point: The ending point of the arrow
        :param color The color of the arrow
        :return:
        """

        # compute the length of the arrow and angle with the horizontal
        r = np.sqrt(pow((to_point[0] - from_point[0]), 2) + pow((to_point[1] - from_point[1]), 2))
        theta = np.arccos((to_point[0] - from_point[0]) / r)

        # length adjustment for arrow side points
        r_factor = 0.70

        # angle offset for arrow side points
        angle = 0.25

        # Compute where the side points should be drawn
        x1 = from_point[0] + r_factor * r * np.cos(theta - angle)
        y1 = from_point[1] + r_factor * r * np.sin(theta - angle)
        x2 = from_point[0] + r_factor * r * np.cos(theta + angle)
        y2 = from_point[1] + r_factor * r * np.sin(theta + angle)

        # Update middle line segment
        self.plot.data.set_data('arrow_x', [from_point[0], to_point[0]])
        self.plot.data.set_data('arrow_y', [from_point[1], to_point[1]])

        # Draw arrowhead
        self.plot.data.set_data('arrowhead_x', [to_point[0], x1, x2, to_point[0]])
        self.plot.data.set_data('arrowhead_y', [to_point[1], y1, y2, to_point[1]])

        self.plot.plot(
            ('arrow_x', 'arrow_x'),
            type='line',
            marker='dot',
            line_width=2.0,
            face_color=color,
            color=color,
        )

        self.plot.plot(
            ('arrowhead_x', 'arrowhead_y'),
            type='polygon',
            marker='dot',
            line_width=1.0,
            edge_color=color,
            face_color=color,
        )
