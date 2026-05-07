import time

class TrafficLight:

    def __init__(self, gpio, green, yellow, red):
        self.gpio = gpio

        self.green_pin = green
        self.yellow_pin = yellow
        self.red_pin = red

        self.gpio.setup_output(green)
        self.gpio.setup_output(yellow)
        self.gpio.setup_output(red)

    def green_state(self):
        self.gpio.turn_on(self.green_pin)
        self.gpio.turn_off(self.yellow_pin)
        self.gpio.turn_off(self.red_pin)

        print("GREEN")
        time.sleep(10)

    def yellow_state(self):
        self.gpio.turn_off(self.green_pin)
        self.gpio.turn_on(self.yellow_pin)
        self.gpio.turn_off(self.red_pin)

        print("YELLOW")
        time.sleep(2)
    
    def red_state(self):
        self.gpio.turn_off(self.green_pin)
        self.gpio.turn_off(self.yellow_pin)
        self.gpio.turn_on(self.red_pin)

        print("RED")
        time.sleep(10)
        
    def execute(self):
        while True:
            self.green_state()
            self.yellow_state()
            self.red_state()