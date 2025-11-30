import sys
import os
import argparse

# Configuração de PATH para encontrar src
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, 'src')

if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from src.main import main
except ImportError as e:
    print(f"Erro de importação crítico: {e}")
    sys.exit(1)

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = base_dir

EXAMPLES_DIR = os.path.join(BASE_DIR, "examples")


def menu_principal():
    """Exibe o menu principal."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("===============================")
        print(" Simulador de Escalonamento SO ")
        print("===============================")
        print("1) FIFO")
        print("2) SRTF")
        print("3) Prioridade (Padrão)")
        print("4) Prioridade (Aging/PRIOPEnv)")
        print("0) Sair")
        print("===============================")
        opcao = input("Escolha o algoritmo: ")

        if opcao == "0":
            sys.exit(0)
        elif opcao in ["1", "2", "3", "4"]:
            algoritmos = {
                "1": "FIFO", 
                "2": "SRTF", 
                "3": "PRIORIDADE",
                "4": "PRIOPENV"
            }
            algoritmo = algoritmos[opcao]
            escolher_config(algoritmo)
        else:
            input("Opção inválida! Enter para tentar novamente.")


def escolher_config(algoritmo: str):
    """Escolhe o arquivo de configuração."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"=== {algoritmo}: Escolha o Arquivo ===")

    if not os.path.exists(EXAMPLES_DIR):
        print(f"Pasta 'examples' não encontrada.")
        input("Enter para voltar.")
        return

    # Filtro de arquivos
    arquivos = []
    prefixo = f"config_{algoritmo.lower()}"
    
    for f in os.listdir(EXAMPLES_DIR):
        if f.lower().startswith(prefixo):
            arquivos.append(f)
            
    if not arquivos:
        print(f"Nenhum arquivo encontrado com prefixo '{prefixo}'.")
        input("Enter para voltar.")
        return

    for i, arq in enumerate(arquivos, start=1):
        print(f"{i}) {arq}")
    print("0) Voltar")

    opcao = input("Opção: ")

    if opcao == "0":
        return

    try:
        idx = int(opcao) - 1
        if 0 <= idx < len(arquivos):
            arquivo_escolhido = os.path.join(EXAMPLES_DIR, arquivos[idx])
            escolher_modo(algoritmo, arquivo_escolhido)
        else:
            input("Opção inválida!")
    except ValueError:
        input("Entrada inválida!")


def escolher_modo(algoritmo: str, config_file: str):
    """NOVO: Escolhe entre modo completo ou passo-a-passo."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Arquivo: {os.path.basename(config_file)}")
    print("-" * 30)
    print("Escolha o modo de execução:")
    print("1) Completo (Executa tudo e mostra estatísticas)")
    print("2) Passo-a-Passo (Interativo: Next, Prev, Gantt)")
    print("0) Voltar")
    print("-" * 30)
    
    opcao = input("Opção: ")
    
    if opcao == "1":
        rodar_simulacao(algoritmo, config_file, 'completo')
    elif opcao == "2":
        rodar_simulacao(algoritmo, config_file, 'passo')
    elif opcao == "0":
        return
    else:
        input("Opção inválida!")


def rodar_simulacao(algoritmo: str, config_file: str, modo: str):
    """Roda a simulação com o modo escolhido."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Rodando {algoritmo} | Modo: {modo}")
    print("-" * 30)

    args = argparse.Namespace(
        config_file=config_file,
        modo=modo, 
        output=f"{os.path.splitext(os.path.basename(config_file))[0]}.svg"
    )

    try:
        main(args)
    except Exception as e:
        print(f"\nErro na execução: {e}")
        import traceback
        traceback.print_exc()

    input("\nPressione ENTER para voltar ao menu.")


if __name__ == "__main__":
    menu_principal()