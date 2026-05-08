try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by using 'sudo' to run your script")

class GPIOController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

    def setup_output(self, pin):
        GPIO.setup(pin, GPIO.OUT)
    
    def setup_input(self, pin):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def add_event_detect(self, pin, callback):
        print(f'{pin=} {callback=}')
        GPIO.add_event_detect(pin, GPIO.RISING, callback=callback, bouncetime=200)

    def output(self, pin, onoff):
        GPIO.output(pin, onoff)

    def turn_on(self, pin):
        GPIO.output(pin, True)

    def turn_off(self, pin):
        GPIO.output(pin, False)

    def cleanup(self):
        GPIO.cleanup()
