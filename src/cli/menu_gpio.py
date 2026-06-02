from app.traffic_light_system import gpio_traffic_light_system

def menu_gpio():
    while True:
        print("\n------- GPIO -------")
        print("1 - Iniciar")
        print("0 - Sair")

        option = input("\nEscolha: ")

        if option == "1":
            gpio_traffic_light_system()

        elif option == "0":
            print('Encerrando...')
            break