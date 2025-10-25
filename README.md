# Simulador de Sistema Operacional

Simulador de escalonamento de processos com suporte a múltiplos algoritmos e análise de métricas de desempenho.

## 👥 Equipe
- Vicente Seabra
- Giovanni Mioto

## 📋 Requisitos
- Python 3.8+
- Nenhuma biblioteca externa necessária

## 🚀 Como Executar



## 📁 Estrutura do Projeto
```

```

## 🔧 Algoritmos Implementados
- [x] FIFO (First In First Out)
- [x] SRTF (Shortest Remaining Time First)
- [x] Prioridade Preemptivo

## 📊 Formato do Arquivo de Configuração

### Estrutura
```
ALGORITMO;QUANTUM
ID;COR;INGRESSO;DURACAO;PRIORIDADE;
ID;COR;INGRESSO;DURACAO;PRIORIDADE;
...
```

### Exemplo
```
FIFO;2
1;#FF0000;0;5;1;
2;#00FF00;2;3;1;
3;#0000FF;4;4;1;
```

**Para mais detalhes, consulte:** [`docs/config-parser.md`](docs/config-parser.md)

## 💻 Como Usar o Parser

```python
from src.config_parser import ConfigParser
from src.scheduler import SchedulerFactory
from src.simulator import Simulator

# Carregar configuração
parser = ConfigParser()
config, tasks = parser.parse_file('examples/config_fifo.txt')

# Criar e executar simulação
scheduler = SchedulerFactory.criar_scheduler(config['algoritmo'], quantum=config['quantum'])
sim = Simulator(scheduler)
sim.carregar_tarefas(tasks)
historico = sim.executar()

# Obter métricas
for task in tasks:
    print(task.calcular_metricas())
```

## 🐛 Modo Passo-a-Passo (Debugger)

Execute a simulação de forma interativa para debug e aprendizado:

```python
from src.simulator import Simulator
from src.scheduler import FIFOScheduler
from src.task import Task

# Configurar simulador
scheduler = FIFOScheduler()
simulator = Simulator(scheduler)
tasks = [Task("T1", "#FF0000", ingresso=0, duracao=3, prioridade=1)]
simulator.carregar_tarefas(tasks)

# Executar em modo passo-a-passo
historico = simulator.executar_passo_a_passo()
```

### Comandos Disponíveis
- **Enter**: Executa próximo tick
- **q/quit**: Sai da simulação
- **info \<id\>**: Detalhes de uma tarefa
- **status**: Status geral do sistema
- **continue**: Executa até o fim

### Exemplo Interativo
```bash
python examples/teste_interativo.py
```

**Para mais detalhes, consulte:** [`docs/passo-a-passo.md`](docs/passo-a-passo.md)

## 📊 Exportação de Diagramas de Gantt

Gere diagramas de Gantt em formato SVG para visualizar a execução:

```python
from src.gantt import GanttChart

# Criar diagrama
gantt = GanttChart()
gantt.adicionar_intervalo('T1', 0, 3, '#FF0000')
gantt.adicionar_intervalo('T2', 3, 6, '#00FF00')

# Exportar para SVG
filepath = gantt.exportar_svg('meu_diagrama.svg')
print(f"SVG salvo em: {filepath}")
```

### Recursos
- ✅ Geração SVG usando apenas strings
- ✅ Grid de referência
- ✅ Eixo de tempo
- ✅ Labels das tarefas
- ✅ Legenda com cores
- ✅ Suporte a preempção (intervalos não-consecutivos)

### Demonstração
```bash
python examples/demo_svg_export.py
```

Arquivos SVG são salvos em `output/` e podem ser abertos em qualquer navegador.


## 📝 Status do Desenvolvimento

### ✅ Completado
- [x] **Task 1.1** - Estruturas de Dados (Task, TCB)
- [x] **Task 1.2** - Parser de Configuração
  - Parser completo com validações
  - 29 testes unitários (100% sucesso)
  - Documentação detalhada
  - Exemplos práticos
- [x] **Task 2.4** - Modo Passo-a-Passo (Debugger)
  - Execução interativa tick por tick
  - Comandos para inspeção de estado
  - 14 testes unitários (100% sucesso)
  - Documentação completa em [`docs/passo-a-passo.md`](docs/passo-a-passo.md)
- [x] **Task 2.7** - Exportação para SVG
  - Geração de diagramas de Gantt em SVG
  - Apenas strings Python (sem bibliotecas externas)
  - 12 testes unitários (100% sucesso)
  - Grid, eixo de tempo, labels e legenda

### 🚧 Em Desenvolvimento
- [x] Algoritmos de escalonamento
- [x] Simulador principal
- [x] Visualização gráfica (Diagramas de Gantt)
- [ ] Modos de execução adicionais

## 🧪 Executar Testes

```bash
# Testes de funcionalidade
python teste_completo.py
```

## 📚 Documentação

- [Task](docs/Task.md) - Estrutura de processos
- [Simulator](docs/Simulator.md) - Simulador principal
- [Scheduler](docs/Scheduler.md) - Algoritmos de escalonamento
- [ConfigParser](docs/config-parser.md) - Formato de arquivos
- [Clock](docs/Clock.md) - Gerenciamento de tempo
- [Passo-a-Passo](docs/passo-a-passo.md) - Modo debugger interativo
- [Gantt](docs/gantt.md) - Diagramas de Gantt e exportação SVG

