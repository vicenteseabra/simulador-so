# Gantt - Documentação Completa

## Visão Geral
O módulo `gantt.py` define a classe `GanttChart`, responsável por armazenar e processar os dados de execução das tarefas e **exportar diagramas de Gantt em formato SVG**. O objetivo desta estrutura é coletar os intervalos de execução (quando cada tarefa executou e por quanto tempo), preparar os dados para renderização e gerar arquivos SVG visualizáveis em qualquer navegador.

---

## Classe `GanttChart`
Classe principal que armazena os intervalos de execução das tarefas.

### Atributos
- **`intervalos`** (`List[Dict[str, Any]]`):  
    Estrutura de dados para armazenar execução. É uma lista de dicionários, onde cada dicionário representa um intervalo com os seguintes campos:  
    - `task_id`  
    - `tempo_inicio`  
    - `tempo_fim`  
    - `cor`  

---

### Métodos

#### `__init__(self)`
Inicializa a classe `GanttChart` com uma lista de intervalos vazia.

- **Retorna:**  
    `None`

---

#### `adicionar_intervalo(self, task_id: str, inicio: int, fim: int, cor: str)`
Adiciona um novo intervalo de execução à lista `intervalos`.

- **Parâmetros:**  
    - `task_id` (`str`): O ID da tarefa que executou.  
    - `inicio` (`int`): O tempo de início do intervalo (ex: `tempo_inicio`).  
    - `fim` (`int`): O tempo de fim do intervalo (ex: `tempo_fim`).  
    - `cor` (`str`): A cor associada à tarefa.  

- **Retorna:**  
    `None`

---

#### `get_dados(self) -> Dict[str, List[Dict[str, Any]]]`
Retorna a estrutura organizada dos dados. Este método processa a lista de intervalos e agrupa todos os intervalos por `task_id`, preparando os dados para a renderização.

- **Retorna:**  
    `Dict`: Um dicionário onde cada chave é um `task_id` e o valor é uma lista de seus respectivos intervalos (`inicio`, `fim`, `cor`).

---

#### `calcular_dimensoes(self) -> Dict[str, int]`
Calcula e retorna a largura/altura do gráfico com base nos dados armazenados.

- **Retorna:**  
    `Dict[str, int]`: Um dicionário contendo:  
    - `largura`: O tempo máximo de fim entre todos os intervalos (representando a duração total da simulação).  
    - `altura`: O número total de tarefas únicas que executaram (representando o número de linhas no gráfico).  
