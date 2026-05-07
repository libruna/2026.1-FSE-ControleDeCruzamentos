from config import pins
from gpio.gpio_controller import GPIOController
from model.traffic_light import TrafficLight

gpio = GPIOController()

traffic_light = TrafficLight(
    gpio,
    pins.GREEN_LED,
    pins.YELLOW_LED,
    pins.RED_LED
)

try:
    traffic_light.execute()
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    gpio.cleanup()