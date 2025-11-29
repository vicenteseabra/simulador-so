# IOManager

**Arquivo**: `src/io_manager.py`

## Visão Geral

A classe `IOManager` gerencia operações de entrada/saída (I/O) para tarefas no simulador. Ela rastreia operações de I/O em andamento e determina quando elas são concluídas.

## Estrutura de Dados

```python
operacoes = [
    ('t01', 8),   # Tarefa t01 completa I/O no tempo 8
    ('t02', 10)   # Tarefa t02 completa I/O no tempo 10
]
```

## API Principal

### Iniciar I/O
```python
tempo_conclusao = io_manager.iniciar_io(task_id, duracao, tempo_atual)
# Calcula: tempo_atual + duracao
# Substitui operação anterior da mesma tarefa
```

### Verificar Conclusões
```python
conclusoes = io_manager.verificar_conclusoes(tempo_atual)
# Retorna: ['t01', 't02', ...] (operações concluídas)
# Remove automaticamente da lista
```

### Cancelar I/O
```python
cancelado = io_manager.cancelar_io(task_id)
# Retorna: True se cancelou, False se não havia I/O
```

### Utilitários
```python
ativas = io_manager.operacoes_ativas()     # Lista todas
tem_io = io_manager.tem_io_ativo(task_id)  # Verifica se tem I/O
tempo = io_manager.obter_tempo_conclusao(task_id)  # Tempo ou None
```

## Exemplo de Uso

```python
from io_manager import IOManager

io = IOManager()

# Iniciar I/O
tempo = io.iniciar_io('t01', duracao=3, tempo_atual=5)  # → 8

# Verificar conclusões
conclusoes = io.verificar_conclusoes(tempo_atual=8)    # → ['t01']
```

## Características

- **Lista ordenada** por tempo de conclusão
- **Uma operação por tarefa** (substitui anterior)
- **Conclusões em lote** (múltiplas no mesmo tick)
- **Reset automático** ao verificar conclusões

## Integração com Simulador

```python
# A cada tick
conclusoes = self.io_manager.verificar_conclusoes(self.tempo_atual)
for task_id in conclusoes:
    self.scheduler.desbloquear_tarefa(task_id)
```
