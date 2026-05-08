from config import pins
from gpio.gpio_controller import GPIOController
from model.traffic_light import TrafficLight
from time import sleep

gpio = GPIOController()

tres_leds = TrafficLight(
    'red',
    5,
    10,
    2,
    2
)

cruzamento = TrafficLight(
    'red',
    5,
    10,
    2,
    2
)

principal = TrafficLight(
    'green',
    10,
    20,
    2,
    2
)

gpio.setup_input(CRUZAMENTO_1)
gpio.setup_input(PRINCIPAL_1)
gpio.setup_input(CRUZAMENTO_2)
gpio.setup_input(PRINCIPAL_2)

gpio.setup_output(RED_LED)
gpio.setup_output(GREEN_LED)
gpio.setup_output(YELLOW_LED)

gpio.setup_output(BIT_0)
gpio.setup_output(BIT_1)
gpio.setup_output(BIT_2)


def output_m1(estado_semaforo):
    gpio.output(RED_LED, estado_semaforo == 'red')
    gpio.output(YELLOW_LED, estado_semaforo == 'yellow')
    gpio.output(GREEN_LED, estado_semaforo == 'green')

def output_m2(estado_principal, estado_cruzamento):

    if estado_principal == 'green' and estado_cruzamento == 'red': # Estado 1
        gpio.output(BIT_0, True)
        gpio.output(BIT_1, False)
        gpio.output(BIT_2, False)
    
    elif estado_principal == 'yellow' and estado_cruzamento == 'red': # Estado 2
        gpio.output(BIT_0, False)
        gpio.output(BIT_1, True)
        gpio.output(BIT_2, False)

    elif estado_principal == estado_cruzamento == 'red': # Estado 4
        gpio.output(BIT_0, False)
        gpio.output(BIT_1, False)
        gpio.output(BIT_2, True)
    
    elif estado_principal == 'red' and estado_cruzamento == 'green': # Estado 5
        gpio.output(BIT_0, True)
        gpio.output(BIT_1, False)
        gpio.output(BIT_2, True)
    
    elif estado_principal == 'red' and estado_cruzamento == 'yellow': # Estado 6
        gpio.output(BIT_0, False)
        gpio.output(BIT_1, True)
        gpio.output(BIT_2, True)
    
    else:
        print('ESTADO INVALIDO')
    
def queue_pedestrian_m1(canal):
    tres_leds.queue_pedestrian()

def queue_pedestrian_cruzamento(canal):
    cruzamento.queue_pedestrian()

def queue_pedestrian_principal(canal):
    principal.queue_pedestrian()

GPIO.add_event_detect(
    CRUZAMENTO_1,
    GPIO.FALLING,
    callback=queue_pedestrian_m1,
    bouncetime=200
)

GPIO.add_event_detect(
    CRUZAMENTO_2,
    GPIO.FALLING,
    callback=queue_pedestrian_cruzamento,
    bouncetime=200
)

GPIO.add_event_detect(
    PRINCIPAL_2,
    GPIO.FALLING,
    callback=queue_pedestrian_principal,
    bouncetime=200
)

time = 0

try:
    while True:
        tres_leds.execute(time, queue_pedestrian=False)
        output_m1(tres_leds.state)

        print(tres_leds.state.capitalize())

        cruzamento.execute(time, principal.state == 'green')
        principal.execute(time, cruzamento.state == 'green')

        output_m2(principal.state, cruzamento.state)

        sleep(0.01)
        time += 0.01
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    gpio.cleanup()