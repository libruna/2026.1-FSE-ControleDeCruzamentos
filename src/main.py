from cli.menu_gpio import gpio_menu
from cli.menu_uart import menu_uart

def main():
    while True:
        print("\n------- MENU -------")
        print("1 - Controle de Cruzamentos")
        print("2 - Comunicação UART")
        print("0 - Sair")

        option = input("\nEscolha: ")

        if option == "1":
            gpio_menu()

        elif option == "2":
            menu_uart()

        elif option == "0":
            print('Encerrando...')
            break

        else:
            print("Opção inválida")

if __name__ == "__main__":
    main()