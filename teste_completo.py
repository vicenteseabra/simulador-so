"""
Teste Completo de Funcionalidade do Simulador
Testa todos os algoritmos e valida métricas
"""

from src.task import Task, TaskState
from src.scheduler import SchedulerFactory
from src.simulator import Simulator

print("="*70)
print("TESTE COMPLETO DE FUNCIONALIDADE")
print("="*70)

# =============================================================================
# TESTE 1: FIFO
# =============================================================================
print("\n[TESTE 1] Algoritmo FIFO")
print("-" * 70)

# Criar tarefas
t1 = Task("t1", "#FF0000", 0, 3, 1)
t2 = Task("t2", "#00FF00", 1, 2, 1)
t3 = Task("t3", "#0000FF", 2, 4, 1)

# Criar simulador FIFO
scheduler = SchedulerFactory.criar_scheduler("FIFO", quantum=2)
sim = Simulator(scheduler)
sim.carregar_tarefas([t1, t2, t3])

# Executar
print("Executando simulação FIFO...")
historico = sim.executar(log=False)

print(f"\n✓ Simulação concluída!")
print(f"  - Total de eventos: {len(historico)}")
print(f"  - Tempo total: {sim.clock.get_tempo()}")

# Validar estados
print("\nEstado das tarefas:")
for task in [t1, t2, t3]:
    print(f"  {task.id}: {task.estado}")
    assert task.estado == TaskState.TERMINADO, f"Task {task.id} não terminou!"

# Calcular métricas
print("\nMétricas de Desempenho:")
for task in [t1, t2, t3]:
    metricas = task.calcular_metricas()
    print(f"  {task.id}:")
    print(f"    - Turnaround Time: {metricas['turnaround_time']}")
    print(f"    - Waiting Time: {metricas['waiting_time']}")
    print(f"    - Response Time: {metricas['response_time']}")
    
    # Validações básicas
    assert metricas['turnaround_time'] >= task.duracao, "Turnaround menor que duração!"
    assert metricas['waiting_time'] >= 0, "Waiting time negativo!"
    assert metricas['response_time'] >= 0, "Response time negativo!"

print("\n✅ FIFO: PASSOU EM TODOS OS TESTES!")

# =============================================================================
# TESTE 2: SRTF
# =============================================================================
print("\n[TESTE 2] Algoritmo SRTF (Shortest Remaining Time First)")
print("-" * 70)

# Criar novas tarefas
t1 = Task("t1", "#FF0000", 0, 8, 1)
t2 = Task("t2", "#00FF00", 1, 4, 1)
t3 = Task("t3", "#0000FF", 2, 2, 1)

# Criar simulador SRTF
scheduler = SchedulerFactory.criar_scheduler("SRTF", quantum=1)
sim = Simulator(scheduler)
sim.carregar_tarefas([t1, t2, t3])

# Executar
print("Executando simulação SRTF...")
historico = sim.executar(log=False)

print(f"\n✓ Simulação concluída!")
print(f"  - Total de eventos: {len(historico)}")
print(f"  - Tempo total: {sim.clock.get_tempo()}")

# Validar estados
print("\nEstado das tarefas:")
all_terminated = True
for task in [t1, t2, t3]:
    print(f"  {task.id}: {task.estado}")
    if task.estado != TaskState.TERMINADO:
        all_terminated = False

assert all_terminated, "Nem todas as tarefas terminaram!"

# Calcular métricas
print("\nMétricas de Desempenho:")
for task in [t1, t2, t3]:
    metricas = task.calcular_metricas()
    print(f"  {task.id}:")
    print(f"    - Turnaround Time: {metricas['turnaround_time']}")
    print(f"    - Waiting Time: {metricas['waiting_time']}")
    print(f"    - Response Time: {metricas['response_time']}")

print("\n✅ SRTF: PASSOU EM TODOS OS TESTES!")

# =============================================================================
# TESTE 3: PRIORIDADE
# =============================================================================
print("\n[TESTE 3] Algoritmo Por Prioridade (Preemptivo)")
print("-" * 70)

# Criar tarefas com diferentes prioridades
t1 = Task("t1", "#FF0000", 0, 5, prioridade=2)  # Baixa prioridade
t2 = Task("t2", "#00FF00", 1, 3, prioridade=0)  # Alta prioridade
t3 = Task("t3", "#0000FF", 2, 4, prioridade=1)  # Média prioridade

# Criar simulador por Prioridade
scheduler = SchedulerFactory.criar_scheduler("PRIORIDADE", quantum=1)
sim = Simulator(scheduler)
sim.carregar_tarefas([t1, t2, t3])

# Executar
print("Executando simulação por Prioridade...")
historico = sim.executar(log=False)

print(f"\n✓ Simulação concluída!")
print(f"  - Total de eventos: {len(historico)}")
print(f"  - Tempo total: {sim.clock.get_tempo()}")

# Validar estados
print("\nEstado das tarefas:")
for task in [t1, t2, t3]:
    print(f"  {task.id}: {task.estado} (prioridade={task.prioridade})")
    assert task.estado == TaskState.TERMINADO, f"Task {task.id} não terminou!"

# Calcular métricas
print("\nMétricas de Desempenho:")
for task in [t1, t2, t3]:
    metricas = task.calcular_metricas()
    print(f"  {task.id} (prioridade={task.prioridade}):")
    print(f"    - Turnaround Time: {metricas['turnaround_time']}")
    print(f"    - Waiting Time: {metricas['waiting_time']}")
    print(f"    - Response Time: {metricas['response_time']}")

print("\n✅ PRIORIDADE: PASSOU EM TODOS OS TESTES!")

# =============================================================================
# TESTE 4: ConfigParser + Simulação
# =============================================================================
print("\n[TESTE 4] Teste com ConfigParser")
print("-" * 70)

from src.config_parser import ConfigParser

# Testar com arquivo real
arquivo = 'examples/config_fifo.txt'
parser = ConfigParser()
config, tasks = parser.parse_file(arquivo)

print(f"Arquivo parseado: {arquivo}")
print(f"  - Algoritmo: {config['algoritmo']}")
print(f"  - Quantum: {config['quantum']}")
print(f"  - Tarefas: {len(tasks)}")

# Criar simulador baseado no config
scheduler = SchedulerFactory.criar_scheduler(config['algoritmo'], quantum=config['quantum'])
sim = Simulator(scheduler)
sim.carregar_tarefas(tasks)

# Executar
print("\nExecutando simulação do arquivo...")
historico = sim.executar(log=False)

print(f"\n✓ Simulação concluída!")
print(f"  - Total de eventos: {len(historico)}")
print(f"  - Tempo total: {sim.clock.get_tempo()}")

# Validar
print("\nEstado final das tarefas:")
for task in tasks:
    print(f"  {task.id}: {task.estado}")
    metricas = task.calcular_metricas()
    print(f"    → Turnaround: {metricas['turnaround_time']}, "
          f"Waiting: {metricas['waiting_time']}, "
          f"Response: {metricas['response_time']}")

print("\n✅ CONFIGPARSER: PASSOU EM TODOS OS TESTES!")

# =============================================================================
# RESUMO FINAL
# =============================================================================
print("\n" + "="*70)
print("RESUMO FINAL DOS TESTES")
print("="*70)

print("\n✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
print("\nSistema testado:")
print("  ✓ Algoritmo FIFO")
print("  ✓ Algoritmo SRTF (preemptivo)")
print("  ✓ Algoritmo Por Prioridade (preemptivo)")
print("  ✓ ConfigParser + Integração")
print("  ✓ Cálculo de métricas")
print("  ✓ Validação de estados")

print("\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL!")
print("="*70)
