import math


class ScanParams:
    def __init__(self,
                 type,
                 start_step,
                 end_step,
                 cluster_count,
                 scan_interval=1,
                 scan_index=1,
                 angular_resolution=(360 / 1024)):
        self.type = type
        self.start_step = start_step
        self.end_step = end_step
        self.cluster_count = cluster_count
        self.scan_interval = scan_interval
        self.scan_index = scan_index
        self.angular_resolution = angular_resolution


class ScanStatus:
    def __init__(self, status_code):
        message = "ok"


class Scan:
    start_step_angle = 315

    def __init__(self, params, status, timestamp, payload):
        self.params = params
        self.status = status
        self.timestamp = timestamp
        self.payload = payload

    # 0 step is -45 -> 315
    #  768 (last) step is 225
    def get_scan_angle(self, step):
        return math.radians(
            (
                    self.start_step_angle
                    + self.params.start_step * self.params.angular_resolution
                    + step * self.params.angular_resolution
            ) % 360
        )
