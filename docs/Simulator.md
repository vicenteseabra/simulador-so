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

### Métodos
#### `__init__(self, scheduler)`
Inicializa o simulador com um escalonador e o relógio zerado.  
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
Executa um ciclo completo da simulação (1 unidade de tempo):
1. Verifica novas tarefas.
2. Identifica tarefa atualmente em execução (se houver).
3. Pede ao escalonador a próxima tarefa.
4. Se houver mudança de tarefa, realiza preempção (pausa a tarefa anterior).
5. Executa a tarefa selecionada por 1 unidade de tempo (ou registra CPU ociosa se não houver tarefa).
6. Se a tarefa iniciou agora, registra o tempo de início.
7. Se a tarefa terminou, registra o tempo de fim e a remove do escalonador.
8. Atualiza o histórico de execução.
9. Avança o relógio.  
**Retorna:**
- `None`

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
```python
# Importações necessárias
from src.simulator import Simulator
from src.task import Task
from src.scheduler import FIFOScheduler, SchedulerFactory

# Criação de tarefas
tarefa1 = Task(task_id="t01", cor="#FF0000", ingresso=0, duracao=5, prioridade=1)
tarefa2 = Task(task_id="t02", cor="#00FF00", ingresso=2, duracao=3, prioridade=1)

# Inicialização do simulador com um escalonador
# Opção 1: Criação direta
simulador = Simulator(FIFOScheduler())

# Opção 2: Usando a Factory
# scheduler = SchedulerFactory.criar_scheduler("FIFO", quantum=2)
# simulador = Simulator(scheduler)

# Carregamento e execução
simulador.carregar_tarefas([tarefa1, tarefa2])
historico = simulador.executar(log=True)
# historico conterá a lista de (tempo, id_tarefa_executada)
# Exemplo: [(0, 't01'), (1, 't01'), (2, 't01'), (3, 't02'), (4, 't02'), ...]
# Se CPU ociosa: [(tempo, None)]
```
