# Modo Passo-a-Passo

## Visão Geral
Executa simulação tick por tick de forma interativa para debug e análise.

## Uso
```python
from src.simulator import Simulator
from src.scheduler import FIFOScheduler

sim = Simulator(FIFOScheduler())
sim.carregar_tarefas(tasks)
historico = sim.executar_passo_a_passo()
```

## Comandos

| Comando | Ação |
|---------|------|
| `Enter` | Próximo tick |
| `q` / `quit` | Encerra simulação |
| `continue` | Executa até o fim |
| `info <id>` | Detalhes de tarefa |
| `status` | Status geral |
| `Ctrl+C` | Interrompe (retorna histórico parcial) |

## Exemplo de Saída

```
[Tick 5] Executando: T1 | Prontos: [T2, T3] | Finalizados: []
> info T1
=== Tarefa T1 ===
Estado: EXECUTANDO
Restante: 2/3
Ingresso: 0
```

## Retorno
Lista de tuplas `(tempo, task_id)`. CPU ociosa: `(tempo, None)`.