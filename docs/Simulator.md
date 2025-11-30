## Simulator - Documentação

## Visão Geral
O módulo `simulator.py` implementa a classe principal do simulador de Sistema Operacional. Ele define a classe `Simulator`, que orquestra a simulação do sistema operacional, controlando o avanço do relógio, a chegada e execução das tarefas, a comunicação com o escalonador e o registro do histórico de execução.

## Conceitos
- **Simulador (`Simulator`)**: Classe que representa o simulador de Sistema Operacional.
- **Relógio (`Clock`)**: Gerencia o tempo da simulação.
- **Tarefa (`Task`)**: Representa um processo ou tarefa no sistema.
- **Escalonador (`Scheduler`)**: Componente responsável por decidir a ordem de execução das tarefas.
- **Histórico de Execução**: Registro do que ocorreu em cada unidade de tempo (tick).
- **Preempção**: Capacidade de pausar uma tarefa em execução para dar lugar a outra de maior prioridade ou menor tempo restante.

## Classe `Simulator`
Classe principal que gerencia a simulação do sistema operacional.

### Atributos
- `clock` (`Clock`): Instância do relógio da simulação.
- `scheduler` (`Scheduler`): Instância do escalonador utilizado para gerenciar a execução das tarefas.
- `tasks` (list): Lista de todas as tarefas (`Task`) carregadas no sistema.
- `historico_execucao` (list): Lista de tuplas `(tempo, id_tarefa)` registrando o que foi executado em cada tick. Quando a CPU está ociosa, registra `(tempo, None)`.
- `gantt` (`GanttChart`): Instância do gráfico de Gantt para visualização da execução.
- `mutex_manager` (`MutexManager`): Gerenciador de mutexes para sincronização entre tarefas.
- `io_manager` (`IOManager`): Gerenciador de operações de I/O.
- `eventos_pendentes` (dict): Dicionário mapeando task_id para lista de eventos processados (para histórico/debug).
- `_blocked` (dict): Estrutura legada para controle de bloqueios (mantida para compatibilidade).
- `mutexes` (dict): Estrutura legada de mutexes sincronizada com MutexManager.
- `_mutex_queues` (dict): Estrutura legada de filas de mutex sincronizada com MutexManager.

### Métodos
#### `__init__(self, scheduler)`
Inicializa o simulador com um escalonador e o relógio zerado. Também inicializa os gerenciadores de recursos (IOManager e MutexManager) e estruturas de controle de eventos.
**Parâmetros:**
- `scheduler` (`Scheduler`): A instância do escalonador a ser utilizada.  
**Retorna:**
- `None`

#### `carregar_tarefas(self, tasks)`
Recebe uma lista de `Task` e prepara as tarefas para a simulação, definindo o estado inicial como `NOVO`.  
**Parâmetros:**
- `tasks` (list of `Task`): Lista das tarefas a serem carregadas.  
**Retorna:**
- `None`

#### `verificar_novas_tarefas(self)`
Verifica o tempo de ingresso das tarefas e admite (muda o estado para `PRONTO` e adiciona ao escalonador) as que chegam no tempo atual.  
**Retorna:**
- `None`

#### `executar_tick(self)`
Executa um ciclo completo da simulação (1 unidade de tempo) com fluxo integrado de eventos:
1. **Desbloqueia tarefas com I/O completo**: Verifica operações de I/O concluídas via IOManager e desbloqueia tarefas.
2. **Verifica novas tarefas**: Admite tarefas cujo tempo de ingresso chegou.
3. **Aplica envelhecimento**: Se o scheduler suportar, aplica envelhecimento de prioridades.
4. **Seleciona próxima tarefa**: Pede ao escalonador a próxima tarefa.
5. **Realiza preempção**: Se houver mudança de tarefa, pausa a tarefa anterior.
6. **Executa tarefa**: Executa a tarefa selecionada por 1 unidade de tempo.
7. **Processa eventos**: Processa eventos da tarefa executada (I/O, Mutex, etc).
8. **Atualiza histórico**: Registra execução no histórico.
9. **Avança relógio**: Incrementa o tempo do sistema.

**Retorna:**
- `None`

**Nota**: Este fluxo suporta processamento automático de eventos (IOEvent, MutexLockEvent, MutexUnlockEvent) definidos nas tarefas.

#### `verificar_io_conclusoes(self)`
Verifica operações de I/O concluídas usando o IOManager e desbloqueia as tarefas correspondentes. Adiciona tarefas desbloqueadas de volta à fila de prontos do scheduler.
**Retorna:**
- `None`

#### `processar_eventos_tarefa(self, tarefa, tempo_atual)`
Processa eventos da tarefa que devem ocorrer no tick atual. Verifica eventos com tempo relativo igual ao tempo de execução da tarefa.
**Parâmetros:**
- `tarefa` (`Task`): Tarefa em execução.
- `tempo_atual` (int): Tempo atual do sistema.
**Retorna:**
- `None`

#### `bloquear_tarefa(self, task_id, duracao)`
Bloqueia uma tarefa por I/O usando o IOManager. Remove a tarefa da fila de prontos e registra a operação de I/O.
**Parâmetros:**
- `task_id` (str): ID da tarefa a bloquear.
- `duracao` (int): Duração do bloqueio em ticks.
**Retorna:**
- `bool`: `True` se bloqueado com sucesso, `False` caso contrário.

#### `solicitar_mutex(self, task_id, mutex_id)`
Solicita um mutex para uma tarefa usando o MutexManager. Se o mutex não estiver disponível, bloqueia a tarefa e a coloca em fila de espera.
**Parâmetros:**
- `task_id` (str): ID da tarefa solicitante.
- `mutex_id` (str): ID do mutex solicitado.
**Retorna:**
- `bool`: `True` se mutex foi concedido imediatamente, `False` se a tarefa foi enfileirada.

#### `liberar_mutex(self, task_id, mutex_id)`
Libera um mutex usando o MutexManager. Se houver tarefas na fila de espera, concede o mutex automaticamente à próxima tarefa e a desbloqueia.
**Parâmetros:**
- `task_id` (str): ID da tarefa que possui o mutex.
- `mutex_id` (str): ID do mutex a liberar.
**Retorna:**
- `bool`: `True` se liberado com sucesso, `False` se a tarefa não possui o mutex.

#### `tem_tarefas_pendentes(self)`
Verifica se ainda existem tarefas em qualquer estado que não seja `TERMINADO`.  
**Retorna:**
- `bool`: `True` se houver tarefas não terminadas, `False` caso contrário.

#### `executar(self, tempo_max=None, log=False)`
Inicia a simulação do sistema operacional e a executa tick a tick até que todas as tarefas terminem ou o tempo máximo seja atingido.  
**Parâmetros:**
- `tempo_max` (int, optional): Tempo máximo de simulação. Se `None`, executa até o fim. Padrão é `None`.
- `log` (bool, optional): Se `True`, imprime mensagens de log durante a execução. Padrão é `False`.  
**Retorna:**
- `list`: O `historico_execucao` completo da simulação.

## Exemplo de Uso

### Uso Básico
```python
# Importações necessárias
from src.simulator import Simulator
from src.task import Task
from src.scheduler import FIFOScheduler, SchedulerFactory

# Criação de tarefas
tarefa1 = Task(task_id="t01", cor="#FF0000", ingresso=0, duracao=5, prioridade=1)
tarefa2 = Task(task_id="t02", cor="#00FF00", ingresso=2, duracao=3, prioridade=1)

# Inicialização do simulador com um escalonador
simulador = Simulator(FIFOScheduler())

# Carregamento e execução
simulador.carregar_tarefas([tarefa1, tarefa2])
historico = simulador.executar(log=True)
# historico conterá a lista de (tempo, id_tarefa_executada)
# Exemplo: [(0, 't01'), (1, 't01'), (2, 't01'), (3, 't02'), (4, 't02'), ...]
# Se CPU ociosa: [(tempo, None)]
```

### Uso com Eventos
```python
from src.simulator import Simulator
from src.scheduler import FIFOScheduler
from src.task import Task
from src.events import IOEvent, MutexLockEvent, MutexUnlockEvent

# Criar eventos para a tarefa
eventos = [
    IOEvent(tipo='IO', tempo_relativo=2, task_id='T1', duracao=3),
    MutexLockEvent(tipo='LOCK', tempo_relativo=6, task_id='T1', mutex_id='recurso1'),
    MutexUnlockEvent(tipo='UNLOCK', tempo_relativo=8, task_id='T1', mutex_id='recurso1')
]

# Criar tarefa com eventos
tarefa = Task('T1', 'azul', 0, 10, 1, eventos=eventos)

# Criar simulador e executar
simulador = Simulator(FIFOScheduler())
simulador.carregar_tarefas([tarefa])
simulador.executar()

# Verificar eventos processados
print(simulador.eventos_pendentes)
# {'T1': [{'tempo': 2, 'tipo': 'IO', 'resultado': {...}}, ...]}
```

### Integração com Sistema de Histórico
```python
from src.simulator import Simulator
from src.history import HistoryManager
from src.scheduler import FIFOScheduler
from src.task import Task

# Criar simulador
simulador = Simulator(FIFOScheduler())
tarefa = Task('T1', 'azul', 0, 10, 1)
simulador.carregar_tarefas([tarefa])

# Criar gerenciador de histórico
history = HistoryManager()

# Executar salvando snapshots
for i in range(15):
    history.salvar_snapshot(simulador)
    simulador.executar_tick()

# Navegar no histórico
estado_anterior = history.retroceder()
estado_seguinte = history.avancar()
```

