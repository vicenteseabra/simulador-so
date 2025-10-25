# Task - Documentação

## Visão Geral
O módulo `task.py` implementa a classe `Task` (também conhecida como TCB - Task Control Block) que representa um processo ou tarefa no simulador de Sistema Operacional. Cada tarefa possui atributos que definem seu comportamento, estado e métricas de execução.

## Conceitos
- **Task/TCB**: Estrutura que representa um processo no sistema operacional.
- **Estados da Tarefa**: Uma tarefa pode estar em diferentes estados durante sua execução (NOVO, PRONTO, EXECUTANDO, BLOQUEADO, TERMINADO).
- **Tempo Restante**: Quantidade de tempo de execução que ainda falta para a tarefa terminar.
- **Métricas**: Medidas de desempenho calculadas após a execução (turnaround time, waiting time, response time).

---

## Classe `TaskState`

Enumeração dos estados possíveis de uma tarefa no sistema.

### Estados
- `NOVO`: Tarefa criada mas ainda não admitida no sistema
- `PRONTO`: Tarefa pronta para execução, aguardando na fila
- `EXECUTANDO`: Tarefa em execução na CPU
- `BLOQUEADO`: Tarefa bloqueada aguardando I/O
- `TERMINADO`: Tarefa finalizada

---

## Classe `Task`

Representa uma tarefa/processo no simulador (Task Control Block).

### Atributos

- `id` (`str`): Identificador único da tarefa
- `cor` (`str`): Cor em formato hexadecimal para visualização no diagrama de Gantt
- `ingresso` (`int`): Tempo de chegada da tarefa no sistema
- `duracao` (`int`): Tempo total de execução necessário (burst time)
- `prioridade` (`int`): Prioridade da tarefa (menor valor = maior prioridade)
- `eventos` (`list`): Lista de eventos (E/S, etc.) que ocorrem durante a execução
- `tempo_restante` (`int`): Tempo de execução restante (inicialmente igual a `duracao`)
- `estado` (`str`): Estado atual da tarefa (valor de `TaskState`)
- `tempo_inicio` (`int`): Primeiro momento em que a tarefa começou a executar (None se ainda não executou)
- `tempo_fim` (`int`): Momento em que a tarefa finalizou (None se ainda não terminou)
- `tempo_execucao` (`int`): Tempo relativo de execução da tarefa (contador interno)

### Métodos

#### `__init__(self, task_id, cor, ingresso, duracao, prioridade=0, eventos=None)`

Inicializa uma nova tarefa.

**Parâmetros:**
- `task_id` (`str`): Identificador único
- `cor` (`str`): Cor em formato hexadecimal (#RRGGBB)
- `ingresso` (`int`): Tempo de chegada no sistema
- `duracao` (`int`): Tempo total de execução necessário
- `prioridade` (`int`, opcional): Prioridade da tarefa (padrão: 0)
- `eventos` (`list`, opcional): Lista de eventos (padrão: [])

**Retorna:**
- `None`

---

#### `executar(self, tempo_atual)`

Executa a tarefa por 1 tick (unidade de tempo).

**Comportamento:**
1. Verifica se a tarefa está em estado `EXECUTANDO`
2. Se for a primeira execução, registra `tempo_inicio`
3. Decrementa `tempo_restante` em 1
4. Incrementa `tempo_execucao` em 1
5. Se `tempo_restante` chegar a 0, muda estado para `TERMINADO` e registra `tempo_fim`

**Parâmetros:**
- `tempo_atual` (`int`): Tempo atual do sistema

**Retorna:**
- `bool`: `True` se a tarefa terminou, `False` caso contrário

---

#### `admitir(self)`

Admite a tarefa no sistema, mudando seu estado de `NOVO` para `PRONTO`.

**Retorna:**
- `None`

---

#### `iniciar(self)`

Inicia a execução da tarefa, mudando seu estado de `PRONTO` para `EXECUTANDO`.

**Retorna:**
- `None`

---

#### `preemptar(self)`

Preempta a tarefa, mudando seu estado de `EXECUTANDO` para `PRONTO`.
Usado quando outra tarefa de maior prioridade ou menor tempo restante deve executar.

**Retorna:**
- `None`

---

#### `bloquear(self)`

Bloqueia a tarefa para operação de I/O, mudando seu estado de `EXECUTANDO` para `BLOQUEADO`.

**Retorna:**
- `None`

---

#### `desbloquear(self)`

Desbloqueia a tarefa após I/O, mudando seu estado de `BLOQUEADO` para `PRONTO`.

**Retorna:**
- `None`

---

#### `calcular_metricas(self)`

Calcula as métricas de desempenho da tarefa após sua finalização.

**Métricas Calculadas:**
- **Turnaround Time**: Tempo total desde a chegada até a finalização (`tempo_fim - ingresso`)
- **Waiting Time**: Tempo que a tarefa ficou esperando na fila (`turnaround_time - duracao`)
- **Response Time**: Tempo desde a chegada até o primeiro momento de execução (`tempo_inicio - ingresso`)

**Retorna:**
- `dict`: Dicionário com as métricas, ou `None` se a tarefa não terminou

**Exemplo de retorno:**
```python
{
    'turnaround_time': 10,
    'waiting_time': 5,
    'response_time': 2
}
```

---

#### `__str__(self)`

Retorna uma representação textual da tarefa para debug.

**Retorna:**
- `str`: String no formato `"Task(id, estado=ESTADO, rest=tempo_restante)"`

---

## Transições de Estado

```
    NOVO
     ↓ admitir()
   PRONTO ←──────────┐
     ↓ iniciar()     │
 EXECUTANDO          │
     ↓               │
     ├→ preemptar() ─┘
     ├→ bloquear() → BLOQUEADO
     |                    ↓ desbloquear()
     |                    └─→ PRONTO
     └→ (tempo_restante=0) → TERMINADO
```

---

## Exemplo de Uso

```python
from src.task import Task, TaskState

# Criar uma tarefa
task = Task(
    task_id="t01",
    cor="#FF0000",
    ingresso=0,
    duracao=5,
    prioridade=1,
    eventos=[]
)

print(task.estado)  # NOVO

# Admitir no sistema
task.admitir()
print(task.estado)  # PRONTO

# Iniciar execução
task.iniciar()
print(task.estado)  # EXECUTANDO

# Executar por 3 ticks
for tempo in range(3):
    task.executar(tempo)
    print(f"Tempo {tempo}: restante={task.tempo_restante}")

# Preemptar
task.preemptar()
print(task.estado)  # PRONTO

# Voltar a executar
task.iniciar()
task.executar(3)
task.executar(4)
print(task.estado)  # TERMINADO

# Calcular métricas
metricas = task.calcular_metricas()
print(metricas)
# {'turnaround_time': 4, 'waiting_time': -1, 'response_time': 0}
```

---

## Notas Importantes

1. **Tempo Relativo vs Tempo Global**: O método `executar()` recebe `tempo_atual` que é o tempo global do sistema. Internamente, a tarefa mantém um `tempo_execucao` que é relativo (contador de quantos ticks ela executou).

2. **Eventos**: A lista de `eventos` é armazenada mas o processamento de eventos (como E/S) deve ser implementado pelo `Simulator`, não pela própria `Task`.

3. **Preempção**: A tarefa não se preempta sozinha. O `Simulator` ou `Scheduler` é responsável por chamar `preemptar()` quando necessário.

4. **Métricas**: As métricas só podem ser calculadas após a tarefa estar em estado `TERMINADO`.

5. **Inicialização**: Todas as tarefas começam no estado `NOVO` e precisam ser admitidas (`admitir()`) antes de poderem executar.
