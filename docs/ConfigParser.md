# ConfigParser

**Arquivo**: `src/config_parser.py`

## Visão Geral

Parser para arquivos de configuração do simulador. Suporta algoritmos de escalonamento, tarefas com eventos de I/O e mutex.

## Formato do Arquivo

### Linha 1: Configuração
```
ALGORITMO;QUANTUM              # Algoritmos padrão
PRIOPENV;QUANTUM;ALPHA         # Prioridade com envelhecimento
```

**Algoritmos suportados:**
- `FIFO`: First In, First Out
- `SRTF`: Shortest Remaining Time First
- `PRIORIDADE`: Priority Scheduling
- `PRIOPENV`: Priority with Aging

### Linhas seguintes: Tarefas
```
ID;COR;INGRESSO;DURACAO;PRIORIDADE;EVENTOS
```

## Eventos Suportados

| Formato | Descrição | Exemplo |
|---------|-----------|---------|
| `IO:tempo-duracao` | E/S no tempo relativo, duração especificada | `IO:2-1` |
| `MLid:tempo` | Lock mutex no tempo relativo | `ML01:1` |
| `MUid:tempo` | Unlock mutex no tempo relativo | `MU01:4` |

## Exemplos

### Básico (FIFO)
```
FIFO;2
t01;#FF0000;0;5;1;
t02;#00FF00;2;3;2;
```

### Com Eventos
```
PRIOPENV;2;1
t01;#FF0000;0;5;2;IO:2-1;ML01:1;MU01:4
t02;#00FF00;1;3;1;IO:1-2;ML02:2
```

## API

```python
from config_parser import ConfigParser

parser = ConfigParser()
config, tasks = parser.parse_file('arquivo.txt')

# Configuração
print(config['algoritmo'])  # 'PRIOPENV'
print(config['quantum'])    # 2
print(config['alpha'])      # 1.0 (só para PRIOPENV)

# Tarefas com eventos
for task in tasks:
    print(f"{task.id}: {len(task.eventos)} eventos")
    for evento in task.eventos:
        print(f"  {type(evento).__name__}")
```

## Validação

- **Eventos malformados**: Geram avisos, não impedem parsing
- **IDs duplicados**: Geram erro
- **Campos obrigatórios**: ID, cor, ingresso, duração

```python
avisos = parser.obter_avisos()
resumo = parser.obter_resumo()
```

- Eventos malformados geram avisos mas não impedem parsing
- `parser.obter_avisos()` retorna lista de problemas
- `parser.obter_resumo()` inclui alpha quando disponível

## Algoritmos Suportados

- `FIFO`: First In, First Out
- `SRTF`: Shortest Remaining Time First  
- `PRIORIDADE`: Priority Scheduling
- `PRIOPENV`: Priority with Aging
