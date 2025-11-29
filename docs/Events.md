# Events - Documentação do Sistema de Eventos

## Visão Geral

O módulo `events.py` define o sistema de eventos para o simulador de SO. Eventos são ações que ocorrem durante a execução de uma tarefa em momentos específicos, como operações de I/O ou solicitação/liberação de mutexes.

## Conceitos

- **Evento**: Ação que ocorre em um tempo relativo específico durante a execução de uma tarefa
- **Tempo Relativo**: Tempo em relação ao início da execução da tarefa (ex: evento no tempo_relativo=3 dispara após 3 unidades de execução)
- **Processamento Automático**: Eventos são processados automaticamente pelo Simulator quando o `tempo_execucao` da tarefa atinge o `tempo_relativo` do evento

---

## Classes de Eventos

### Event (Classe Base)

Classe base abstrata para todos os eventos.

**Atributos:**
- `tipo` (str): String identificando o tipo de evento ('IO', 'LOCK', 'UNLOCK')
- `tempo_relativo` (int): Ticks após início da tarefa quando o evento ocorre
- `task_id` (str): Identificador da tarefa que gera o evento

**Métodos:**

#### `executar(self, sistema, tarefa)`
Executa o evento contra o simulador.

**Parâmetros:**
- `sistema`: Instância do Simulator
- `tarefa`: Instância da Task que disparou o evento

**Retorna:**
- `dict` opcional com descrição da ação realizada

#### `calcular_tempo_absoluto(self, tempo_inicio_tarefa)`
Calcula o tick absoluto quando o evento deve disparar.

**Parâmetros:**
- `tempo_inicio_tarefa` (int): Tempo absoluto quando a tarefa iniciou

**Retorna:**
- `int`: Tempo absoluto (tempo_inicio_tarefa + tempo_relativo)

---

### IOEvent

Evento de operação de I/O que bloqueia a tarefa por uma duração específica.

**Atributos Adicionais:**
- `duracao` (int): Número de ticks que a tarefa será bloqueada

**Comportamento:**
1. Bloqueia a tarefa (muda estado para BLOQUEADO)
2. Remove tarefa da fila de prontos
3. Registra operação no IOManager com tempo de conclusão
4. Após duração, tarefa é automaticamente desbloqueada pelo Simulator

**Exemplo:**
```python
from src.events import IOEvent

# I/O de 3 ticks que ocorre após 2 unidades de execução
evento_io = IOEvent(
    tipo='IO',
    tempo_relativo=2,
    task_id='T1',
    duracao=3
)
```

**Fluxo de Execução:**
```
Tempo de execução da tarefa = 2
↓ IOEvent dispara
Tarefa bloqueada (estado = BLOQUEADO)
Tempo de conclusão = tempo_atual + 3
↓ 3 ticks depois
IOManager detecta conclusão
Tarefa desbloqueada (estado = PRONTO)
Tarefa retorna à fila de prontos
```

---

### MutexLockEvent

Evento de solicitação de mutex (trava de exclusão mútua).

**Atributos Adicionais:**
- `mutex_id` (str): Identificador do mutex a solicitar

**Comportamento:**
1. Solicita mutex ao MutexManager
2. Se mutex disponível: tarefa obtém posse e continua executando
3. Se mutex ocupado: tarefa é bloqueada e enfileirada até mutex ser liberado

**Exemplo:**
```python
from src.events import MutexLockEvent

# Solicita mutex após 1 unidade de execução
evento_lock = MutexLockEvent(
    tipo='LOCK',
    tempo_relativo=1,
    task_id='T1',
    mutex_id='recurso1'
)
```

**Fluxo de Execução:**

**Caso 1: Mutex Disponível**
```
Tempo de execução da tarefa = 1
↓ MutexLockEvent dispara
MutexManager verifica disponibilidade
Mutex livre → concedido à tarefa
Tarefa continua executando (possui mutex)
```

**Caso 2: Mutex Ocupado**
```
Tempo de execução da tarefa = 1
↓ MutexLockEvent dispara
MutexManager verifica disponibilidade
Mutex ocupado por outra tarefa
Tarefa bloqueada (estado = BLOQUEADO)
Tarefa enfileirada para aguardar mutex
↓ Quando mutex for liberado
Tarefa desbloqueada automaticamente
Tarefa recebe mutex e volta a executar
```

---

### MutexUnlockEvent

Evento de liberação de mutex.

**Atributos Adicionais:**
- `mutex_id` (str): Identificador do mutex a liberar

**Comportamento:**
1. Libera mutex do MutexManager
2. Se há tarefas aguardando: próxima tarefa na fila recebe mutex e é desbloqueada
3. Se não há tarefas aguardando: mutex fica livre

**Exemplo:**
```python
from src.events import MutexUnlockEvent

# Libera mutex após 8 unidades de execução
evento_unlock = MutexUnlockEvent(
    tipo='UNLOCK',
    tempo_relativo=8,
    task_id='T1',
    mutex_id='recurso1'
)
```

**Fluxo de Execução:**

**Caso 1: Sem Fila de Espera**
```
Tempo de execução da tarefa = 8
↓ MutexUnlockEvent dispara
MutexManager libera mutex
Sem tarefas aguardando
Mutex fica livre
```

**Caso 2: Com Fila de Espera**
```
Tempo de execução da tarefa = 8
↓ MutexUnlockEvent dispara
MutexManager libera mutex
Próxima tarefa (T2) na fila recebe mutex
T2 desbloqueada (estado = PRONTO)
T2 adicionada à fila de prontos
```

---

## Integração com Simulator

Os eventos são processados automaticamente pelo Simulator no método `processar_eventos_tarefa()`:

1. **Verificação**: A cada tick, o Simulator verifica se há eventos da tarefa em execução
2. **Comparação**: Compara `tempo_execucao` da tarefa com `tempo_relativo` dos eventos
3. **Disparo**: Quando iguais, executa o evento via `evento.executar(self, tarefa)`
4. **Registro**: Registra o evento processado em `eventos_pendentes`
5. **Remoção**: Remove o evento da lista de eventos da tarefa

---

## Exemplo Completo

### Cenário: Tarefa com I/O e Mutex

```python
from src.simulator import Simulator
from src.scheduler import FIFOScheduler
from src.task import Task
from src.events import IOEvent, MutexLockEvent, MutexUnlockEvent

# Criar eventos
eventos = [
    # Após 2 unidades de execução: bloqueia por I/O de 3 ticks
    IOEvent(tipo='IO', tempo_relativo=2, task_id='T1', duracao=3),
    
    # Após 6 unidades de execução: solicita mutex
    MutexLockEvent(tipo='LOCK', tempo_relativo=6, task_id='T1', mutex_id='recurso1'),
    
    # Após 8 unidades de execução: libera mutex
    MutexUnlockEvent(tipo='UNLOCK', tempo_relativo=8, task_id='T1', mutex_id='recurso1')
]

# Criar tarefa com eventos
tarefa = Task('T1', 'azul', 0, 10, 1, eventos=eventos)

# Criar e executar simulador
simulador = Simulator(FIFOScheduler())
simulador.carregar_tarefas([tarefa])
simulador.executar()

# Verificar eventos processados
print(simulador.eventos_pendentes)
# {'T1': [
#     {'tempo': 2, 'tipo': 'IO', 'resultado': {...}},
#     {'tempo': 6, 'tipo': 'LOCK', 'resultado': {...}},
#     {'tempo': 8, 'tipo': 'UNLOCK', 'resultado': {...}}
# ]}
```

### Linha do Tempo da Execução

```
Tick 0: T1 admitida (estado: PRONTO)
Tick 1: T1 inicia execução (tempo_execucao=1)
Tick 2: T1 executa (tempo_execucao=2)
        → IOEvent dispara
        → T1 bloqueada para I/O
Tick 3: T1 bloqueada (I/O em andamento)
Tick 4: T1 bloqueada (I/O em andamento)
Tick 5: IOManager detecta conclusão
        → T1 desbloqueada e volta à fila
Tick 6: T1 executa (tempo_execucao=6)
        → MutexLockEvent dispara
        → T1 obtém mutex 'recurso1'
Tick 7: T1 executa (tempo_execucao=7) com mutex
Tick 8: T1 executa (tempo_execucao=8)
        → MutexUnlockEvent dispara
        → T1 libera mutex 'recurso1'
Tick 9: T1 executa (tempo_execucao=9)
Tick 10: T1 executa (tempo_execucao=10)
         → T1 termina (estado: TERMINADO)
```

---

## Criação de Eventos Personalizados

Para criar novos tipos de eventos, herde da classe `Event`:

```python
from src.events import Event

class CustomEvent(Event):
    def __init__(self, tipo, tempo_relativo, task_id, parametro_custom):
        super().__init__(tipo, tempo_relativo, task_id)
        self.parametro_custom = parametro_custom
    
    def executar(self, sistema, tarefa):
        # Implementar lógica personalizada
        print(f"Evento custom executado: {self.parametro_custom}")
        
        return {
            'event': self.tipo,
            'task_id': self.task_id,
            'custom_data': self.parametro_custom
        }
```

---

## Notas Importantes

1. **Tempo Relativo vs Absoluto**: Eventos usam tempo relativo (baseado em execução da tarefa), não tempo absoluto do sistema
2. **Processamento Único**: Cada evento é processado apenas uma vez e então removido
3. **Ordem de Processamento**: Eventos com mesmo tempo_relativo são processados na ordem em que aparecem na lista
4. **Estado da Tarefa**: Eventos só são processados se a tarefa estiver executando
5. **Exceções**: Erros em eventos são capturados e não quebram a simulação

---

## API de Integração

### Para o Simulator

Os métodos do Simulator usados pelos eventos:

- `bloquear_tarefa(task_id, duracao)` - Usado por IOEvent
- `solicitar_mutex(task_id, mutex_id)` - Usado por MutexLockEvent
- `liberar_mutex(task_id, mutex_id)` - Usado por MutexUnlockEvent

### Para Diagnóstico

Verificar eventos processados:

```python
# Após executar simulação
eventos_processados = simulador.eventos_pendentes

# Para uma tarefa específica
if 'T1' in eventos_processados:
    for evento in eventos_processados['T1']:
        print(f"Tempo {evento['tempo']}: {evento['tipo']}")
```

---

## Referências

- [Simulator.md](Simulator.md) - Documentação do Simulator
- [SimulatorEvents.md](SimulatorEvents.md) - Integração de eventos
- [IOManager.md](IOManager.md) - Gerenciador de I/O
- [MutexManager.md](MutexManager.md) - Gerenciador de mutexes
- [Task.md](Task.md) - Documentação de tarefas
