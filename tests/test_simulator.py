from src.simulator import Simulator
from src.scheduler import FIFOScheduler
from src.task import TCB

def test_fifo_simulador():
    # Criar escalonador FIFO
    scheduler = FIFOScheduler()

    # Criar simulador
    sim = Simulator(scheduler)

    # Criar tarefas
    t1 = TCB("T1", "azul", ingresso=0, duracao=3)
    t2 = TCB("T2", "verde", ingresso=3, duracao=2)
    t3 = TCB("T3", "vermelho", ingresso=5, duracao=4)

    # Carregar tarefas no simulador
    sim.carregar_tarefas([t1, t2, t3])

    # Executar simulação com log
    sim.executar(log=True)

    # Mostrar histórico
    print("\nHistórico de execução:")
    print(sim.historico_execucao)

    # Mostrar resumo das tarefas
    for t in sim.tasks:
        print(f"\nResumo de {t.id}:")
        for linha in t.obter_historico_resumido():
            print(linha)

def test_execucao_completa_task_2_3():
    """
    Teste específico para a Task 2.3, usando o novo método
    executar_completo() e o teste manual da sua captura de tela.
    """
    print("\n--- Teste Task 2.3: executar_completo() ---")
    
    scheduler = FIFOScheduler()
    sim = Simulator(scheduler)
    
    t1 = TCB("T1", "azul", ingresso=0, duracao=3)
    t2 = TCB("T2", "verde", ingresso=3, duracao=2)
    t3 = TCB("T3", "vermelho", ingresso=5, duracao=4)
    
    sim.carregar_tarefas([t1, t2, t3])

    resultado = sim.executar_completo()

    print(f"Simulação concluída em {resultado['tempo_total']} ticks")
    print(f"Tempo de execução real: {resultado['tempo_execucao_real_ms']:.2f} ms")
    
    print("\nHistórico de execução final:")
    print(resultado['historico_execucao'])

# Executa o teste
if __name__ == "__main__":
    test_fifo_simulador()
    test_execucao_completa_task_2_3()
