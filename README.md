# Simulador de Sistema Operacional Multitarefa

Simulador de SO com escalonamento de tarefas e visualização gráfica.

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
- [ ] FIFO (First In First Out)
- [ ] SRTF (Shortest Remaining Time First)
- [ ] Prioridade Preemptivo

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

# Parse do arquivo de configuração
parser = ConfigParser()
config, tasks = parser.parse_file('examples/config_fifo.txt')

# Exibe informações
print(f"Algoritmo: {config['algoritmo']}")
print(f"Tarefas: {len(tasks)}")

# Obtém resumo
resumo = parser.obter_resumo()
print(resumo)
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

```powershell
# Testes das estruturas de dados
python tests/test_scheduler.py

# Testes do parser de configuração
python tests/test_config_parser.py

# Todos os testes
python tests/test_scheduler.py; python tests/test_config_parser.py
```

## 📚 Documentação

- **[Estruturas de Dados](docs/estruturas-dados.md)** - Classes Task e TCB
- **[Config Parser](docs/config-parser.md)** - Parser de arquivos de configuração

