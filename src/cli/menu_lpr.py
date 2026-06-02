from lpr.traffic_light_system import traffic_light_system
import config.pins as pins

def menu_lpr():
    while True:
        print("\n------- LPR -------")
        print("1 - Servidor")
        print("2 - Cruzamento")
        print("0 - Sair")

        option = input("\nEscolha: ")

        if option == "1":
            pass
        
        elif option == "2":
            menu_cruzamento()

        elif option == "0":
            print('Encerrando...')
            break

        else:
            print("Opção inválida")
def menu_cruzamento():
    while True:
        print("\n--- Cruzamento ----")
        print("1 - Cruzamento 1")
        print("2 - Cruzamento 2")

        option = input("\nEscolha: ")

        if option == "1":
            traffic_light_system(option, pins.BIT_1_0, pins.BIT_1_1, pins.BIT_1_2, pins.IN_P_1, pins.IN_C_1)
            pass
        
        elif option == "2":
            traffic_light_system(option, pins.BIT_2_0, pins.BIT_2_1, pins.BIT_2_2, pins.IN_P_2, pins.IN_C_2)
            pass

        elif option == "0":
            print('Encerrando...')
            break

        else:
            print("Opção inválida")
