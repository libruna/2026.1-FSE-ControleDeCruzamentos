import time

class SpeedSensor:
    
    DISTANCE_METERS = 2

    def __init__(self, sensor_id):
        self.sensor_id = sensor_id
        self.start_time = None
        self.vehicle_count = 0
        self.last_speed = 0

    def trigger_a(self, channel = None):
        self.start_time = time.time()

    def trigger_b(self, channel = None):
        if self.start_time is None:
            return

        delta_t = time.time() - self.start_time

        self.last_speed = (self.DISTANCE_METERS / delta_t) * 3.6
        self.vehicle_count += 1
        self.start_time = None