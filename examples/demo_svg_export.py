"""
Script de demonstração da exportação SVG do diagrama de Gantt.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gantt import GanttChart
from src.simulator import Simulator
from src.scheduler import FIFOScheduler, SRTFScheduler, PriorityPreemptiveScheduler
from src.task import Task


def criar_gantt_de_historico(historico, tasks):
    """
    Cria um GanttChart a partir do histórico de execução.
    
    Args:
        historico: Lista de tuplas (tempo, task_id)
        tasks: Lista de objetos Task
    
    Returns:
        GanttChart preenchido
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
        
        # Se mudou de tarefa ou é CPU ociosa
        if task_id != task_atual:
            # Fecha intervalo anterior
            if task_atual is not None:  # Ignora períodos IDLE
                cor = cores.get(task_atual, '#CCCCCC')
                gantt.adicionar_intervalo(task_atual, inicio_intervalo, tempo, cor)
            
            # Inicia novo intervalo
            inicio_intervalo = tempo
            task_atual = task_id
    
    # Fecha último intervalo
    if task_atual is not None:
        tempo_final = historico[-1][0] + 1
        cor = cores.get(task_atual, '#CCCCCC')
        gantt.adicionar_intervalo(task_atual, inicio_intervalo, tempo_final, cor)
    
    return gantt


def demo_simples():
    """Demonstração simples com FIFO."""
    print("=" * 60)
    print("DEMO 1: Escalonamento FIFO Simples")
    print("=" * 60)
    
    scheduler = FIFOScheduler()
    simulator = Simulator(scheduler)
    
    tasks = [
        Task("T1", "#FF6B6B", ingresso=0, duracao=3, prioridade=1),
        Task("T2", "#4ECDC4", ingresso=1, duracao=2, prioridade=2),
        Task("T3", "#45B7D1", ingresso=2, duracao=4, prioridade=3),
    ]
    
    simulator.carregar_tarefas(tasks)
    historico = simulator.executar()
    
    print(f"Simulação concluída: {len(historico)} ticks")
    
    gantt = criar_gantt_de_historico(historico, tasks)
    filepath = gantt.exportar_svg('gantt_fifo_simples.svg')
    
    print(f"SVG exportado: {filepath}")
    print()


def demo_preempcao():
    """Demonstração com preempção (SRTF)."""
    print("=" * 60)
    print("DEMO 2: Escalonamento SRTF (com preempção)")
    print("=" * 60)
    
    scheduler = SRTFScheduler()
    simulator = Simulator(scheduler)
    
    tasks = [
        Task("T1", "#FF6B6B", ingresso=0, duracao=7, prioridade=1),
        Task("T2", "#4ECDC4", ingresso=2, duracao=4, prioridade=1),
        Task("T3", "#45B7D1", ingresso=4, duracao=1, prioridade=1),
        Task("T4", "#FFA07A", ingresso=5, duracao=3, prioridade=1),
    ]
    
    simulator.carregar_tarefas(tasks)
    historico = simulator.executar()
    
    print(f"Simulação concluída: {len(historico)} ticks")
    
    gantt = criar_gantt_de_historico(historico, tasks)
    filepath = gantt.exportar_svg('gantt_srtf_preempcao.svg')
    
    print(f"SVG exportado: {filepath}")
    print()


def demo_prioridade():
    """Demonstração com prioridade preemptiva."""
    print("=" * 60)
    print("DEMO 3: Escalonamento por Prioridade")
    print("=" * 60)
    
    scheduler = PriorityPreemptiveScheduler()
    simulator = Simulator(scheduler)
    
    tasks = [
        Task("T1", "#14B42F", ingresso=0, duracao=5, prioridade=3),  # Baixa
        Task("T2", "#BCCD4E", ingresso=2, duracao=2, prioridade=1),  # Alta
        Task("T3", "#AC16B9", ingresso=4, duracao=3, prioridade=2),  # Média
    ]
    
    simulator.carregar_tarefas(tasks)
    historico = simulator.executar()
    
    print(f"Simulação concluída: {len(historico)} ticks")
    
    gantt = criar_gantt_de_historico(historico, tasks)
    filepath = gantt.exportar_svg('gantt_prioridade.svg')
    
    print(f"SVG exportado: {filepath}")
    print()


def demo_complexo():
    """Demonstração com cenário mais complexo."""
    print("=" * 60)
    print("DEMO 4: Cenário Complexo (6 tarefas)")
    print("=" * 60)
    
    scheduler = SRTFScheduler()
    simulator = Simulator(scheduler)
    
    tasks = [
        Task("T1", "#FF6B6B", ingresso=0, duracao=8, prioridade=1),
        Task("T2", "#4ECDC4", ingresso=1, duracao=4, prioridade=2),
        Task("T3", "#45B7D1", ingresso=2, duracao=9, prioridade=3),
        Task("T4", "#FFA07A", ingresso=3, duracao=5, prioridade=1),
        Task("T5", "#95E1D3", ingresso=5, duracao=2, prioridade=2),
        Task("T6", "#F38181", ingresso=6, duracao=6, prioridade=3),
    ]
    
    simulator.carregar_tarefas(tasks)
    historico = simulator.executar()
    
    print(f"Simulação concluída: {len(historico)} ticks")
    
    gantt = criar_gantt_de_historico(historico, tasks)
    filepath = gantt.exportar_svg('gantt_complexo.svg')
    
    print(f"SVG exportado: {filepath}")
    print()


def main():
    """Executa todas as demonstrações."""
    print("\n" + "=" * 60)
    print("  DEMONSTRAÇÃO DE EXPORTAÇÃO SVG - DIAGRAMA DE GANTT")
    print("=" * 60)
    print()
    
    demo_simples()
    demo_preempcao()
    demo_prioridade()
    demo_complexo()
    
    print("=" * 60)
    print("Todas as demonstrações concluídas!")
    print("Arquivos SVG salvos no diretório 'output/'")
    print("Abra os arquivos .svg em um navegador para visualizar.")
    print("=" * 60)


if __name__ == '__main__':
    main()
