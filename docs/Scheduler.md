## Scheduler - Documentação

## Visão Geral

O módulo define a estrutura base para todos os algoritmos de escalonamento do sistema operacional. Ele introduz a classe abstrata `Scheduler`, que estabelece a interface para gerenciamento da fila de tarefas prontas e a seleção da próxima tarefa a ser executada. O módulo também inclui uma implementação concreta, o `FIFOScheduler`.

---

## Conceitos

- **Escalonador (`Scheduler`)**: Classe base abstrata para algoritmos de escalonamento.
- **Fila de Prontos (`fila_prontos`)**: Lista de tarefas que estão no estado PRONTO e aguardam execução.
- **Tarefa (`Task`)**: Entidade que representa um processo no sistema (assumidamente do módulo `src.task`).

---

## Classe Abstrata `Scheduler`

Classe base que define a interface comum para todos os escalonadores.

### Atributos

- `fila_prontos` (`List[Task]`): Lista de tarefas prontas para execução.

### Métodos

#### `__init__(self)`

Inicializa o escalonador com uma fila de prontos vazia.

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

