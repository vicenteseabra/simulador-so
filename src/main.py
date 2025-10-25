# src/main.py

import argparse
import sys
import os
from typing import List, Dict, Any, Tuple

# --- Bloco de Importação Robusto ---
# Adiciona o diretório raiz do projeto (o pai de 'src') ao sys.path
# Isso permite que o script seja executado de duas formas:
# 1. Como um módulo (python -m src.main ...)
# 2. Como um script direto (python src/main.py ...)
try:
    # Tenta importar como se 'src' fosse um pacote (execução como módulo)
    from src.config_parser import ConfigParser
    from src.scheduler import SchedulerFactory
    from src.simulator import Simulator
    from src.gantt import GanttChart
    from src.task import Task
except ImportError:
    # Se falhar, é provável que esteja sendo executado como script direto.
    # Adicionamos o diretório pai ao path.
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    try:
        from src.config_parser import ConfigParser
        from src.scheduler import SchedulerFactory
        from src.simulator import Simulator
        from src.gantt import GanttChart
        from src.task import Task
    except ImportError as e:
        print(f"Erro crítico de importação: {e}", file=sys.stderr)
        print("Certifique-se de que todos os arquivos .py (task.py, scheduler.py, etc.) "
              "estejam no mesmo diretório 'src'.", file=sys.stderr)
        sys.exit(1)
# --- Fim do Bloco de Importação ---


def configurar_argumentos() -> argparse.Namespace:
    """
    Configura e faz o parse dos argumentos da linha de comando.
    """
    parser = argparse.ArgumentParser(
        description="Simulador de Escalonador de Processos de SO.",
        epilog="Exemplo de uso: python src/main.py examples/config_fifo.txt --modo completo"
    )

    parser.add_argument(
        "config_file",
        help="Arquivo de configuração (obrigatório) contendo o algoritmo e as tarefas."
    )

    parser.add_argument(
        "--modo",
        help="Modo de execução da simulação.",
        choices=['completo', 'passo'],
        default='completo'
    )

    parser.add_argument(
        "--output",
        help="Nome do arquivo SVG de saída para o gráfico de Gantt (opcional). "
             "O arquivo será salvo no diretório 'output/'.",
        default=None
    )

    return parser.parse_args()


def popular_gantt_chart(historico: List[Tuple[int, str]], tasks: List[Task]) -> GanttChart:
    """
    Processa o histórico de execução e o insere no objeto GanttChart.
    (Lógica corrigida baseada no script de demonstração)
    """
    gantt = GanttChart()
    
    # Cria mapa de task_id -> cor
    cores = {task.id: task.cor for task in tasks}
    
    # Agrupa execuções consecutivas
    if not historico:
        return gantt
    
    inicio_intervalo = historico[0][0]
    task_atual = historico[0][1]
    
    for i in range(1, len(historico)):
        tempo, task_id = historico[i]
        
        # Se mudou de tarefa
        if task_id != task_atual:
            # Fecha intervalo anterior
            if task_atual is not None:  # Ignora períodos IDLE (ociosidade)
                cor = cores.get(task_atual, '#CCCCCC') # Usa cinza se não achar
                gantt.adicionar_intervalo(task_atual, inicio_intervalo, tempo, cor)
            
            # Inicia novo intervalo
            inicio_intervalo = tempo
            task_atual = task_id
    
    # Fecha último intervalo
    if task_atual is not None:
        # O tempo final é o tick do último evento + 1
        tempo_final = historico[-1][0] + 1
        cor = cores.get(task_atual, '#CCCCCC')
        gantt.adicionar_intervalo(task_atual, inicio_intervalo, tempo_final, cor)
    
    return gantt


def exibir_resultados(simulator: Simulator, resultados: Dict[str, Any]):
    """
    Exibe as métricas finais da simulação no terminal.
    """
    print("\n=== Resultados da Simulação ===")
    print(f"Modo de execução: {args.modo}")
    print(f"Algoritmo: {simulator.scheduler.__class__.__name__}")
    
    tempo_total = resultados.get('tempo_total_ticks', 0)
    print(f"Tempo total de execução (ticks): {tempo_total}")

    if 'tempo_execucao_real_ms' in resultados:
        print(f"Tempo de processamento (real): {resultados['tempo_execucao_real_ms']:.2f} ms")

    print("\n--- Métricas das Tarefas ---")
    if not simulator.tasks:
        print("Nenhuma tarefa foi processada.")
        return

    # Cabeçalho da tabela
    print(f"{'ID':<5} | {'Turnaround':<10} | {'Espera':<10} | {'Resposta':<10}")
    print("-" * 49)

    total_turnaround = 0
    total_espera = 0
    total_resposta = 0
    tarefas_finalizadas = 0

    for task in sorted(simulator.tasks, key=lambda t: t.id):
        metricas = task.calcular_metricas()
        if metricas:
            tarefas_finalizadas += 1
            total_turnaround += metricas['turnaround_time']
            total_espera += metricas['waiting_time']
            total_resposta += metricas['response_time']
            print(f"{task.id:<5} | {metricas['turnaround_time']:<10} | "
                  f"{metricas['waiting_time']:<10} | {metricas['response_time']:<10}")
        else:
            print(f"{task.id:<5} | {'N/A (Não finalizada)':<42}")

    # Médias
    if tarefas_finalizadas > 0:
        print("-" * 49)
        print(f"{'MÉDIA':<5} | {total_turnaround / tarefas_finalizadas:<10.2f} | "
              f"{total_espera / tarefas_finalizadas:<10.2f} | "
              f"{total_resposta / tarefas_finalizadas:<10.2f}")


def main(args: argparse.Namespace):
    """
    Função principal que orquestra o fluxo da simulação.
    """
    
    # 1. Carregar configuração
    print(f"1. Carregando configuração de: {args.config_file}")
    parser = ConfigParser()
    config, tasks = parser.parse_file(args.config_file)
    
    avisos = parser.obter_avisos()
    if avisos:
        print("Avisos durante o parsing:")
        for aviso in avisos:
            print(f"   - {aviso}")
            
    print(f"   -> Algoritmo: {config['algoritmo']} (Quantum: {config.get('quantum')})")
    print(f"   -> Tarefas carregadas: {len(tasks)}")

    # 2. Criar scheduler
    print("2. Criando escalonador...")
    scheduler = SchedulerFactory.criar_scheduler(
        config['algoritmo'], 
        config.get('quantum')
    )

    # 3. Criar simulador
    print("3. Criando simulador...")
    simulator = Simulator(scheduler)
    simulator.carregar_tarefas(tasks)

    # 4. Executar simulação
    print(f"4. Executando simulação (Modo: {args.modo})...")
    
    resultados: Dict[str, Any] = {}
    
    if args.modo == 'passo':
        # Modo passo-a-passo imprime sua própria UI
        historico = simulator.executar_passo_a_passo()
        # Coleta resultados pós-execução
        resultados['tempo_total_ticks'] = simulator.clock.get_tempo()
        resultados['historico_execucao'] = historico
    else:
        # Modo completo
        resultados = simulator.executar_completo()
        print("   -> Simulação concluída.")

    # 5. Exibir resultados
    print("5. Exibindo resultados...")
    exibir_resultados(simulator, resultados)

    # 6. Gerar gráfico de Gantt
    print("\n6. Gerando gráfico de Gantt...")
    gantt = popular_gantt_chart(
        resultados['historico_execucao'], 
        simulator.tasks
    )
    
    # Exibe no terminal
    print("\n--- Gráfico de Gantt (Terminal) ---")
    gantt.exibir_terminal()
    print("--- Fim do Gráfico ---")

    # Exporta SVG (opcional)
    if args.output:
        try:
            # Garante que o diretório 'output' exista
            output_dir = 'output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"   -> Diretório '{output_dir}' criado.")
            
            # O método exportar_svg já prefixa com 'output/'
            path_svg = gantt.exportar_svg(args.output)
            print(f"\n   -> Gráfico de Gantt salvo em: {path_svg}")
        except IOError as e:
            print(f"\n   -> ERRO ao salvar SVG: {e}", file=sys.stderr)

    print("\nExecução finalizada.")


# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    args = None
    try:
        # Parse dos argumentos
        args = configurar_argumentos()
        
        # Chama a função principal
        main(args)
        
    except FileNotFoundError as e:
        print(f"\nERRO: Arquivo não encontrado.", file=sys.stderr)
        print(f"Detalhe: {e}", file=sys.stderr)
        sys.exit(1)
        
    except ValueError as e:
        print(f"\nERRO: Valor inválido ou arquivo de configuração mal formatado.", file=sys.stderr)
        print(f"Detalhe: {e}", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        print(f"\nERRO INESPERADO: {e.__class__.__name__}", file=sys.stderr)
        print(f"Detalhe: {e}", file=sys.stderr)
        # Em caso de erro, exibir o traceback pode ser útil para debug
        # import traceback
        # traceback.print_exc()
        sys.exit(1)