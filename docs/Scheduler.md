## Scheduler - Documentação

## Visão Geral

O módulo define a estrutura base para todos os algoritmos de escalonamento do sistema operacional. Ele introduz a classe abstrata `Scheduler`, que estabelece a interface para gerenciamento da fila de tarefas prontas e a seleção da próxima tarefa a ser executada. O módulo também inclui uma implementação concreta, o `FIFOScheduler`.

---

## Conceitos

- **Escalonador (`Scheduler`)**: Classe base abstrata para algoritmos de escalonamento.
- **Fila de Prontos (`fila_prontos`)**: Lista de tarefas que estão no estado PRONTO e aguardam execução.
- **Tarefa (`Task`)**: Entidade que representa um processo no sistema (do módulo `src.task`).
- **Quantum**: Período máximo de tempo que uma tarefa pode executar antes de ser preemptada (usado em algoritmos preemptivos).

---

## Classe Abstrata `Scheduler`

Classe base que define a interface comum para todos os escalonadores.

### Atributos

- `fila_prontos` (`List[Task]`): Lista de tarefas prontas para execução.
- `quantum` (`Optional[int]`): Quantum associado a escalonadores preemptivos (opcional).

### Métodos

#### `__init__(self, quantum: Optional[int] = None)`

Inicializa o escalonador com uma fila de prontos vazia e quantum opcional.

**Parâmetros:**
- `quantum` (`Optional[int]`): Quantum para algoritmos preemptivos (opcional).

**Retorna:**
- `None`

#### `adicionar_tarefa(self, tarefa: Task)`

Adiciona uma tarefa à fila de prontos.

**Parâmetros:**
- `tarefa` (`Task`): A tarefa a ser adicionada.

**Retorna:**
- `None`

#### `selecionar_proxima_tarefa(self) -> Optional[Task]`

Método Abstrato. Deve ser implementado pelas subclasses. Retorna a próxima tarefa que deve ser executada, baseada no algoritmo de escalonamento.

**Retorna:**
- `Optional[Task]`: A tarefa selecionada ou `None` se a fila estiver vazia ou nenhuma tarefa elegível for encontrada.

#### `remover_tarefa(self, tarefa: Task)`

Remove uma tarefa da fila de prontos (geralmente usada quando a tarefa é finalizada/terminada).

**Parâmetros:**
- `tarefa` (`Task`): A tarefa a ser removida.

**Retorna:**
- `None`

#### `__str__(self)`

Retorna uma representação textual do escalonador, incluindo o nome da classe e os IDs das tarefas na fila de prontos.

**Retorna:**
- `str`: Representação de debug.

---

## Classe `FIFOScheduler`

Implementa o algoritmo de escalonamento FIFO (First In, First Out), também conhecido como FCFS (First Come, First Served).

### Métodos

#### `selecionar_proxima_tarefa(self) -> Optional[Task]`

Implementa a lógica FIFO. Procura a primeira tarefa na `fila_prontos` que esteja no estado PRONTO ou EXECUTANDO e a retorna.

**Nota:** Como não há preempção no `FIFOScheduler` simples, a tarefa que já está em execução (estado EXECUTANDO) continua sendo retornada até ser finalizada.

**Retorna:**
- `Optional[Task]`: A primeira tarefa elegível na fila.

**Lógica:**
1. Itera sobre a `fila_prontos`.
2. Retorna a primeira tarefa encontrada com `tarefa.estado` igual a `TaskState.PRONTO` ou `TaskState.EXECUTANDO`.
3. Retorna `None` se nenhuma tarefa elegível for encontrada.

---

## Classe `SRTFScheduler`

Implementa o algoritmo de escalonamento SRTF (Shortest Remaining Time First), também conhecido como SRTF preemptivo.

### Métodos

#### `selecionar_proxima_tarefa(self) -> Optional[Task]`

Implementa a lógica SRTF. Seleciona a tarefa com menor tempo restante de execução dentre as tarefas disponíveis (PRONTO ou EXECUTANDO).

**Nota:** Este algoritmo é preemptivo - quando chega uma tarefa com menor tempo restante, ela pode preemptar a tarefa em execução.

**Retorna:**
- `Optional[Task]`: A tarefa com menor `tempo_restante` ou `None` se não houver tarefas disponíveis.

**Lógica:**
1. Filtra tarefas com estado `TaskState.PRONTO` ou `TaskState.EXECUTANDO`.
2. Seleciona a tarefa com menor valor de `tempo_restante` usando `min()`.
3. Retorna `None` se não houver tarefas disponíveis.

---

## Classe `PriorityPreemptiveScheduler`

Implementa o algoritmo de escalonamento por Prioridade Preemptivo.

### Métodos

#### `selecionar_proxima_tarefa(self) -> Optional[Task]`

Implementa a lógica de prioridade preemptiva. Seleciona a tarefa com maior prioridade (menor valor numérico de prioridade) dentre as tarefas disponíveis.

**Nota:** Menor valor de prioridade = maior prioridade. Por exemplo, uma tarefa com `prioridade=0` tem maior prioridade que uma com `prioridade=1`.

**Retorna:**
- `Optional[Task]`: A tarefa com menor valor de `prioridade` ou `None` se não houver tarefas disponíveis.

**Lógica:**
1. Filtra tarefas com estado `TaskState.PRONTO` ou `TaskState.EXECUTANDO`.
2. Seleciona a tarefa com menor valor de `prioridade` usando `min()`.
3. Retorna `None` se não houver tarefas disponíveis.

---

## Classe `SchedulerFactory`

Factory para criação de escalonadores suportados. Centraliza a criação de instâncias de escalonadores, garantindo consistência e facilitando a adição de novos algoritmos.

### Métodos

#### `criar_scheduler(cls, nome_algoritmo: str, quantum: Optional[int] = None) -> Scheduler`

Cria uma instância de escalonador com base no nome do algoritmo.

**Parâmetros:**
- `nome_algoritmo` (`str`): Nome do algoritmo desejado (case-insensitive). Valores válidos: `'FIFO'`, `'SRTF'`, `'PRIORIDADE'`.
- `quantum` (`Optional[int]`): Quantum associado a algoritmos preemptivos (opcional).

**Retorna:**
- `Scheduler`: Instância concreta de escalonador.

**Exceções:**
- `ValueError`: Se o nome do algoritmo não for suportado ou se estiver vazio.

**Exemplo de Uso:**
```python
from src.scheduler import SchedulerFactory

# Criar escalonador FIFO
scheduler_fifo = SchedulerFactory.criar_scheduler("FIFO")

# Criar escalonador SRTF com quantum
scheduler_srtf = SchedulerFactory.criar_scheduler("SRTF", quantum=2)

# Criar escalonador por Prioridade
scheduler_prio = SchedulerFactory.criar_scheduler("PRIORIDADE", quantum=1)
```

### Algoritmos Suportados

| Nome | Classe | Descrição | Preemptivo |
|------|--------|-----------|------------|
| `FIFO` | `FIFOScheduler` | First In, First Out | Não |
| `SRTF` | `SRTFScheduler` | Shortest Remaining Time First | Sim |
| `PRIORIDADE` | `PriorityPreemptiveScheduler` | Escalonamento por Prioridade | Sim |

### Como Adicionar Novos Algoritmos

Para adicionar um novo algoritmo de escalonamento:

1. Crie uma subclasse de `Scheduler` implementando `selecionar_proxima_tarefa()`.
2. Registre a classe no dicionário `_REGISTRO` da `SchedulerFactory`.
3. Atualize a documentação e a lista `ALGORITMOS_VALIDOS` no `ConfigParser`.

