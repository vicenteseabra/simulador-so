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
    """Exibe o menu principal organizado por categorias."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=======================================")
        print("    Simulador SO - Menu de Testes      ")
        print("=======================================")
        print("1) FIFO")
        print("2) SRTF")
        print("3) Prioridade (Sem Aging)")
        print("4) Testes de Aging (PRIOPEnv)")
        print("5) Testes de Mutex (Sincronização)")
        print("6) Testes de I/O (Entrada/Saída)")
        print("7) Cenários Complexos (Integrados)")
        print("8) Casos de Teste (Avaliação)")
        print("\n0) Sair")
        print("=======================================")
        
        opcao = input("Escolha uma categoria: ")

        categorias = {
            "1": ("FIFO", "config_fifo"),
            "2": ("SRTF", "config_srtf"),
            "3": ("Prioridade", "config_prioridade"),
            "4": ("Aging / PRIOPEnv", "config_aging"),
            "5": ("Mutex", "config_mutex"),
            "6": ("I/O", "config_io"),
            "7": ("Complexo", "config_complexo"),
            "8": ("Casos de Teste", "caso-teste")
        }

        if opcao == "0":
            sys.exit(0)
        elif opcao in categorias:
            nome, prefixo = categorias[opcao]
            escolher_config(nome, prefixo)
        else:
            input("Opção inválida! Enter para tentar novamente.")


def escolher_config(nome_categoria, prefixo_arquivo):
    """Lista arquivos que começam com o prefixo escolhido."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"=== Categoria: {nome_categoria} ===")
    print(f"(Buscando arquivos iniciados em '{prefixo_arquivo}...')")
    print("-" * 40)

    if not os.path.exists(EXAMPLES_DIR):
        print(f"Pasta 'examples' não encontrada.")
        input("Enter para voltar.")
        return

    # Filtra arquivos pelo prefixo
    arquivos = [f for f in os.listdir(EXAMPLES_DIR) 
                if f.lower().startswith(prefixo_arquivo.lower()) and f.endswith('.txt')]
    
    arquivos.sort() # Ordena alfabeticamente

    if not arquivos:
        print(f"Nenhum arquivo encontrado para esta categoria.")
        print(f"Dica: Crie arquivos como '{prefixo_arquivo}_1.txt' na pasta examples.")
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
            escolher_modo(arquivo_escolhido)
        else:
            input("Opção inválida!")
    except ValueError:
        input("Entrada inválida!")


def escolher_modo(config_file):
    """Escolhe entre modo completo ou passo-a-passo."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Arquivo: {os.path.basename(config_file)}")
    print("-" * 30)
    print("1) Modo Completo (Estatísticas finais)")
    print("2) Modo Passo-a-Passo (Interativo / Debug)")
    print("0) Voltar")
    print("-" * 30)
    
    opcao = input("Opção: ")
    
    if opcao == "1":
        rodar_simulacao(config_file, 'completo')
    elif opcao == "2":
        rodar_simulacao(config_file, 'passo')
    elif opcao == "0":
        return
    else:
        input("Opção inválida!")


def rodar_simulacao(config_file, modo):
    """Roda a simulação chamando o main."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    nome_svg = f"{os.path.splitext(os.path.basename(config_file))[0]}.svg"
    
    args = argparse.Namespace(
        config_file=config_file,
        modo=modo, 
        output=nome_svg
    )

    try:
        main(args)
    except SystemExit:
        pass
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()

    input("\nPressione ENTER para voltar ao menu.")


if __name__ == "__main__":
    menu_principal()