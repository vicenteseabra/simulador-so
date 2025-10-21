## Simulator - Documentação

## Visão Geral
O módulo `simulator.py` implementa a classe principal do simulador de Sistema Operacional. Ele define a classe `Simulator`, que orquestra a simulação do sistema operacional, controlando o avanço do relógio, a chegada e execução das tarefas, a comunicação com o escalonador e o registro do histórico de execução.

## Conceitos
- **Simulador (`Simulator`)**: Classe que representa o simulador de Sistema Operacional.
- **Relógio (`Clock`)**: Gerencia o tempo da simulação.
- **Tarefa (`TCB`)**: Representa um processo ou tarefa no sistema.
- **Escalonador (`Scheduler`)**: Componente responsável por decidir a ordem de execução das tarefas.
- **Histórico de Execução**: Registro do que ocorreu em cada unidade de tempo (tick).

## Classe `Simulator`
Classe principal que gerencia a simulação do sistema operacional.

### Atributos
- `clock` (`Clock`): Instância do relógio da simulação.
- `scheduler` (`Scheduler`): Instância do escalonador utilizado para gerenciar a execução das tarefas.
- `tasks` (list): Lista de todas as tarefas (`TCBs`) carregadas no sistema.
- `historico_execucao` (list): Lista de tuplas `(tempo, id_tarefa)` registrando o que foi executado em cada tick.

### Métodos
#### `__init__(self, scheduler)`
Inicializa o simulador com um escalonador e o relógio zerado.  
**Parâmetros:**
- `scheduler` (`Scheduler`): A instância do escalonador a ser utilizada.  
**Retorna:**
- `None`

#### `carregar_tarefas(self, tasks)`
Recebe uma lista de `TCBs` e prepara as tarefas para a simulação, definindo o estado inicial como `NOVO`.  
**Parâmetros:**
- `tasks` (list of `TCB`): Lista das tarefas a serem carregadas.  
**Retorna:**
- `None`

#### `verificar_novas_tarefas(self)`
Verifica o tempo de ingresso das tarefas e admite (muda o estado para `PRONTO` e adiciona ao escalonador) as que chegam no tempo atual.  
**Retorna:**
- `None`

#### `executar_tick(self)`
Executa um ciclo completo da simulação (1 unidade de tempo):
1. Verifica novas tarefas.
2. Pede ao escalonador a próxima tarefa.
3. Executa a tarefa selecionada (ou registra CPU ociosa).
4. Atualiza estados e registra no histórico.
5. Avança o relógio.  
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
# Assumindo que TCB, Clock e FIFOScheduler (ou outro) estão definidos
# from src.task import TCB
# from src.scheduler import FIFOScheduler 

# Criação de tarefas (assumindo que TCBs têm atributos como ingresso, tempo_servico)
tarefa1 = TCB(id=1, nome="Tarefa 1", ingresso=0, tempo_servico=5) 
tarefa2 = TCB(id=2, nome="Tarefa 2", ingresso=2, tempo_servico=3)

# Inicialização do simulador
simulador = Simulator(FIFOScheduler())

# Carregamento e execução
simulador.carregar_tarefas([tarefa1, tarefa2])
historico = simulador.executar(log=True)
# historico conterá a lista de (tempo, id_tarefa_executada)
```
