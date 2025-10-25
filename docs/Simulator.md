# Simulator

## Visão Geral
Orquestra a simulação do SO: controla Clock, chegada/execução de tarefas, escalonador e histórico.

## Atributos
- `clock` (`Clock`): Relógio da simulação
- `scheduler` (`Scheduler`): Escalonador utilizado
- `tasks` (`List[Task]`): Tarefas carregadas
- `historico_execucao` (`List[Tuple]`): Lista `(tempo, task_id)`. CPU ociosa: `(tempo, None)`
- `gantt` (`GanttChart`): Diagrama de Gantt

## Métodos Principais

### `carregar_tarefas(tasks: List[Task])`
Carrega tarefas e define estado inicial como `NOVO`.

### `executar_tick()`
Executa 1 tick: verifica chegadas, seleciona próxima tarefa, executa/preempta, atualiza histórico.

### `tem_tarefas_pendentes() -> bool`
Retorna `True` se há tarefas não terminadas.

### `executar(tempo_max=None, log=False) -> List`
Executa simulação completa. Retorna histórico.

### `executar_passo_a_passo() -> List`
Modo interativo. Comandos:
- **Enter**: Próximo tick
- **q/quit**: Sair
- **info \<id\>**: Detalhes de tarefa
- **status**: Status geral
- **continue**: Executar até fim

## Exemplo
```python
from src.simulator import Simulator
from src.scheduler import FIFOScheduler
from src.task import Task

sim = Simulator(FIFOScheduler())
sim.carregar_tarefas([Task("T1", "#F00", 0, 5, 1)])
historico = sim.executar(log=True)
sim.gantt.exportar_svg('diagrama.svg')
```
