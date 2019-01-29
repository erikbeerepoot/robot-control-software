from enable.api import BaseTool
from enum import Enum

class VelocityTool(BaseTool):
    """
    Allows control inputs for robot to be set by
    clicking on a plot
    """
    event_state = "normal"

    def __init__(self,
                 f_r_center,
                 size,
                 velocity_callback,
                 hover_velocity_callback):
        """
        Initializer
        :param f_r_center: The center of the robot coordinate frame
        (used to compute velociy commands)
        :param size: The size of the plot (used as range)
        """
        super().__init__()
        self.f_r_center = f_r_center
        self.size = size
        self.velocity_callback = velocity_callback
        self.hover_velocity_callback = hover_velocity_callback

    def normal_mouse_move(self, event):
        hover_velocity = self.compute_velocity((event.x, event.y))
        self.hover_velocity_callback(hover_velocity)
        event.handled = True

    def normal_left_down(self, event):
        self.event_state = "mousedown"
        event.handled = True

    def mousedown_left_up(self, event):
        self.event_state = "normal" \
                           ""
        velocity = self.compute_velocity((event.x, event.y))
        self.velocity_callback(velocity)
        event.handled = True

    def compute_velocity(self, mouse_location):
        # The velocity input is just the difference between
        # the center and the current click location divided by
        # the maximum (normalized, i.e. 9 -1 =< v =< 1
        delta_x = mouse_location[0] - self.f_r_center[0]
        delta_y = mouse_location[1] - self.f_r_center[1]
        v_x = delta_x / (self.size[0] / 2)
        v_y = delta_y / (self.size[1] / 2)
        return v_x, v_y
