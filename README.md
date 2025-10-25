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


## 📝 Status do Desenvolvimento

### ✅ Completado
- [x] **Task 1.1** - Estruturas de Dados (Task, TCB)
- [x] **Task 1.2** - Parser de Configuração
  - Parser completo com validações
  - 29 testes unitários (100% sucesso)
  - Documentação detalhada
  - Exemplos práticos

### 🚧 Em Desenvolvimento
- [x] Algoritmos de escalonamento
- [ ] Simulador principal
- [ ] Modos de execução
- [ ] Visualização gráfica (Diagramas de Gantt)

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

