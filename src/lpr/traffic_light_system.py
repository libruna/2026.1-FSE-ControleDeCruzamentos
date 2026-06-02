from config import pins
from gpio.gpio_controller import GPIOController
from model.traffic_light import TrafficLight
from time import sleep

def get_state(estado_principal, estado_cruzamento, noite):
    output = [False, False, False] # Estado 0

    if noite:
        pass
    elif estado_principal == 'green' and estado_cruzamento == 'red': # Estado 1
        output[0] = True
    elif estado_principal == 'yellow' and estado_cruzamento == 'red': # Estado 2
        output[1] = True
    elif estado_principal == estado_cruzamento == 'red': # Estado 4
        output[2] = True
    elif estado_principal == 'red' and estado_cruzamento == 'green': # Estado 5
        output[0] = True
        output[2] = True
    elif estado_principal == 'red' and estado_cruzamento == 'yellow': # Estado 6
        output[1] = True
        output[2] = True
    else:
        print('ESTADO INVALIDO')
    
    return output

def traffic_light_system(name, bit0, bit1, bit2, botao_principal, botao_cruzamento):
    gpio = GPIOController()

    cruzamento = TrafficLight(
        'Cruzamento ' + name,
        'red',
        5,
        10,
        3,
        2
    )

    principal = TrafficLight(
        'Principal ' + name,
        'red',
        15,
        30,
        3,
        2
    )

    gpio.setup_input(botao_principal)
    gpio.setup_input(botao_cruzamento)

    gpio.setup_output(bit0)
    gpio.setup_output(bit1)
    gpio.setup_output(bit2)

    gpio.add_event_detect(
        botao_principal,
        principal.queue_pedestrian,
        500
    )

    gpio.add_event_detect(
        botao_cruzamento,
        cruzamento.queue_pedestrian,
        500
    )

    time = 0

    try:
        while True:
            cruzamento.execute(time, principal.state != 'red')
            principal.execute(time, cruzamento.state != 'red')

            # TODO: noite/dia tcp/ip
            noite = False

            output = get_state(principal.state, cruzamento.state, noite)

            # TODO: emergencia tcp/ip
            # use metodo principal.force_state(time, state)

            gpio.output(bit0, output[0])
            gpio.output(bit1, output[1])
            gpio.output(bit2, output[2])

            sleep(0.01)
            time += 0.01
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        gpio.cleanup()