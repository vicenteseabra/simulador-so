"""
Script interativo para testar o modo passo-a-passo.
Cria um cenário simples de 3 tarefas para demonstração.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.simulator import Simulator
from src.scheduler import FIFOScheduler, SRTFScheduler, PriorityPreemptiveScheduler
from src.task import Task


def criar_cenario_simples():
    """Cria um cenário simples com 3 tarefas."""
    tasks = [
        Task("T1", "#FF0000", ingresso=0, duracao=4, prioridade=2),
        Task("T2", "#00FF00", ingresso=1, duracao=2, prioridade=1),
        Task("T3", "#0000FF", ingresso=3, duracao=3, prioridade=3),
    ]
    return tasks


def criar_cenario_preempcao():
    """Cria um cenário que demonstra preempção."""
    tasks = [
        Task("T1", "#FF0000", ingresso=0, duracao=5, prioridade=3),
        Task("T2", "#00FF00", ingresso=2, duracao=2, prioridade=1),  # Alta prioridade
        Task("T3", "#0000FF", ingresso=4, duracao=3, prioridade=2),
    ]
    return tasks


def criar_cenario_srtf():
    """Cria um cenário interessante para SRTF."""
    tasks = [
        Task("T1", "#FF0000", ingresso=0, duracao=7, prioridade=1),
        Task("T2", "#00FF00", ingresso=2, duracao=4, prioridade=1),
        Task("T3", "#0000FF", ingresso=4, duracao=1, prioridade=1),  # Mais curta
        Task("T4", "#FFFF00", ingresso=5, duracao=3, prioridade=1),
    ]
    return tasks


def main():
    """Menu principal para escolha de cenário e algoritmo."""
    print("=" * 60)
    print("  SIMULADOR DE ESCALONAMENTO - MODO PASSO-A-PASSO")
    print("=" * 60)
    print()
    
    # Escolha de cenário
    print("Escolha um cenário:")
    print("1. Cenário simples (3 tarefas)")
    print("2. Cenário com preempção (demonstra prioridade)")
    print("3. Cenário SRTF (demonstra menor tempo restante)")
    print()
    
    while True:
        try:
            escolha_cenario = input("Digite o número do cenário (1-3): ").strip()
            if escolha_cenario in ['1', '2', '3']:
                break
            print("Opção inválida. Escolha 1, 2 ou 3.")
        except (EOFError, KeyboardInterrupt):
            print("\nOperação cancelada.")
            return
    
    # Cria tarefas do cenário escolhido
    if escolha_cenario == '1':
        tasks = criar_cenario_simples()
        print("\n[Cenário Simples]")
        print("T1: ingresso=0, duração=4, prioridade=2")
        print("T2: ingresso=1, duração=2, prioridade=1")
        print("T3: ingresso=3, duração=3, prioridade=3")
    elif escolha_cenario == '2':
        tasks = criar_cenario_preempcao()
        print("\n[Cenário com Preempção]")
        print("T1: ingresso=0, duração=5, prioridade=3 (baixa)")
        print("T2: ingresso=2, duração=2, prioridade=1 (alta)")
        print("T3: ingresso=4, duração=3, prioridade=2 (média)")
    else:
        tasks = criar_cenario_srtf()
        print("\n[Cenário SRTF]")
        print("T1: ingresso=0, duração=7")
        print("T2: ingresso=2, duração=4")
        print("T3: ingresso=4, duração=1 (mais curta)")
        print("T4: ingresso=5, duração=3")
    
    print()
    
    # Escolha de algoritmo
    print("Escolha o algoritmo de escalonamento:")
    print("1. FIFO (First In, First Out)")
    print("2. SRTF (Shortest Remaining Time First)")
    print("3. Prioridade Preemptiva")
    print()
    
    while True:
        try:
            escolha_algo = input("Digite o número do algoritmo (1-3): ").strip()
            if escolha_algo in ['1', '2', '3']:
                break
            print("Opção inválida. Escolha 1, 2 ou 3.")
        except (EOFError, KeyboardInterrupt):
            print("\nOperação cancelada.")
            return
    
    # Cria scheduler
    if escolha_algo == '1':
        scheduler = FIFOScheduler()
        print("\n[Usando FIFO Scheduler]")
        print("Tipo: Não-preemptivo")
    elif escolha_algo == '2':
        scheduler = SRTFScheduler()
        print("\n[Usando SRTF Scheduler]")
        print("Tipo: Preemptivo (por tempo restante)")
    else:
        scheduler = PriorityPreemptiveScheduler()
        print("\n[Usando Priority Preemptive Scheduler]")
        print("Tipo: Preemptivo (por prioridade)")
    
    # Exibe quantum se o scheduler tiver
    if hasattr(scheduler, 'quantum') and scheduler.quantum is not None:
        print(f"Quantum: {scheduler.quantum}")
    
    print()
    
    # Cria e configura simulador
    simulator = Simulator(scheduler)
    simulator.carregar_tarefas(tasks)
    
    # Executa em modo passo-a-passo
    print("Iniciando simulação em modo passo-a-passo...")
    print()
    
    try:
        historico = simulator.executar_passo_a_passo()
        
        print("\n" + "=" * 60)
        print(f"Simulação concluída! Total de ticks: {len(historico)}")
        print("=" * 60)
        
        # Exibe métricas finais
        print("\nMétricas das tarefas:")
        for task in tasks:
            metricas = task.calcular_metricas()
            if metricas:
                print(f"\n{task.id}:")
                print(f"  Turnaround time: {metricas['turnaround_time']}")
                print(f"  Waiting time: {metricas['waiting_time']}")
                print(f"  Response time: {metricas['response_time']}")
        
    except KeyboardInterrupt:
        print("\n\nSimulação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n\nErro durante a simulação: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
