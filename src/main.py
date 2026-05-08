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
    10
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

gpio.setup_input(pins.CRUZAMENTO_1)
gpio.setup_input(pins.PRINCIPAL_1)
gpio.setup_input(pins.CRUZAMENTO_2)
gpio.setup_input(pins.PRINCIPAL_2)

gpio.setup_output(pins.RED_LED)
gpio.setup_output(pins.GREEN_LED)
gpio.setup_output(pins.YELLOW_LED)

gpio.setup_output(pins.BIT_0)
gpio.setup_output(pins.BIT_1)
gpio.setup_output(pins.BIT_2)


def output_m1(estado_semaforo):
    gpio.output(pins.RED_LED, estado_semaforo == 'red')
    gpio.output(pins.YELLOW_LED, estado_semaforo == 'yellow')
    gpio.output(pins.GREEN_LED, estado_semaforo == 'green')

def output_m2(estado_principal, estado_cruzamento):

    if estado_principal == 'green' and estado_cruzamento == 'red': # Estado 1
        gpio.output(pins.BIT_0, True)
        gpio.output(pins.BIT_1, False)
        gpio.output(pins.BIT_2, False)
    
    elif estado_principal == 'yellow' and estado_cruzamento == 'red': # Estado 2
        gpio.output(pins.BIT_0, False)
        gpio.output(pins.BIT_1, True)
        gpio.output(pins.BIT_2, False)

    elif estado_principal == estado_cruzamento == 'red': # Estado 4
        gpio.output(pins.BIT_0, False)
        gpio.output(pins.BIT_1, False)
        gpio.output(pins.BIT_2, True)
    
    elif estado_principal == 'red' and estado_cruzamento == 'green': # Estado 5
        gpio.output(pins.BIT_0, True)
        gpio.output(pins.BIT_1, False)
        gpio.output(pins.BIT_2, True)
    
    elif estado_principal == 'red' and estado_cruzamento == 'yellow': # Estado 6
        gpio.output(pins.BIT_0, False)
        gpio.output(pins.BIT_1, True)
        gpio.output(pins.BIT_2, True)
    
    else:
        print('ESTADO INVALIDO')
    
def queue_pedestrian_m1(canal):
    tres_leds.queue_pedestrian()

def queue_pedestrian_cruzamento(canal):
    cruzamento.queue_pedestrian()

def queue_pedestrian_principal(canal):
    principal.queue_pedestrian()

gpio.add_event_detect(
    pins.CRUZAMENTO_1,
    callback=queue_pedestrian_m1
)

gpio.add_event_detect(
    pins.CRUZAMENTO_2,
    callback=queue_pedestrian_cruzamento
)

gpio.add_event_detect(
    pins.PRINCIPAL_2,
    callback=queue_pedestrian_principal
)

time = 0

try:
    while True:
        tres_leds.execute(time, False)
        output_m1(tres_leds.state)

        print(tres_leds.state.capitalize())

        cruzamento.execute(time, principal.state != 'red')
        principal.execute(time, cruzamento.state != 'red')

        output_m2(principal.state, cruzamento.state)

        sleep(0.01)
        time += 0.01
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    gpio.cleanup()
