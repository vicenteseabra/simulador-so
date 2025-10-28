import sys
import os
import argparse
from src.main import main

# Corrige o caminho para a pasta 'examples' mesmo quando rodar como .exe
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS  # diretório temporário do PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXAMPLES_DIR = os.path.join(BASE_DIR, "examples")



def menu_principal():
    """
    Exibe o menu principal para escolha do algoritmo de escalonamento.
    """
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("===============================")
        print(" Simulador de Escalonamento SO ")
        print("===============================")
        print("1) FIFO")
        print("2) SRTF")
        print("3) Prioridade")
        print("0) Sair")
        print("===============================")
        opcao = input("Escolha o algoritmo: ")

        if opcao == "0":
            print("Encerrando simulador.")
            sys.exit(0)
        elif opcao in ["1", "2", "3"]:
            algoritmos = {"1": "FIFO", "2": "SRTF", "3": "PRIORIDADE"}
            algoritmo = algoritmos[opcao]
            escolher_config(algoritmo)
        else:
            input("Opção inválida! Pressione ENTER para tentar novamente.")


def escolher_config(algoritmo: str):
    """
    Permite ao usuário escolher o arquivo de configuração para o algoritmo selecionado.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"=== {algoritmo} ===")

    # Filtra os arquivos que começam com o nome do algoritmo
    arquivos = [f for f in os.listdir(EXAMPLES_DIR)
                if f.lower().startswith(f"config_{algoritmo.lower()}")]

    if not arquivos:
        print(f"Nenhum arquivo de configuração encontrado para {algoritmo}.")
        input("Pressione ENTER para voltar.")
        return

    for i, arq in enumerate(arquivos, start=1):
        print(f"{i}) {arq}")
    print("0) Voltar")

    opcao = input("Escolha o arquivo: ")

    if opcao == "0":
        return

    try:
        idx = int(opcao) - 1
        if 0 <= idx < len(arquivos):
            arquivo_escolhido = os.path.join(EXAMPLES_DIR, arquivos[idx])
            rodar_simulacao(algoritmo, arquivo_escolhido)
        else:
            input("Opção inválida! Pressione ENTER.")
    except ValueError:
        input("Entrada inválida! Pressione ENTER.")


def rodar_simulacao(algoritmo: str, config_file: str):
    """
    Executa a simulação chamando o main() do módulo principal.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Rodando {algoritmo} com {config_file}...\n")

    # Cria um objeto de argumentos simulando o argparse
    args = argparse.Namespace(
        config_file=config_file,
        modo='completo',
        output=f"{os.path.splitext(os.path.basename(config_file))[0]}.svg"
    )

    # Chama a função principal do simulador
    main(args)

    input("\nPressione ENTER para voltar ao menu.")


if __name__ == "__main__":
    # Garante que a pasta src esteja no sys.path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    menu_principal()
