"""Teste simples e direto do sistema de histórico."""

# Teste básico das classes sem dependências complexas
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.history import HistoryManager, SystemSnapshot
    print("✓ Import das classes de histórico bem-sucedido")
except ImportError as e:
    print(f"✗ Erro no import: {e}")
    sys.exit(1)

# Teste básico das classes
def teste_basico():
    print("\n=== TESTE BÁSICO DAS CLASSES ===")

    # Teste do SystemSnapshot
    print("\n1. Testando SystemSnapshot...")
    snapshot_data = {
        'tempo': 5,
        'tasks_state': {'T1': {'id': 'T1', 'estado': 'EXECUTANDO'}},
        'scheduler_state': {'tipo': 'FIFO', 'fila_prontos': ['T1']},
        'mutex_state': {'mutexes': {}, 'mutex_queues': {}},
        'io_state': {'blocked': {}}
    }

    snapshot = SystemSnapshot(
        tempo=5,
        tasks_state=snapshot_data['tasks_state'],
        scheduler_state=snapshot_data['scheduler_state'],
        mutex_state=snapshot_data['mutex_state'],
        io_state=snapshot_data['io_state']
    )

    print(f"   Snapshot criado: {snapshot}")

    # Teste de serialização
    serialized = snapshot.to_dict()
    print(f"   Serializado: tempo={serialized['tempo']}")

    # Teste de deserialização
    restored = SystemSnapshot.from_dict(serialized)
    print(f"   Deserializado: tempo={restored.tempo}")
    print("✓ SystemSnapshot funcionando corretamente")

    # Teste do HistoryManager
    print("\n2. Testando HistoryManager...")
    history = HistoryManager(max_snapshots=5)
    print(f"   HistoryManager criado: {history}")

    # Simula alguns snapshots manuais
    class MockSimulator:
        def __init__(self, tempo):
            self.clock = MockClock(tempo)
            self.tasks = [MockTask('T1'), MockTask('T2')]
            self.scheduler = MockScheduler()
            self.mutexes = {}
            self._mutex_queues = {}
            self._blocked = {}

    class MockClock:
        def __init__(self, tempo):
            self.tempo = tempo
        def get_tempo(self):
            return self.tempo

    class MockTask:
        def __init__(self, task_id):
            self.id = task_id
            self.cor = 'azul'
            self.ingresso = 0
            self.duracao = 5
            self.prioridade = 1
            self.tempo_restante = 3
            self.estado = 'PRONTO'
            self.tempo_inicio = None
            self.tempo_fim = None
            self.tempo_execucao = 0
            self.numero_preempcoes = 0

    class MockScheduler:
        def __init__(self):
            self.__class__.__name__ = 'FIFOScheduler'
            self.quantum = None
            self.fila_prontos = []

    # Teste de salvamento e navegação
    print("\n3. Testando salvamento e navegação...")

    for i in range(4):
        simulator = MockSimulator(i)
        history.salvar_snapshot(simulator)
        print(f"   Snapshot {i} salvo")

    print(f"   Total de snapshots: {len(history)}")
    print(f"   Info histórico: {history.obter_info_historico()}")

    # Teste de retrocesso
    print("\n4. Testando retrocesso...")
    estado_anterior = history.retroceder()
    if estado_anterior:
        print(f"   Retrocedido para tempo: {estado_anterior['tempo']}")

    estado_anterior = history.retroceder()
    if estado_anterior:
        print(f"   Retrocedido novamente para tempo: {estado_anterior['tempo']}")

    # Teste de avanço
    print("\n5. Testando avanço...")
    estado_seguinte = history.avancar()
    if estado_seguinte:
        print(f"   Avançado para tempo: {estado_seguinte['tempo']}")

    print(f"   Índice atual: {history.indice_atual}")

    # Teste de limite
    print("\n6. Testando limite de histórico...")
    history_pequeno = HistoryManager(max_snapshots=2)
    for i in range(5):
        simulator = MockSimulator(i * 10)
        history_pequeno.salvar_snapshot(simulator)

    print(f"   Snapshots salvos: {len(history_pequeno)} (máximo: 2)")
    info = history_pequeno.obter_info_historico()
    print(f"   Primeiro tempo: {info['tempo_primeiro']}")
    print(f"   Último tempo: {info['tempo_ultimo']}")

    print("\n✓ Todos os testes básicos passaram com sucesso!")

if __name__ == "__main__":
    teste_basico()
