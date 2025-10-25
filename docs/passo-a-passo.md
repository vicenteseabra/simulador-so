# Modo Passo-a-Passo (Debugger)

## Visão Geral

Executa a simulação tick por tick de forma interativa para debug e análise.

## Uso Básico
```python
from simulator import Simulator
from scheduler import FIFOScheduler

scheduler = FIFOScheduler()
simulator = Simulator(scheduler)
simulator.carregar_tarefas(tasks)

# Executa em modo passo-a-passo
historico = simulator.executar_passo_a_passo()
```

## Interface

Após cada tick:
```
[Tick 5] Executando: Task T1 | Prontos: [T2, T3] | Finalizados: []
> 
```

## Comandos

| Comando | Ação |
|---------|------|
| `Enter` | Próximo tick |
| `q` ou `quit` | Encerra simulação |
| `continue` | Executa até o fim sem pausas |
| `info <id>` | Detalhes de uma tarefa |
| `status` | Status geral do sistema |
| `Ctrl+C` | Interrompe e retorna histórico parcial |

## Exemplos de Comandos

### info \<id\>
```
> info T1

=== Tarefa T1 ===
Estado: EXECUTANDO
Prioridade: 1
Ingresso: 0
Duração: 3
Restante: 2
Executado: 1
Início: 0
```

### status
```
> status

=== Status do Sistema ===
Tempo: 5
Algoritmo: FIFOScheduler
Tarefas: 3
  Novas: 0
  Prontas: 2
  Executando: 1
  Bloqueadas: 0
  Terminadas: 0
```

## Retorno

Retorna histórico de execução como lista de tuplas `(tempo, task_id)`.
```python
historico = simulator.executar_passo_a_passo()
# [(0, 'T1'), (1, 'T1'), (2, 'T2'), ...]
```

**Nota**: Comandos são case-insensitive (exceto IDs de tarefas).