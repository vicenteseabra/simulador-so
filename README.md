# Simulador de Sistema Operacional

Simulador de escalonamento de processos com suporte a múltiplos algoritmos e análise de métricas de desempenho.

## 👥 Equipe
- Vicente Seabra
- Giovanni Mioto

## 📋 Requisitos
- Python 3.8+

## 🚀 Como Usar

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



## � Algoritmos de Escalonamento

- ✅ **FIFO** (First In First Out)
- ✅ **SRTF** (Shortest Remaining Time First - Preemptivo)
- ✅ **Prioridade** (Preemptivo)

## 📊 Formato de Configuração

```
ALGORITMO;QUANTUM
ID;COR;INGRESSO;DURACAO;PRIORIDADE;EVENTOS
```

**Exemplo:**
```
FIFO;2
t01;#FF0000;0;5;1;
t02;#00FF00;2;3;1;
t03;#0000FF;4;4;1;E/S(2,1)
```

## 📈 Métricas Calculadas

- **Turnaround Time** - Tempo total no sistema
- **Waiting Time** - Tempo em espera
- **Response Time** - Tempo até primeira execução

## 🧪 Testes

```bash
# Verificação completa do sistema
python verificar_compatibilidade.py

# Testes de funcionalidade
python teste_completo.py
```

## 📚 Documentação

- [Task](docs/Task.md) - Estrutura de processos
- [Simulator](docs/Simulator.md) - Simulador principal
- [Scheduler](docs/Scheduler.md) - Algoritmos de escalonamento
- [ConfigParser](docs/config-parser.md) - Formato de arquivos
- [Clock](docs/Clock.md) - Gerenciamento de tempo

