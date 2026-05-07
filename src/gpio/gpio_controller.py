try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by using 'sudo' to run your script")

class GPIOController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

    def setup_output(self, pin):
        GPIO.setup(pin, GPIO.OUT)

    def turn_on(self, pin):
        GPIO.output(pin, True)

    def turn_off(self, pin):
        GPIO.output(pin, False)

    def cleanup(self):
        GPIO.cleanup()