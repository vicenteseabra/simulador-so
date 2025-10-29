"""
Testes para validar os três algoritmos de escalonamento.
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scheduler import FIFOScheduler, SRTFScheduler, PriorityPreemptiveScheduler
from src.task import Task as TCB
from src.simulator import Simulator


def teste_fifo():
    """Testa escalonamento FIFO (não-preemptivo)."""
    print("\n=== TESTE FIFO ===")
    scheduler = FIFOScheduler()
    sim = Simulator(scheduler)
    
    t1 = TCB('T1', '#FF0000', 0, 3, 0)
    t2 = TCB('T2', '#00FF00', 1, 2, 0)
    t3 = TCB('T3', '#0000FF', 2, 2, 0)
    
    sim.carregar_tarefas([t1, t2, t3])
    historico = sim.executar()
    
    # Verifica ordem FIFO
    assert historico[0][1] == 'T1'
    assert historico[3][1] == 'T2'
    assert historico[5][1] == 'T3'
    
    # Verifica não-preempção
    assert t1.numero_preempcoes == 0
    assert t2.numero_preempcoes == 0
    assert t3.numero_preempcoes == 0
    
    print("FIFO: tarefas executam em ordem de chegada sem preempção")
    print(f"  Sequência: {[tid for _, tid in historico]}")
    return True


def teste_srtf():
    """Testa escalonamento SRTF (preemptivo)."""
    print("\n=== TESTE SRTF ===")
    scheduler = SRTFScheduler()
    sim = Simulator(scheduler)
    
    t1 = TCB('T1', '#FF0000', 0, 8, 0)
    t2 = TCB('T2', '#00FF00', 1, 4, 0)
    t3 = TCB('T3', '#0000FF', 2, 2, 0)
    
    sim.carregar_tarefas([t1, t2, t3])
    historico = sim.executar()
    
    # T3 tem menor duração (2), deve executar completamente após chegar
    # T2 tem duração 4, deve executar após T3
    # T1 tem duração 8, deve ser preemptado
    
    # Verifica que T1 foi preemptado
    assert t1.numero_preempcoes >= 1
    
    # Verifica que T3 executa completamente sem interrupção após chegar
    t3_execucoes = [t for t, tid in historico if tid == 'T3']
    assert t3_execucoes == [2, 3], "T3 deve executar continuamente em t=2,3"
    
    print("SRTF: seleciona tarefa com menor tempo restante")
    print(f"  Preempções: T1={t1.numero_preempcoes}, T2={t2.numero_preempcoes}, T3={t3.numero_preempcoes}")
    print(f"  Ordem execução T3: {t3_execucoes}")
    return True


def teste_prioridade():
    """Testa escalonamento por Prioridade Preemptivo."""
    print("\n=== TESTE PRIORIDADE PREEMPTIVO ===")
    scheduler = PriorityPreemptiveScheduler()
    sim = Simulator(scheduler)
    
    t1 = TCB('T1', '#FF0000', 0, 4, 3)  # prioridade baixa
    t2 = TCB('T2', '#00FF00', 1, 3, 1)  # prioridade alta
    t3 = TCB('T3', '#0000FF', 2, 2, 2)  # prioridade média
    
    sim.carregar_tarefas([t1, t2, t3])
    historico = sim.executar()
    
    # T2 tem maior prioridade (menor valor), deve preemptar T1
    assert historico[1][1] == 'T2', "T2 deve preemptar T1 em t=1"
    
    # T1 deve ser preemptado
    assert t1.numero_preempcoes >= 1
    
    # T2 executa completamente (prioridade 1 > todas)
    t2_execucoes = [t for t, tid in historico if tid == 'T2']
    assert len(t2_execucoes) == 3, "T2 deve executar 3 unidades"
    
    print("PRIORIDADE: seleciona tarefa com maior prioridade (menor valor)")
    print(f"  Preempções: T1={t1.numero_preempcoes}, T2={t2.numero_preempcoes}, T3={t3.numero_preempcoes}")
    print(f"  Prioridades: T1=3, T2=1, T3=2")
    return True


def main():
    """Executa todos os testes."""
    print("="*60)
    print("TESTES DOS ALGORITMOS DE ESCALONAMENTO")
    print("="*60)
    
    testes = [
        ("FIFO", teste_fifo),
        ("SRTF", teste_srtf),
        ("Prioridade Preemptivo", teste_prioridade)
    ]
    
    resultados = []
    
    for nome, teste_func in testes:
        try:
            teste_func()
            resultados.append((nome, True))
        except AssertionError as e:
            print(f"FALHOU: {e}")
            resultados.append((nome, False))
        except Exception as e:
            print(f"ERRO: {e}")
            resultados.append((nome, False))
    
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    
    for nome, passou in resultados:
        status = "✓" if passou else "✗"
        print(f"{status} {nome}")
    
    total_passou = sum(1 for _, p in resultados if p)
    print(f"\n{total_passou}/{len(resultados)} testes passaram")
    
    return all(p for _, p in resultados)


if __name__ == '__main__':
    sucesso = main()
    exit(0 if sucesso else 1)
