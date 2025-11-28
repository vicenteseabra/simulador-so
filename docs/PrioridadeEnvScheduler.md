# PrioridadeEnvScheduler

Escalonamento por Prioridade com Envelhecimento (Aging).

## Características

- **Prioridade Dinâmica**: Reduz a cada tick para evitar starvation
- **Fórmula**: `prioridade_dinamica -= alpha` (a cada tick)
- **Reset Automático**: Prioridade volta ao original ao selecionar para executar
- **Simples**: Apenas gerencia prioridades, simulador controla preempção/quantum

## Parâmetros

- `quantum`: Herdado da classe base (gerenciado pelo simulador)
- `alpha`: Fator de envelhecimento (redução por tick)

## Formato Config

```
PRIOPEnv;5;1
# algoritmo;quantum;alpha
```

## Exemplo de Uso

```python
from scheduler import PrioridadeEnvScheduler

scheduler = PrioridadeEnvScheduler(quantum=5, alpha=1)

# Tarefa prioridade 10 esperando:
# Tick 0: prioridade = 10
# Tick 1: prioridade = 9  (envelhecimento)
# Tick 2: prioridade = 8
# Tick 3: prioridade = 7
# ...
```

## Comportamento

### Envelhecimento
Tarefas prontas (não executando) têm prioridade reduzida a cada tick:
```python
scheduler.aplicar_envelhecimento()  # Chama a cada tick
```

### Seleção
1. Seleciona tarefa com **menor** prioridade dinâmica (maior prioridade real)
2. Reseta automaticamente a prioridade da tarefa selecionada

**Nota**: Preempção e controle de quantum são responsabilidade do simulador.

## Prevenção de Starvation

Tarefa de baixa prioridade eventualmente terá prioridade suficiente:

```
Tarefa prioridade 10, alpha=1:
Tick  0: prioridade = 10
Tick  5: prioridade = 5  (envelheceu 5 ticks)
Tick 10: prioridade = 0  (máxima prioridade)
```

## Integração

```python
# Factory cria automaticamente
from scheduler import SchedulerFactory

scheduler = SchedulerFactory.criar_scheduler("PRIOPENV", quantum=5)
```

## API

### Métodos Principais

```python
# Adiciona tarefa e inicializa prioridade dinâmica
scheduler.adicionar_tarefa(tarefa)

# Aplica envelhecimento (chamar a cada tick)
scheduler.aplicar_envelhecimento()

# Seleciona próxima tarefa (com reset automático)
proxima = scheduler.selecionar_proxima_tarefa()

# Remove tarefa e limpa prioridade
scheduler.remover_tarefa(tarefa)
```

### Atributos

- `alpha`: Fator de envelhecimento
- `prioridades_dinamicas`: Dict {task_id: prioridade_atual}

## Testes

```bash
python tests/test_prioridade_env.py
```

Todos os testes validam envelhecimento, seleção por prioridade e prevenção de starvation.

