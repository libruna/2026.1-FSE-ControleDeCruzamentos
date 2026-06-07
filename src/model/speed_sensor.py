import time

class SpeedSensor:
    
    DISTANCE_METERS = 2.5

    def __init__(self, sensor_id, on_infraction=None):
        self.sensor_id = sensor_id
        self.start_time = None
        self.vehicle_count = 0
        self.last_speed = 0
        self.on_infraction = on_infraction

    def trigger_a(self, channel = None):
        self.start_time = time.perf_counter()

    def trigger_b(self, channel = None):
        if self.start_time is not None:

            delta_t = time.perf_counter() - self.start_time
            self.start_time = None 
            
            if 0.010 <= delta_t <= 0.400:
                self.vehicle_count += 1
                self.last_speed = (self.DISTANCE_METERS / delta_t) * 3.6
                
                if self.last_speed > 60.0:
                    if self.on_infraction:
                        self.on_infraction(self.sensor_id, self.last_speed)