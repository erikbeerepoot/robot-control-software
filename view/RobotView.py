import numpy as np
from chaco.api import DataRange1D, Plot, LinearMapper, ArrayPlotData
from enable.api import ComponentEditor, Line
from traits.api import HasTraits, Instance, CFloat
from traitsui.api import Item, Group, View

from view.VelocityTool import VelocityTool


class RobotView(HasTraits):
    size = (300, 300)

    view = View(
        Group(
            Item('plot', editor=ComponentEditor(size=size), show_label=False),
            Item(name='velocity_x'),
            Item(name='velocity_y'),
            orientation="vertical"
        ),
        resizable=True,
        width=size[0],
        height=size[1]
    )

    wheel_line = Instance(Line, args=())

    velocity_x = CFloat(
        0.0,
        desc="Velocity in the x direction",
        label="Vx"
    )
    velocity_y = CFloat(
        0.0,
        desc="Velocity in the y direction",
        label="Vy"
    )

    def __init__(self,
                 x_range=DataRange1D(low=0, high=size[0]),
                 y_range=DataRange1D(low=0, high=size[1]), *args, **kwargs):
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
            arrow_x=[0, 100, 200],
            arrow_y=[0, 100, 100],
            arrowhead_x=[150, 200],
            arrowhead_y=[150, 200]
        )

        self.x_range = x_range
        self.y_range = y_range

        velocity_tool = VelocityTool(
            (150, 150),
            (300, 300),
            self.update_velocity,
            self.hover_velocity
        )

        # Show starting plot
        self.plot = self.plot_robot()
        self.plot.tools.append(velocity_tool)
        self.plot_velocity()

    def update_velocity(self, velocity):
        target_x = 150 + velocity[0] * 150
        target_y = 150 + velocity[1] * 150
        self.velocity_x = (target_x - 150) / 150
        self.velocity_y = (target_y - 150) / 150
        self.plot_arrow((150, 150), (target_x, target_y), (1.0, 0, 0, 0.9), 'vel')

    def hover_velocity(self, hover_velocity):
        target_x = 150 + hover_velocity[0] * 150
        target_y = 150 + hover_velocity[1] * 150
        self.plot_arrow((150, 150), (target_x, target_y), (0.0, 0.0, 0.0, 0.25), 'hov_vel')
        pass

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
        self.plot_arrow((origin_x, origin_y), (origin_x, origin_y))
        pass

    def plot_arrow(self,
                   from_point,
                   to_point,
                   color=(1.0, 1.0, 0.0, 0.1),
                   label="arrow"):
        """
        Plot an arrow between two points
        :param from_point: The starting point of the arrow
        :param to_point: The ending point of the arrow
        :param color The color of the arrow
        :return:
        """
        if to_point == from_point:
            return

        # compute the length of the arrow and angle with the horizontal
        r = np.sqrt(pow((to_point[0] - from_point[0]), 2) + pow((to_point[1] - from_point[1]), 2))
        theta = np.arccos((to_point[0] - from_point[0]) / r)

        # length adjustment for arrow side points
        r_factor = 0.70 + 0.15 * (r / 212.5)

        # angle offset for arrow side points
        angle = 0.25 - 0.125 * (r / 212.5)

        # Compute where the side points should be drawn
        pos_neg = 1 if (from_point[1] < to_point[1]) else -1
        x1 = from_point[0] + r_factor * r * np.cos(theta - angle)
        x2 = from_point[0] + r_factor * r * np.cos(theta + angle)
        y1 = from_point[1] + pos_neg * r_factor * r * np.sin(theta - angle)
        y2 = from_point[1] + pos_neg * r_factor * r * np.sin(theta + angle)

        update = True if f'{label}_x' in self.plot.data.arrays.keys() else False

        # Update middle line segment
        self.plot.data.set_data(f'{label}_x', [from_point[0], to_point[0]])
        self.plot.data.set_data(f'{label}_y', [from_point[1], to_point[1]])

        # Draw arrowhead
        self.plot.data.set_data(f'{label}_arrowhead_x', [to_point[0], x1, x2, to_point[0]])
        self.plot.data.set_data(f'{label}_arrowhead_y', [to_point[1], y1, y2, to_point[1]])

        if not update:
            self.plot.plot(
                (f'{label}_x', f'{label}_y'),
                type='line',
                marker='dot',
                line_width=2.0,
                face_color=color,
                color=color,
            )

            self.plot.plot(
                (f'{label}_arrowhead_x', f'{label}_arrowhead_y'),
                type='polygon',
                marker='dot',
                line_width=1.0,
                edge_color=color,
                face_color=color,
            )
