# Integração de Eventos no Simulator

## Visão Geral

O módulo `simulator.py` foi atualizado para integrar completamente o sistema de eventos, gerenciando operações de I/O e mutexes de forma estruturada através dos gerenciadores `IOManager` e `MutexManager`.

## Novos Atributos

### Gerenciadores de Recursos
- `self.mutex_manager`: Instância de `MutexManager` para gerenciar mutexes
- `self.io_manager`: Instância de `IOManager` para gerenciar operações de I/O
- `self.eventos_pendentes`: Dicionário que mapeia `task_id` para lista de eventos processados (para histórico/debug)

### Estruturas Legadas (Mantidas para Compatibilidade)
- `self._blocked`: Estrutura legada de bloqueio
- `self.mutexes`: Estrutura legada de mutexes (sincronizada com MutexManager)
- `self._mutex_queues`: Estrutura legada de filas de mutex (sincronizada com MutexManager)

## Novos Métodos

### verificar_io_conclusoes()
```python
def verificar_io_conclusoes(self):
    """
    Verifica operações de I/O concluídas e desbloqueia tarefas correspondentes.
    Usa o IOManager para obter lista de tarefas com I/O completo.
    """
```

**Funcionalidade:**
- Consulta o `IOManager` para obter tarefas com I/O concluído
- Desbloqueia as tarefas correspondentes
- Adiciona tarefas de volta à fila de prontos do scheduler
- Remove tarefas da estrutura de bloqueio legada

### processar_eventos_tarefa(tarefa, tempo_atual)
```python
def processar_eventos_tarefa(self, tarefa, tempo_atual):
    """
    Processa eventos da tarefa que devem ocorrer no tick atual.
    Verifica eventos com tempo relativo igual ao tempo de execução da tarefa.
    
    Args:
        tarefa: Tarefa em execução
        tempo_atual: Tempo atual do sistema
    """
```

**Funcionalidade:**
- Identifica eventos que devem disparar no tick atual
- Compara `tempo_execucao` da tarefa com `tempo_relativo` dos eventos
- Executa cada evento apropriado
- Registra eventos processados no histórico (`eventos_pendentes`)
- Remove eventos disparados da lista de eventos da tarefa
- Trata exceções para não quebrar a simulação

## Novo Fluxo de Execução

### executar_tick() - Fluxo Atualizado

O método `executar_tick()` foi completamente refatorado para seguir o novo fluxo integrado:

```python
def executar_tick(self):
    """
    Executa um ciclo de simulação (1 unidade de tempo) com novo fluxo integrado:
    1. Desbloqueia tarefas com I/O completo
    2. Verifica novas tarefas
    3. Processa eventos da tarefa em execução
    4. Aplica envelhecimento (se scheduler suportar)
    5. Seleciona e executa próxima tarefa
    6. Atualiza estados e histórico
    7. Avança o relógio
    """
```

#### Passo a Passo Detalhado

**PASSO 1: Desbloquear tarefas com I/O completo**
```python
self.verificar_io_conclusoes()
```
- Verifica operações de I/O concluídas no `IOManager`
- Desbloqueia tarefas que completaram I/O
- Adiciona tarefas de volta à fila de prontos

**PASSO 2: Verificar chegada de novas tarefas**
```python
self.verificar_novas_tarefas()
```
- Admite tarefas cujo tempo de ingresso chegou
- Adiciona tarefas ao scheduler

**PASSO 3: Processar eventos da tarefa em execução**
```python
if tarefa_executando and tarefa_executando.estado != TaskState.TERMINADO:
    self.processar_eventos_tarefa(tarefa_executando, tempo_atual)
```
- Processa eventos ANTES de selecionar a próxima tarefa
- Eventos podem bloquear a tarefa atual, afetando a seleção

**PASSO 4: Aplicar envelhecimento (se suportado)**
```python
if hasattr(self.scheduler, 'aplicar_envelhecimento'):
    self.scheduler.aplicar_envelhecimento()
```
- Aplica envelhecimento de prioridades (se o scheduler implementar)

**PASSO 5: Selecionar próxima tarefa**
```python
tarefa = self.scheduler.selecionar_proxima_tarefa()
```
- Lógica normal de escalonamento
- Preempta tarefa anterior se necessário

**PASSO 6: Executar tarefa selecionada**
```python
if tarefa:
    if tarefa.estado == TaskState.PRONTO:
        tarefa.iniciar()
    tarefa.executar(tempo_atual)
    self.historico_execucao.append((tempo_atual, tarefa.id))
    if tarefa.estado == TaskState.TERMINADO:
        self.scheduler.remover_tarefa(tarefa)
```
- Inicia tarefa se estava pronta
- Executa um tick da tarefa
- Registra no histórico
- Remove tarefa se terminou

**PASSO 7: Atualizar e avançar**
```python
self._update_blocked_tasks()
self.clock.tick()
```
- Atualiza estruturas legadas de bloqueio
- Avança o relógio

## API de Bloqueio e Mutex Atualizada

### bloquear_tarefa(task_id, duracao)
```python
def bloquear_tarefa(self, task_id: str, duracao: int):
    """
    Bloqueia a tarefa por `duracao` ticks (I/O).
    Usa IOManager para gerenciar a operação de I/O.
    """
```

**Mudanças:**
- Usa `IOManager.iniciar_io()` para registrar operação
- Remove tarefa da fila de prontos
- Mantém estrutura legada para compatibilidade

### solicitar_mutex(task_id, mutex_id)
```python
def solicitar_mutex(self, task_id: str, mutex_id: str) -> bool:
    """
    Solicita o mutex; retorna True se concedido, False se enfileirado.
    Usa MutexManager para gerenciar mutexes.
    """
```

**Mudanças:**
- Usa `MutexManager.solicitar_mutex()` para gerenciar mutex
- Bloqueia tarefa se mutex não foi concedido
- Sincroniza estruturas legadas (`self.mutexes`, `self._mutex_queues`)

### liberar_mutex(task_id, mutex_id)
```python
def liberar_mutex(self, task_id: str, mutex_id: str) -> bool:
    """
    Libera o mutex; se houver fila de espera, concede ao próximo e desbloqueia-o.
    Usa MutexManager para gerenciar mutexes.
    """
```

**Mudanças:**
- Usa `MutexManager.liberar_mutex()` para gerenciar mutex
- Desbloqueia próxima tarefa na fila automaticamente
- Adiciona tarefa desbloqueada de volta à fila de prontos
- Sincroniza estruturas legadas

## Integração com Eventos

### Eventos Suportados

O simulator agora suporta completamente os eventos definidos em `src/events.py`:

1. **IOEvent**: Bloqueia tarefa por duração especificada
   ```python
   IOEvent(tipo='IO', tempo_relativo=5, task_id='T1', duracao=3)
   ```

2. **MutexLockEvent**: Solicita um mutex
   ```python
   MutexLockEvent(tipo='LOCK', tempo_relativo=3, task_id='T1', mutex_id='mutex1')
   ```

3. **MutexUnlockEvent**: Libera um mutex
   ```python
   MutexUnlockEvent(tipo='UNLOCK', tempo_relativo=8, task_id='T1', mutex_id='mutex1')
   ```

### Processamento de Eventos

Os eventos são processados automaticamente quando:
- A tarefa está em execução
- `tempo_execucao` da tarefa atinge o `tempo_relativo` do evento
- O evento ainda não foi disparado

## Histórico de Eventos

O simulator mantém um histórico de eventos processados em `self.eventos_pendentes`:

```python
self.eventos_pendentes = {
    'T1': [
        {
            'tempo': 5,
            'tipo': 'IO',
            'resultado': {'action': 'bloquear_tarefa', ...}
        },
        {
            'tempo': 10,
            'tipo': 'LOCK',
            'resultado': {'granted': True, ...}
        }
    ]
}
```

Isso permite:
- Debug de eventos processados
- Análise de execução
- Integração com sistema de histórico/snapshot

## Compatibilidade

### Retrocompatibilidade

O código mantém compatibilidade com implementações existentes através de:

1. **Estruturas Legadas**: `_blocked`, `mutexes`, `_mutex_queues` são mantidas e sincronizadas
2. **Método _update_blocked_tasks()**: Mantido para compatibilidade com código legado
3. **Aliases**: `block_task()`, `request_mutex()`, `release_mutex()` mantidos

### Migração

Para migrar código existente:

1. **Sem mudanças necessárias**: O código existente continua funcionando
2. **Opcional**: Pode acessar os gerenciadores diretamente:
   ```python
   simulator.io_manager.operacoes_ativas()
   simulator.mutex_manager.obter_donos_mutex()
   ```

## Exemplo de Uso

```python
from src.simulator import Simulator
from src.scheduler import FIFOScheduler
from src.task import Task
from src.events import IOEvent, MutexLockEvent, MutexUnlockEvent

# Criar scheduler e simulator
scheduler = FIFOScheduler()
simulator = Simulator(scheduler)

# Criar tarefa com eventos
eventos = [
    IOEvent(tipo='IO', tempo_relativo=2, task_id='T1', duracao=3),
    MutexLockEvent(tipo='LOCK', tempo_relativo=6, task_id='T1', mutex_id='recurso1'),
    MutexUnlockEvent(tipo='UNLOCK', tempo_relativo=8, task_id='T1', mutex_id='recurso1')
]

task = Task('T1', 'azul', 0, 10, 1, eventos=eventos)
simulator.carregar_tarefas([task])

# Executar simulação
simulator.executar()

# Verificar histórico de eventos
print(simulator.eventos_pendentes)
```

## Testes

Para validar a integração:

```python
# Teste de I/O
simulator.bloquear_tarefa('T1', 5)
assert simulator.io_manager.tem_io_ativo('T1')

# Teste de Mutex
concedido = simulator.solicitar_mutex('T1', 'mutex1')
assert concedido == True

# Teste de eventos
# (eventos são processados automaticamente durante executar_tick())
```

## Conformidade com Especificação

✅ **Atributos Adicionados**
- ✅ `self.mutex_manager = MutexManager()`
- ✅ `self.io_manager = IOManager()`
- ✅ `self.eventos_pendentes = {}` (dict por task_id)

✅ **Método processar_eventos_tarefa(tarefa, tempo_atual)**
- ✅ Verifica eventos que devem ocorrer neste tick
- ✅ Executa evento apropriado
- ✅ Atualiza estado da tarefa

✅ **Método verificar_io_conclusoes()**
- ✅ Implementado e integrado no fluxo

✅ **Atualização de executar_tick()**
- ✅ Verifica conclusões de I/O
- ✅ Desbloqueia tarefas com I/O completo
- ✅ Processa eventos da tarefa em execução
- ✅ Aplica envelhecimento (se scheduler suportar)
- ✅ Executa lógica normal

✅ **Registro de eventos no histórico**
- ✅ Implementado via `eventos_pendentes`

✅ **Documentação do novo fluxo**
- ✅ Documentado neste arquivo

## Próximos Passos

Para integração completa com o sistema de histórico (History):
1. O `HistoryManager` já captura os gerenciadores (`mutex_manager`, `io_manager`)
2. O histórico de eventos (`eventos_pendentes`) é incluído nos snapshots
3. A restauração de snapshots restaura completamente o estado dos gerenciadores
