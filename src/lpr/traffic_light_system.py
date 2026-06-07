from config import pins
from gpio.gpio_controller import GPIOController
from model.traffic_light import TrafficLight
from time import sleep
from model.speed_sensor import SpeedSensor
from network.tcp_client import connect_to_central

def get_state(estado_principal, estado_cruzamento, noite, time):
    output = [False, False, False] # Estado 0

    if noite:
        if int(time) % 2 == 0:
            pass 
        else:
            output[2] = True
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
        print('[ERRO] ESTADO INVALIDO')
    
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

    client_id = f'cruzamento_{name}'
    print(f"\nInicializando {client_id.upper()}...")

    def send_infraction_alert(sensor_id, velocity):
        message = f"INFRACTION:{name}:{sensor_id}:{velocity:.2f}"
        try:
            client.send(message.encode('utf-8'))
            print(f"[INFO] Infração detectada no {sensor_id}: {velocity:.2f} km/h. Enviando ao servidor...")
        except Exception as e:
            print(f"[ERRO] Falha ao enviar infração: {e}")

    # Sensores cruzamento 1
    if name == "1":
        gpio.setup_input(16)
        gpio.setup_input(20)
        gpio.setup_input(21)
        gpio.setup_input(27)

        sensor_1 = SpeedSensor('sensor_1', on_infraction=send_infraction_alert)
        sensor_2 = SpeedSensor('sensor_2', on_infraction=send_infraction_alert)

        gpio.add_event_detect(16, callback=sensor_1.trigger_a, bouncetime=1)
        gpio.add_event_detect(20, callback=sensor_1.trigger_b, bouncetime=1)
        gpio.add_event_detect(21, callback=sensor_2.trigger_a, bouncetime=1)
        gpio.add_event_detect(27, callback=sensor_2.trigger_b, bouncetime=1)

    # Sensores cruzamento 2
    if name == "2":
        gpio.setup_input(11)
        gpio.setup_input(0) 
        gpio.setup_input(5)
        gpio.setup_input(6) 

        sensor_3 = SpeedSensor('sensor_3', on_infraction=send_infraction_alert)
        sensor_4 = SpeedSensor('sensor_4', on_infraction=send_infraction_alert)

        gpio.add_event_detect(11, callback=sensor_3.trigger_a, bouncetime=1)
        gpio.add_event_detect(0, callback=sensor_3.trigger_b, bouncetime=1)
        gpio.add_event_detect(5, callback=sensor_4.trigger_a, bouncetime=1)
        gpio.add_event_detect(6, callback=sensor_4.trigger_b, bouncetime=1)

    client = connect_to_central()
    
    time = 0
    night_mode = False

    try:
        while True:
            cruzamento.execute(time, principal.state != 'red')
            principal.execute(time, cruzamento.state != 'red')

            try:
                data = client.recv(1024).decode('utf-8')
            
                if data == 'NIGHT_MODE_ON':
                    night_mode = True
                    print("\n[INFO] Modo Noturno ativado!")
                elif data == 'NIGHT_MODE_OFF': # TODO: verificar regra para desativar modo noturno
                    night_mode = False
                    print("\n[INFO] Modo Noturno desativado!")
            except BlockingIOError:
                pass
            except Exception as e:
                pass

            output = get_state(principal.state, cruzamento.state, night_mode, time)

            # TODO: emergencia tcp/ip
            # use metodo principal.force_state(time, state)

            gpio.output(bit0, output[0])
            gpio.output(bit1, output[1])
            gpio.output(bit2, output[2])

            if round(time, 2) % 2.0 == 0 and time > 0:
                if name == "1":
                    sensors = {
                        'sensor_1': sensor_1.vehicle_count,
                        'sensor_2': sensor_2.vehicle_count
                    }
                else:
                    sensors = {
                        'sensor_3': sensor_3.vehicle_count,
                        'sensor_4': sensor_4.vehicle_count
                    }

                # Mensagens no formato: 'cruzamento_A:sensor_B:quantidade'
                for sensor_id, count in sensors.items():
                    message = f'{client_id}:{sensor_id}:{count}'
                    client.send(message.encode('utf-8'))

            sleep(0.01)
            time += 0.01
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        gpio.cleanup()