# Sistema de Histórico (Snapshot)

## Visão Geral

O módulo `history.py` implementa um sistema completo de histórico para o simulador de SO, permitindo capturar, armazenar e navegar através de snapshots do estado completo do sistema.

## Classes Implementadas

### SystemSnapshot

Representa um snapshot completo do estado do sistema em um momento específico.

**Atributos:**
- `tempo (int)`: Tempo atual do sistema no momento do snapshot
- `tasks_state (Dict)`: Estado serializado de todas as tarefas
- `scheduler_state (Dict)`: Estado serializado do escalonador
- `mutex_state (Dict)`: Estado serializado dos mutexes
- `io_state (Dict)`: Estado serializado das operações de I/O

**Métodos:**
- `to_dict()`: Serializa o snapshot para um dicionário
- `from_dict(data)`: Restaura um snapshot a partir de um dicionário (método de classe)

### HistoryManager

Gerencia histórico de snapshots do sistema e navegação temporal.

**Atributos:**
- `snapshots (List[SystemSnapshot])`: Lista de snapshots ordenada cronologicamente
- `indice_atual (int)`: Índice do snapshot atual na lista
- `max_snapshots (int)`: Número máximo de snapshots a manter (padrão: 1000)

**Métodos Principais:**
- `salvar_snapshot(simulator)`: Captura e salva um snapshot completo do sistema
- `restaurar_snapshot(index)`: Restaura o estado a partir de um snapshot específico
- `avancar()`: Avança para o próximo snapshot no histórico
- `retroceder()`: Retrocede para o snapshot anterior no histórico
- `obter_snapshot_atual()`: Obtém o snapshot atual
- `obter_info_historico()`: Obtém informações sobre o histórico para debug
- `limpar_historico()`: Remove todos os snapshots do histórico

## Características Técnicas

### Deep Copy
- Utiliza `copy.deepcopy()` para garantir que os snapshots não sejam afetados por mudanças posteriores no sistema
- Preserva a integridade dos dados através de cópias profundas de todos os objetos

### Limitação de Tamanho
- Mantém automaticamente apenas os últimos N snapshots (padrão: 1000)
- Remove snapshots antigos quando o limite é atingido
- Otimização de memória para execuções longas

### Serialização Completa
- **Tarefas**: ID, cor, ingresso, duração, prioridade, tempo restante, estado, tempos de início/fim, execução, preempções, eventos
- **Escalonador**: Tipo, quantum, fila de prontos, atributos específicos (alpha, tempo_atual_quantum)
- **Mutexes**: Estado dos mutexes e filas de espera
- **I/O**: Operações bloqueadas e operações ativas

### Navegação Temporal
- Navegação bidirecional (avançar/retroceder)
- Índice atual para rastreamento da posição no histórico
- Suporte a acesso direto por índice

## Estrutura de Dados

### Snapshot Serializado
```python
{
    'tempo': 5,
    'tasks_state': {
        'T1': {
            'id': 'T1',
            'cor': 'azul',
            'ingresso': 0,
            'duracao': 5,
            'prioridade': 1,
            'tempo_restante': 3,
            'estado': 'EXECUTANDO',
            'tempo_inicio': 2,
            'tempo_fim': None,
            'tempo_execucao': 2,
            'numero_preempcoes': 0,
            'eventos': [...]
        }
    },
    'scheduler_state': {
        'tipo': 'FIFOScheduler',
        'quantum': None,
        'fila_prontos': ['T1', 'T2']
    },
    'mutex_state': {
        'mutexes': {'mutex1': 'T1'},
        'mutex_queues': {'mutex1': ['T2']}
    },
    'io_state': {
        'blocked': {'T3': {'tipo': 'io', 'remaining': 2}},
        'operacoes': [('T3', 7)]
    }
}
```

## Uso

### Exemplo Básico
```python
from src.history import HistoryManager

# Criar gerenciador de histórico
history = HistoryManager()

# Salvar snapshot
history.salvar_snapshot(sistema)

# Executar alguns ticks
for i in range(5):
    sistema.executar_tick()
    history.salvar_snapshot(sistema)

# Navegar no histórico
sistema_anterior = history.retroceder()  # Volta um snapshot
sistema_seguinte = history.avancar()     # Avança um snapshot

# Acessar informações
info = history.obter_info_historico()
print(f"Total de snapshots: {info['total_snapshots']}")
print(f"Tempo atual: {info['tempo_atual']}")
```

### Exemplo com Limite Personalizado
```python
# Histórico com limite de 100 snapshots
history = HistoryManager(max_snapshots=100)

# Uso normal
history.salvar_snapshot(sistema)
```

### Restauração por Índice
```python
# Restaurar snapshot específico
estado = history.restaurar_snapshot(5)
if estado:
    print(f"Restaurado para tempo: {estado['tempo']}")
```

## Testes

### Teste Manual Básico
```python
history = HistoryManager()
history.salvar_snapshot(sistema)
# ... executa alguns ticks ...
sistema_anterior = history.retroceder()
```

### Validação de Funcionalidade
- ✅ Serialização/deserialização de snapshots
- ✅ Deep copy de objetos
- ✅ Navegação temporal (avançar/retroceder)
- ✅ Limitação de tamanho do histórico
- ✅ Acesso direto por índice
- ✅ Informações de debug

## Integração

O sistema de histórico foi projetado para ser usado em conjunto com o `Simulator` principal, capturando automaticamente o estado de todos os componentes:

- **Clock**: Tempo atual
- **Tasks**: Estado completo de todas as tarefas
- **Scheduler**: Tipo, configuração e fila de prontos
- **Mutex Manager**: Estado dos mutexes e filas de espera
- **IO Manager**: Operações bloqueadas e ativas

## Arquivos Criados

- `src/history.py`: Implementação principal
- `test_history_simple.py`: Teste básico de funcionalidade
- `test_history_manual.py`: Teste manual completo (para uso com simulador real)

## Conformidade com Especificação

✅ **Classe SystemSnapshot**
- ✅ Atributos: tempo, tasks_state, scheduler_state, mutex_state, io_state
- ✅ Método to_dict() - serializa estado
- ✅ Método from_dict() - restaura estado

✅ **Classe HistoryManager**
- ✅ Lista de snapshots: [snapshot1, snapshot2, ...]
- ✅ Método salvar_snapshot(sistema)
- ✅ Método restaurar_snapshot(index) → retorna estado
- ✅ Método avancar() - vai para próximo snapshot
- ✅ Método retroceder() - volta para snapshot anterior
- ✅ Atributo indice_atual

✅ **Funcionalidades Técnicas**
- ✅ Deep copy de objetos para evitar referências
- ✅ Limitar tamanho do histórico (opcional: últimos 1000 ticks)
- ✅ Documentar estrutura de dados

✅ **Teste Manual**
- ✅ Implementado conforme especificação
