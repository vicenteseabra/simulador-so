import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scheduler import FIFOScheduler
from src.simulator import Simulator
from src.task import Task


def test_fifo_simulador():
    """Teste básico do simulador com FIFO."""
    print("\n=== Teste FIFO Simulador ===")
    
    # Criar escalonador FIFO
    scheduler = FIFOScheduler()

    # Criar simulador
    sim = Simulator(scheduler)

    # Criar tarefas
    t1 = Task("T1", "#0000FF", ingresso=0, duracao=3, prioridade=1)
    t2 = Task("T2", "#00FF00", ingresso=3, duracao=2, prioridade=1)
    t3 = Task("T3", "#FF0000", ingresso=5, duracao=4, prioridade=1)

    # Carregar tarefas no simulador
    sim.carregar_tarefas([t1, t2, t3])

    # Executar simulação
    historico = sim.executar(log=False)

    # Mostrar histórico
    print(f"\nHistórico de execução ({len(historico)} eventos):")
    for tempo, task_id in historico:
        print(f"  t={tempo}: {task_id if task_id else 'CPU OCIOSA'}")

    # Mostrar métricas das tarefas
    print("\nMétricas das Tarefas:")
    for t in sim.tasks:
        metricas = t.calcular_metricas()
        print(f"\n{t.id}:")
        print(f"  Estado: {t.estado}")
        print(f"  Turnaround Time: {metricas['turnaround_time']}")
        print(f"  Waiting Time: {metricas['waiting_time']}")
        print(f"  Response Time: {metricas['response_time']}")
    
    print("\n✅ Teste FIFO concluído com sucesso!")


def test_execucao_completa_task_2_3():
    """
    Teste específico para a Task 2.3, usando o método executar_completo().
    """
    print("\n=== Teste Task 2.3: executar_completo() ===")
    
    scheduler = FIFOScheduler()
    sim = Simulator(scheduler)
    
    t1 = Task("T1", "#0000FF", ingresso=0, duracao=3, prioridade=1)
    t2 = Task("T2", "#00FF00", ingresso=3, duracao=2, prioridade=1)
    t3 = Task("T3", "#FF0000", ingresso=5, duracao=4, prioridade=1)
    
    sim.carregar_tarefas([t1, t2, t3])

    resultado = sim.executar_completo()

    print(f"\n✓ Simulação concluída em {resultado['tempo_total_ticks']} ticks")
    print(f"✓ Tempo de execução real: {resultado['tempo_execucao_real_ms']:.2f} ms")
    print(f"✓ Eventos no histórico: {len(resultado['historico_execucao'])}")
    
    # Validações
    assert resultado['tempo_total_ticks'] > 0, "Tempo total deve ser > 0"
    assert resultado['tempo_execucao_real_ms'] >= 0, "Tempo real deve ser >= 0"
    assert len(resultado['historico_execucao']) > 0, "Histórico não pode estar vazio"
    
    print("\n✅ Teste executar_completo() passou!")


# Executa os testes
if __name__ == "__main__":
    test_fifo_simulador()
    test_execucao_completa_task_2_3()
    print("\n" + "="*50)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("="*50)

