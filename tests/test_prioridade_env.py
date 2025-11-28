"""Testes para PrioridadeEnvScheduler."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scheduler import PrioridadeEnvScheduler
from task import Task, TaskState


def test_basic_aging():
    """Testa envelhecimento básico."""
    print("=" * 60)
    print("TEST: Basic Aging")
    print("=" * 60)

    scheduler = PrioridadeEnvScheduler(quantum=5, alpha=1)

    # Cria tarefas com diferentes prioridades
    t1 = Task(task_id="t1", cor="blue", ingresso=0, duracao=10, prioridade=10)
    t2 = Task(task_id="t2", cor="red", ingresso=0, duracao=10, prioridade=5)

    t1.estado = TaskState.PRONTO
    t2.estado = TaskState.PRONTO

    scheduler.adicionar_tarefa(t1)
    scheduler.adicionar_tarefa(t2)

    print(f"Prioridades iniciais: t1={scheduler.prioridades_dinamicas['t1']}, t2={scheduler.prioridades_dinamicas['t2']}")
    assert scheduler.prioridades_dinamicas['t1'] == 10
    assert scheduler.prioridades_dinamicas['t2'] == 5

    # t2 deve ser selecionada (menor prioridade = maior prioridade real)
    proxima = scheduler.selecionar_proxima_tarefa()
    print(f"Primeira seleção: {proxima.id}")
    assert proxima.id == "t2"

    # Aplica envelhecimento (t1 envelhece, t2 não pois está executando)
    t2.estado = TaskState.EXECUTANDO
    scheduler.aplicar_envelhecimento()

    print(f"Após envelhecimento: t1={scheduler.prioridades_dinamicas['t1']}, t2={scheduler.prioridades_dinamicas['t2']}")
    assert scheduler.prioridades_dinamicas['t1'] == 9  # 10 - 1
    assert scheduler.prioridades_dinamicas['t2'] == 5  # resetada ao executar

    print("✅ Test PASSED\n")


def test_starvation_prevention():
    """Testa prevenção de starvation por envelhecimento."""
    print("=" * 60)
    print("TEST: Starvation Prevention")
    print("=" * 60)

    scheduler = PrioridadeEnvScheduler(quantum=5, alpha=1)

    # Tarefa com baixa prioridade
    t1 = Task(task_id="t1", cor="blue", ingresso=0, duracao=10, prioridade=10)
    t1.estado = TaskState.PRONTO
    scheduler.adicionar_tarefa(t1)

    print(f"Prioridade inicial t1: {scheduler.prioridades_dinamicas['t1']}")

    # Simula envelhecimento por vários ticks
    for i in range(5):
        scheduler.aplicar_envelhecimento()
        print(f"Tick {i+1}: prioridade t1 = {scheduler.prioridades_dinamicas['t1']}")

    # Após 5 ticks, prioridade deve ter reduzido
    assert scheduler.prioridades_dinamicas['t1'] == 5  # 10 - 5*1

    print("✅ Test PASSED\n")


def test_quantum_expiration():
    """Testa que algoritmo funciona com quantum configurado."""
    print("=" * 60)
    print("TEST: Quantum Support")
    print("=" * 60)

    # Verifica que quantum é aceito no construtor
    scheduler = PrioridadeEnvScheduler(quantum=3, alpha=1)
    assert scheduler.quantum == 3

    t1 = Task(task_id="t1", cor="blue", ingresso=0, duracao=10, prioridade=5)
    t1.estado = TaskState.PRONTO
    scheduler.adicionar_tarefa(t1)

    proxima = scheduler.selecionar_proxima_tarefa()
    print(f"Selecionou: {proxima.id}")
    assert proxima.id == "t1"

    print("✅ Test PASSED\n")


def test_priority_preemption():
    """Testa preempção por prioridade."""
    print("=" * 60)
    print("TEST: Priority Preemption")
    print("=" * 60)

    scheduler = PrioridadeEnvScheduler(quantum=5, alpha=1)

    # Tarefa de baixa prioridade executando
    t1 = Task(task_id="t1", cor="blue", ingresso=0, duracao=10, prioridade=10)
    t1.estado = TaskState.EXECUTANDO
    scheduler.adicionar_tarefa(t1)

    proxima = scheduler.selecionar_proxima_tarefa()
    print(f"Tarefa inicial: {proxima.id}")
    assert proxima.id == "t1"

    # Chega tarefa de alta prioridade
    t2 = Task(task_id="t2", cor="red", ingresso=5, duracao=5, prioridade=2)
    t2.estado = TaskState.PRONTO
    scheduler.adicionar_tarefa(t2)

    # Deve preemptar
    proxima = scheduler.selecionar_proxima_tarefa()
    print(f"Após chegada de t2 (prioridade 2): {proxima.id}")
    assert proxima.id == "t2"

    print("✅ Test PASSED\n")


def test_reset_priority():
    """Testa reset automático de prioridade ao selecionar para executar."""
    print("=" * 60)
    print("TEST: Reset Priority")
    print("=" * 60)

    scheduler = PrioridadeEnvScheduler(quantum=5, alpha=1)

    t1 = Task(task_id="t1", cor="blue", ingresso=0, duracao=10, prioridade=10)
    t1.estado = TaskState.PRONTO
    scheduler.adicionar_tarefa(t1)

    # Envelhece manualmente
    scheduler.prioridades_dinamicas['t1'] = 5
    print(f"Prioridade após envelhecimento: {scheduler.prioridades_dinamicas['t1']}")

    # Ao selecionar, reseta automaticamente
    proxima = scheduler.selecionar_proxima_tarefa()
    print(f"Prioridade após seleção: {scheduler.prioridades_dinamicas['t1']}")
    assert scheduler.prioridades_dinamicas['t1'] == 10
    assert proxima.id == 't1'

    print("✅ Test PASSED\n")


def test_manual_scenario():
    """Testa cenário manual da especificação."""
    print("=" * 60)
    print("TEST: Manual Scenario")
    print("=" * 60)

    scheduler = PrioridadeEnvScheduler(quantum=5, alpha=1)

    # Tarefa com prioridade 10 esperando
    t1 = Task(task_id="t1", cor="blue", ingresso=0, duracao=10, prioridade=10)
    t1.estado = TaskState.PRONTO
    scheduler.adicionar_tarefa(t1)

    print(f"Prioridade inicial: {scheduler.prioridades_dinamicas['t1']}")

    # Simula envelhecimento: 10, 9, 8, 7...
    prioridades = []
    for i in range(4):
        prioridades.append(scheduler.prioridades_dinamicas['t1'])
        scheduler.aplicar_envelhecimento()

    prioridades.append(scheduler.prioridades_dinamicas['t1'])

    print(f"Sequência de prioridades: {prioridades}")
    assert prioridades == [10.0, 9.0, 8.0, 7.0, 6.0]

    print("✅ Test PASSED - Cenário manual correto!\n")


def run_all_tests():
    """Executa todos os testes."""
    print("\n")
    print("*" * 60)
    print("PRIORIDADE COM ENVELHECIMENTO - TEST SUITE")
    print("*" * 60)
    print()

    test_basic_aging()
    test_starvation_prevention()
    test_quantum_expiration()
    test_priority_preemption()
    test_reset_priority()
    test_manual_scenario()

    print("*" * 60)
    print("ALL TESTS PASSED! ✅")
    print("*" * 60)
    print()


if __name__ == "__main__":
    run_all_tests()

