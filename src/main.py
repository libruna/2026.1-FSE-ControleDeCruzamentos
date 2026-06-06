import sys
import config.pins as pins
from lpr.traffic_light_system import traffic_light_system

def main():
    # Verifica o ID do cruzamento passado como argumento
    if len(sys.argv) < 2:
        print('[ERRO] Informe o ID do cruzamento ao iniciar. Exemplo: python main.py 1')
        sys.exit(1)

    cruzamento_id = sys.argv[1]

    if cruzamento_id == '1':
        print('[INFO] Inicializando Servidor Distribuído do Cruzamento 1...')
        traffic_light_system('1', pins.BIT_1_0, pins.BIT_1_1, pins.BIT_1_2, pins.IN_P_1, pins.IN_C_1)
    
    elif cruzamento_id == '2':
        print('[INFO] Inicializando Servidor Distribuído do Cruzamento 2...')
        traffic_light_system('2', pins.BIT_2_0, pins.BIT_2_1, pins.BIT_2_2, pins.IN_P_2, pins.IN_C_2)
    
    else:
        print(f"[ERRO] Cruzamento '{cruzamento_id}' inválido. Escolha 1 ou 2.")
        sys.exit(1)

if __name__ == '__main__':
    main()