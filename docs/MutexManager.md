# MutexManager

**Arquivo**: `src/mutex_manager.py`

## Visão Geral

Gerencia mutexes para sincronização entre tarefas. Suporta filas de espera FIFO e prevenção de starvation.

## Estrutura de Dados

```python
mutexes = {
    'mutex_01': {
        'dono': 't01',              # task_id do dono (None se livre)
        'fila_espera': ['t02', 't03']  # Lista FIFO de tasks aguardando
    }
}
```

## API Principal

### Solicitar Mutex
```python
granted = mutex_manager.solicitar_mutex(mutex_id, task_id)
# True:  mutex concedido imediatamente
# False: adicionado à fila de espera
```

### Liberar Mutex
```python
next_owner = mutex_manager.liberar_mutex(mutex_id, task_id)
# Valida posse, transfere para próximo na fila
# Retorna: task_id do próximo dono ou None
```

### Verificar Posse
```python
owns = mutex_manager.tarefa_possui_mutex(task_id, mutex_id)
# Retorna: True se possui, False caso contrário
```

### Utilitários
```python
donos = mutex_manager.obter_donos_mutex()        # {mutex_id: dono}
fila = mutex_manager.obter_fila_espera(mutex_id) # Lista de aguardando
```

## Exemplo de Uso

```python
from mutex_manager import MutexManager

mm = MutexManager()

# t01 solicita mutex
granted = mm.solicitar_mutex('01', 't01')  # → True

# t02 solicita mesmo mutex  
granted = mm.solicitar_mutex('01', 't02')  # → False (fila)

# t01 libera, t02 recebe automaticamente
next_owner = mm.liberar_mutex('01', 't01')  # → 't02'
```

## Características

- **FIFO**: Ordem justa na fila de espera
- **Reentrante**: Tarefa pode solicitar mutex que já possui
- **Transferência automática**: Próxima tarefa recebe ao liberar
- **Validação**: Erro ao tentar liberar mutex não possuído

## Integração com Simulador

```python
# MutexLockEvent
granted = self.mutex_manager.solicitar_mutex(evento.mutex_id, evento.task_id)
if not granted:
    self.scheduler.bloquear_tarefa(evento.task_id)

# MutexUnlockEvent  
next_owner = self.mutex_manager.liberar_mutex(evento.mutex_id, evento.task_id)
if next_owner:
    self.scheduler.desbloquear_tarefa(next_owner)
```
