## Gantt - Documentação

### Visão Geral
O módulo define a classe `GanttChart`, responsável por armazenar e processar os dados de execução das tarefas. O objetivo desta estrutura é coletar os intervalos de execução (quando cada tarefa executou e por quanto tempo) e preparar os dados para renderização posterior em um gráfico de Gantt visual.

---

### Classe `GanttChart`
Classe principal que armazena os intervalos de execução das tarefas.

#### Atributos
- **`intervalos`** (`List[Dict[str, Any]]`):  
    Estrutura de dados para armazenar execução. É uma lista de dicionários, onde cada dicionário representa um intervalo com os seguintes campos:  
    - `task_id`  
    - `inicio`  
    - `fim`  
    - `cor`  

---

#### Métodos

##### `__init__(self)`
Inicializa a classe `GanttChart` com uma lista de intervalos vazia.

- **Retorna:**  
    `None`

---

##### `adicionar_intervalo(self, task_id: str, inicio: int, fim: int, cor: str)`
Adiciona um novo intervalo de execução à lista `intervalos`.

- **Parâmetros:**  
    - `task_id` (`str`): O ID da tarefa que executou.  
    - `inicio` (`int`): O tempo de início do intervalo.  
    - `fim` (`int`): O tempo de fim do intervalo.  
    - `cor` (`str`): A cor associada à tarefa.  

- **Retorna:**  
    `None`

---

##### `get_dados(self) -> Dict[str, List[Dict[str, Any]]]`
Retorna a estrutura organizada dos dados. Este método processa a lista de intervalos e agrupa todos os intervalos por `task_id`, preparando os dados para a renderização.

- **Retorna:**  
    `Dict`: Um dicionário onde cada chave é um `task_id` e o valor é uma lista de seus respectivos intervalos (`inicio`, `fim`, `cor`).

---

##### `calcular_dimensoes(self) -> Dict[str, int]`
Calcula e retorna a largura/altura do gráfico com base nos dados armazenados.

- **Retorna:**  
    `Dict[str, int]`: Um dicionário contendo:  
    - `largura`: O tempo máximo de fim entre todos os intervalos (representando a duração total da simulação).  
    - `altura`: O número total de tarefas únicas que executaram (representando o número de linhas no gráfico).  

---

##### `exibir_terminal(self)`
Exibe uma representação ASCII do gráfico de Gantt diretamente no terminal. Este método é responsável por:

- Desenhar uma linha para cada tarefa.
- Usar o caractere `█` (Bloco Cheio) para representar o tempo de execução.
- Usar o caractere `░` (Bloco Leve) para representar o tempo de espera.
- Exibir um eixo de tempo numérico abaixo do gráfico para referência.

- **Parâmetros:**  
    Nenhum.

- **Retorna:**  
    `None` (imprime diretamente no console).

