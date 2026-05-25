from app.traffic_light_system import traffic_light_system

def menu_gpio():
    while True:
        print("\n------- GPIO -------")
        print("1 - Iniciar")
        print("0 - Voltar")

        option = input("\nEscolha: ")

        if option == "1":
            traffic_light_system()

        elif option == "0":
            break