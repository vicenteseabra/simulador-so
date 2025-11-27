# MutexManager

**Arquivo**: `src/mutex_manager.py`

## Visão Geral

A classe `MutexManager` gerencia travas de exclusão mútua (mutexes) para sincronização entre tarefas no simulador. Ela permite que tarefas solicitem e liberem mutexes, mantendo filas de espera para mutexes ocupados.

## Estrutura de Dados

O gerenciador mantém um dicionário de mutexes:

```python
mutexes = {
    mutex_id: {
        'dono': task_id,        # None se livre
        'fila_espera': [...]    # Lista de task_ids aguardando
    }
}
```

## Protocolo de Uso

### 1. Solicitar Mutex

```python
granted = mutex_manager.solicitar_mutex(mutex_id, task_id)
```

- **Se livre**: concede imediatamente → retorna `True`
- **Se ocupado**: adiciona à fila de espera → retorna `False`
- **Se já possui**: retorna `True` (requisição reentrante)

### 2. Liberar Mutex

```python
next_owner = mutex_manager.liberar_mutex(mutex_id, task_id)
```

- **Valida posse**: lança `ValueError` se a tarefa não for dona
- **Com fila**: transfere automaticamente para próxima tarefa (FIFO)
- **Sem fila**: mutex fica livre
- **Retorna**: `task_id` do próximo dono ou `None`

### 3. Verificar Posse

```python
owns = mutex_manager.tarefa_possui_mutex(task_id, mutex_id)
```

Retorna `True` se a tarefa possui o mutex, `False` caso contrário.

### 4. Debug

```python
# Obter todos os donos
owners = mutex_manager.obter_donos_mutex()
# Retorna: {'mutex_01': 't01', 'mutex_02': None, ...}

# Obter fila de espera
queue = mutex_manager.obter_fila_espera(mutex_id)
# Retorna: ['t02', 't03', ...]

# Obter estado completo
state = mutex_manager.obter_estado_completo()
# Retorna: {'mutex_01': {'dono': 't01', 'fila_espera': ['t02']}, ...}
```

## Exemplo Completo

```python
from mutex_manager import MutexManager

# Criar gerenciador
mm = MutexManager()

# Tarefa t01 solicita mutex 01
granted = mm.solicitar_mutex('01', 't01')
# → True (concedido)

# Tarefa t02 solicita mesmo mutex
granted = mm.solicitar_mutex('01', 't02')
# → False (bloqueado, entra na fila)

# Tarefa t03 também solicita
granted = mm.solicitar_mutex('01', 't03')
# → False (entra na fila após t02)

# Verificar estado
print(mm)
# MutexManager:
#   01: dono=t01, fila: ['t02', 't03']

# t01 libera o mutex
next_owner = mm.liberar_mutex('01', 't01')
# → 't02' (t02 recebe automaticamente)

# t02 agora é o dono
owns = mm.tarefa_possui_mutex('t02', '01')
# → True

# t02 libera
next_owner = mm.liberar_mutex('01', 't02')
# → 't03' (t03 recebe automaticamente)

# t03 libera (fila vazia)
next_owner = mm.liberar_mutex('01', 't03')
# → None (mutex fica livre)
```

## Tratamento de Erros

### Erro: Liberar mutex não possuído

```python
mm.solicitar_mutex('M1', 't01')  # t01 é dono

try:
    mm.liberar_mutex('M1', 't02')  # t02 tenta liberar
except ValueError as e:
    print(e)
    # Erro: task 't02' tentou liberar mutex 'M1',
    # mas o dono atual é 't01'
```

### Erro: Liberar mutex inexistente

```python
try:
    mm.liberar_mutex('M99', 't01')
except ValueError as e:
    print(e)
    # Erro: tentativa de liberar mutex 'M99' que não existe.
    # Task: t01
```

## Integração com o Simulador

O `MutexManager` é projetado para ser usado pela classe `Simulator`:

### Quando uma tarefa executa MutexLockEvent:

```python
# No simulator
granted = self.mutex_manager.solicitar_mutex(mutex_id, task_id)

if not granted:
    # Bloquear a tarefa até o mutex ser concedido
    self.bloquear_tarefa(task_id)
```

### Quando uma tarefa executa MutexUnlockEvent:

```python
# No simulator
next_owner = self.mutex_manager.liberar_mutex(mutex_id, task_id)

if next_owner:
    # Desbloquear a próxima tarefa que recebeu o mutex
    self.desbloquear_tarefa(next_owner)
```

## Características Importantes

### ✅ FIFO (First-In-First-Out)

Tarefas recebem mutexes na ordem em que solicitaram:

```python
mm.solicitar_mutex('M1', 't01')  # t01 é dono
mm.solicitar_mutex('M1', 't02')  # t02 na posição 1
mm.solicitar_mutex('M1', 't03')  # t03 na posição 2

mm.liberar_mutex('M1', 't01')    # t02 recebe (não t03)
```

### ✅ Múltiplos Mutexes Independentes

Uma tarefa pode possuir múltiplos mutexes diferentes:

```python
mm.solicitar_mutex('M1', 't01')  # True
mm.solicitar_mutex('M2', 't01')  # True
mm.solicitar_mutex('M3', 't01')  # True

# t01 agora possui M1, M2 e M3 simultaneamente
```

### ✅ Requisições Reentrantes

Uma tarefa pode solicitar um mutex que já possui:

```python
mm.solicitar_mutex('M1', 't01')  # True (adquire)
mm.solicitar_mutex('M1', 't01')  # True (já possui)
# Não entra na fila de espera
```

### ✅ Prevenção de Duplicatas

Uma tarefa não é adicionada múltiplas vezes à fila:

```python
mm.solicitar_mutex('M1', 't01')  # t01 é dono
mm.solicitar_mutex('M1', 't02')  # t02 entra na fila
mm.solicitar_mutex('M1', 't02')  # não adiciona duplicata
```

## API Completa

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `solicitar_mutex(mutex_id, task_id)` | `bool` | Solicita mutex. True se concedido, False se bloqueado |
| `liberar_mutex(mutex_id, task_id)` | `Optional[str]` | Libera mutex. Retorna próximo dono ou None |
| `tarefa_possui_mutex(task_id, mutex_id)` | `bool` | Verifica se tarefa possui mutex |
| `obter_donos_mutex()` | `Dict[str, Optional[str]]` | Retorna mapa mutex_id → dono |
| `obter_fila_espera(mutex_id)` | `List[str]` | Retorna fila de espera de um mutex |
| `obter_estado_completo()` | `Dict` | Retorna estado completo de todos mutexes |
| `limpar()` | `None` | Remove todos os mutexes (para testes) |

## Testes

Execute os testes com:

```bash
python tests/test_mutex_manager.py
```

Os testes cobrem:
- ✅ Uso básico (solicitar, liberar, verificar)
- ✅ Múltiplas tarefas aguardando
- ✅ Múltiplos mutexes independentes
- ✅ Erros de liberação inválida
- ✅ Requisições reentrantes
- ✅ Cenário manual da especificação

## Notas de Implementação

### Thread Safety

A implementação atual **não é thread-safe**. Se o simulador usar múltiplas threads, será necessário adicionar locks internos.

### Deadlock Prevention

O `MutexManager` **não previne deadlocks**. É responsabilidade do usuário garantir que tarefas não criem ciclos de dependência. Por exemplo:

```python
# PERIGO: Possível deadlock!
# t01 possui M1, quer M2
# t02 possui M2, quer M1
```

### Fairness

A política FIFO garante fairness: tarefas não sofrem starvation e recebem mutexes na ordem de solicitação.

### Performance

- **Solicitar mutex livre**: O(1)
- **Solicitar mutex ocupado**: O(1) (append na lista)
- **Liberar mutex**: O(1) (pop da lista)
- **Verificar posse**: O(1) (lookup em dicionário)

## Compatibilidade

- Python 3.7+ (usa `from __future__ import annotations`)
- Type hints completos
- Sem dependências externas

## Exemplo de Uso no Simulador

```python
class Simulator:
    def __init__(self):
        self.mutex_manager = MutexManager()
        # ... outros atributos
    
    def processar_evento_mutex_lock(self, evento):
        granted = self.mutex_manager.solicitar_mutex(
            evento.mutex_id, 
            evento.task_id
        )
        
        if not granted:
            # Bloquear tarefa
            self.bloquear_tarefa(evento.task_id)
            self.log(f"Task {evento.task_id} bloqueada aguardando mutex {evento.mutex_id}")
        else:
            self.log(f"Task {evento.task_id} adquiriu mutex {evento.mutex_id}")
    
    def processar_evento_mutex_unlock(self, evento):
        next_owner = self.mutex_manager.liberar_mutex(
            evento.mutex_id,
            evento.task_id
        )
        
        if next_owner:
            # Desbloquear próxima tarefa
            self.desbloquear_tarefa(next_owner)
            self.log(f"Mutex {evento.mutex_id} transferido para {next_owner}")
        else:
            self.log(f"Mutex {evento.mutex_id} agora está livre")
```

## Referências

- [Mutual Exclusion (Wikipedia)](https://en.wikipedia.org/wiki/Mutual_exclusion)
- [Semaphores and Mutexes](https://en.wikipedia.org/wiki/Semaphore_(programming))
- [Deadlock Prevention](https://en.wikipedia.org/wiki/Deadlock)

