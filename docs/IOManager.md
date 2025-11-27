# IOManager

**Arquivo**: `src/io_manager.py`

## Visão Geral

A classe `IOManager` gerencia operações de entrada/saída (I/O) para tarefas no simulador. Ela rastreia operações de I/O em andamento e determina quando elas são concluídas.

## Estrutura de Dados

Cada operação de I/O é representada como uma tupla:

```python
(task_id, tempo_conclusao)
```

Exemplo: `('t01', 8)` - Tarefa t01 completa I/O no tempo 8

A lista de operações é mantida **ordenada por tempo de conclusão** para eficiência na verificação de conclusões.

## Protocolo de Uso

### 1. Iniciar I/O

```python
tempo_conclusao = io_manager.iniciar_io(task_id, duracao, tempo_atual)
```

- **Calcula tempo de conclusão**: `tempo_atual + duracao`
- **Registra a operação** na lista ordenada
- **Substitui operação anterior** da mesma tarefa (se existir)
- **Retorna**: tempo de conclusão calculado

### 2. Verificar Conclusões

```python
conclusoes = io_manager.verificar_conclusoes(tempo_atual)
```

- **Identifica operações concluídas**: `tempo_conclusao <= tempo_atual`
- **Remove operações** da lista automaticamente
- **Retorna**: lista de task_ids que completaram I/O
- **Ordem**: ordenada por tempo de conclusão, depois por inserção

### 3. Cancelar I/O

```python
cancelado = io_manager.cancelar_io(task_id)
```

- **Remove operação** da tarefa especificada
- **Retorna**: `True` se cancelou, `False` se não havia I/O ativo
- **Uso**: término forçado de tarefa ou preempção

### 4. Debug

```python
# Ver todas as operações ativas
ativas = io_manager.operacoes_ativas()
# Retorna: [('t01', 8), ('t02', 10), ...]

# Verificar se tarefa tem I/O ativo
tem_io = io_manager.tem_io_ativo(task_id)
# Retorna: True ou False

# Obter tempo de conclusão
tempo = io_manager.obter_tempo_conclusao(task_id)
# Retorna: tempo de conclusão ou None
```

## Exemplo Completo

```python
from io_manager import IOManager

# Criar gerenciador
io = IOManager()

# Tarefa t01 inicia I/O de 3 ticks no tempo 5
tempo_conclusao = io.iniciar_io('t01', duracao=3, tempo_atual=5)
# → 8 (5 + 3)

print(io)
# IOManager:
#   t01: conclusão no tempo 8

# No tempo 7, verificar conclusões (nenhuma ainda)
conclusoes = io.verificar_conclusoes(tempo_atual=7)
# → []

# No tempo 8, verificar conclusões
conclusoes = io.verificar_conclusoes(tempo_atual=8)
# → ['t01']

print(io)
# IOManager: nenhuma operação ativa
```

## Múltiplas Operações

```python
io = IOManager()

# Várias tarefas iniciam I/O
io.iniciar_io('t01', duracao=3, tempo_atual=5)  # conclusão: 8
io.iniciar_io('t02', duracao=5, tempo_atual=5)  # conclusão: 10
io.iniciar_io('t03', duracao=2, tempo_atual=5)  # conclusão: 7

print(io)
# IOManager:
#   t03: conclusão no tempo 7
#   t01: conclusão no tempo 8
#   t02: conclusão no tempo 10

# Verificar operações ativas
ativas = io.operacoes_ativas()
# → [('t03', 7), ('t01', 8), ('t02', 10)]

# No tempo 8, duas operações completam
conclusoes = io.verificar_conclusoes(tempo_atual=8)
# → ['t03', 't01']  (ambas <= 8)
```

## Comportamento Especial

### Substituição de Operação

Se uma tarefa inicia I/O enquanto já tem uma operação ativa, a operação anterior é **substituída**:

```python
io = IOManager()

# Primeira operação
io.iniciar_io('t01', duracao=3, tempo_atual=5)  # conclusão: 8

# Segunda operação da mesma tarefa (substitui)
io.iniciar_io('t01', duracao=5, tempo_atual=6)  # conclusão: 11

# Há apenas UMA operação para t01
ativas = io.operacoes_ativas()
# → [('t01', 11)]  (não há mais a operação que concluiria em 8)
```

### Mesmo Tempo de Conclusão

Múltiplas operações podem completar no mesmo tick:

```python
io = IOManager()

io.iniciar_io('t01', duracao=3, tempo_atual=5)  # conclusão: 8
io.iniciar_io('t02', duracao=3, tempo_atual=5)  # conclusão: 8
io.iniciar_io('t03', duracao=3, tempo_atual=5)  # conclusão: 8

# No tempo 8, todas completam juntas
conclusoes = io.verificar_conclusoes(tempo_atual=8)
# → ['t01', 't02', 't03']
```

### Cancelamento

```python
io = IOManager()

io.iniciar_io('t01', duracao=3, tempo_atual=5)
io.iniciar_io('t02', duracao=5, tempo_atual=5)

# Cancelar I/O de t01
cancelado = io.cancelar_io('t01')  # → True

# Tentar cancelar novamente
cancelado = io.cancelar_io('t01')  # → False (não existe mais)

# Apenas t02 permanece
ativas = io.operacoes_ativas()
# → [('t02', 10)]
```

## Integração com o Simulador

O `IOManager` é projetado para ser usado pela classe `Simulator`:

### Quando um IOEvent é executado:

```python
# No simulator
def processar_evento_io(self, evento):
    # Registra operação de I/O
    tempo_conclusao = self.io_manager.iniciar_io(
        evento.task_id,
        evento.duracao,
        self.tempo_atual
    )
    
    # Bloqueia a tarefa
    self.scheduler.bloquear_tarefa(evento.task_id)
    
    self.log(f"Task {evento.task_id} iniciou I/O, conclusão no tempo {tempo_conclusao}")
```

### A cada tick do simulador:

```python
# No loop principal do simulator
def executar_tick(self):
    # ... lógica do tick ...
    
    # Verificar conclusões de I/O
    conclusoes = self.io_manager.verificar_conclusoes(self.tempo_atual)
    
    # Desbloquear tarefas que completaram I/O
    for task_id in conclusoes:
        self.scheduler.desbloquear_tarefa(task_id)
        self.log(f"Task {task_id} completou I/O no tempo {self.tempo_atual}")
    
    # ... continuar tick ...
```

### Quando uma tarefa é terminada:

```python
# No simulator
def terminar_tarefa(self, task_id):
    # Cancelar I/O se a tarefa for terminada forçadamente
    if self.io_manager.tem_io_ativo(task_id):
        self.io_manager.cancelar_io(task_id)
        self.log(f"I/O da task {task_id} cancelado")
    
    # ... resto da lógica de término ...
```

## API Completa

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `iniciar_io(task_id, duracao, tempo_atual)` | `int` | Inicia I/O, retorna tempo de conclusão |
| `verificar_conclusoes(tempo_atual)` | `List[str]` | Retorna e remove operações concluídas |
| `cancelar_io(task_id)` | `bool` | Cancela I/O, retorna se havia operação ativa |
| `operacoes_ativas()` | `List[Tuple[str, int]]` | Retorna todas as operações ativas |
| `tem_io_ativo(task_id)` | `bool` | Verifica se tarefa tem I/O ativo |
| `obter_tempo_conclusao(task_id)` | `Optional[int]` | Retorna tempo de conclusão ou None |
| `limpar()` | `None` | Remove todas as operações (para testes) |
| `__len__()` | `int` | Retorna número de operações ativas |

## Testes

Execute os testes com:

```bash
python tests/test_io_manager.py
```

Os testes cobrem:
- ✅ Uso básico (iniciar, verificar conclusões)
- ✅ Múltiplas operações simultâneas
- ✅ Operações completando no mesmo tempo
- ✅ Cancelamento de operações
- ✅ Substituição de operação da mesma tarefa
- ✅ Métodos auxiliares
- ✅ Cenário manual da especificação
- ✅ Verificação com tempo futuro

## Características Importantes

### ✅ Ordenação por Tempo de Conclusão

A lista de operações é mantida ordenada, permitindo verificação eficiente:

```python
# Lista sempre ordenada
operacoes = [('t03', 7), ('t01', 8), ('t02', 10)]
```

### ✅ Remoção Eficiente

Ao verificar conclusões, a lista é cortada de uma vez:

```python
# Remove todas as operações concluídas de uma vez
self.operacoes = self.operacoes[indice_corte:]
```

### ✅ Uma Operação por Tarefa

Uma tarefa pode ter apenas uma operação de I/O ativa. Se iniciar outra, a anterior é substituída automaticamente.

### ✅ Conclusões em Lote

Múltiplas operações que completam no mesmo tick são retornadas juntas:

```python
conclusoes = io.verificar_conclusoes(tempo_atual=8)
# Pode retornar várias: ['t01', 't02', 't03']
```

## Performance

| Operação | Complexidade | Observação |
|----------|--------------|------------|
| `iniciar_io()` | O(n) | Inserção ordenada |
| `verificar_conclusoes()` | O(k) | k = operações concluídas |
| `cancelar_io()` | O(n) | Busca linear |
| `tem_io_ativo()` | O(n) | Busca linear |
| `operacoes_ativas()` | O(n) | Copia lista |

### Otimizações Possíveis

Para cenários com muitas operações de I/O simultâneas:
- Usar heap (heapq) para inserção O(log n)
- Usar dicionário adicional para acesso O(1) por task_id

Implementação atual é simples e eficiente para casos típicos (< 100 operações simultâneas).

## Compatibilidade

- Python 3.7+ (usa `from __future__ import annotations`)
- Type hints completos
- Sem dependências externas

## Exemplo de Uso Avançado

```python
from io_manager import IOManager

io = IOManager()

# Simular múltiplos ticks
for tempo in range(1, 15):
    # Algumas tarefas iniciam I/O
    if tempo == 2:
        io.iniciar_io('t01', duracao=3, tempo_atual=tempo)  # conclusão: 5
        io.iniciar_io('t02', duracao=5, tempo_atual=tempo)  # conclusão: 7
    
    if tempo == 4:
        io.iniciar_io('t03', duracao=4, tempo_atual=tempo)  # conclusão: 8
    
    # Verificar conclusões a cada tick
    conclusoes = io.verificar_conclusoes(tempo_atual=tempo)
    
    if conclusoes:
        print(f"Tempo {tempo}: {conclusoes} completaram I/O")
    
    # Debug: mostrar operações ativas
    if len(io) > 0:
        print(f"  Operações ativas: {io.operacoes_ativas()}")

# Output esperado:
# Tempo 5: ['t01'] completaram I/O
#   Operações ativas: [('t02', 7), ('t03', 8)]
# Tempo 7: ['t02'] completaram I/O
#   Operações ativas: [('t03', 8)]
# Tempo 8: ['t03'] completaram I/O
```

## Referências

- [I/O Operations in OS](https://en.wikipedia.org/wiki/Input/output)
- [Blocking I/O](https://en.wikipedia.org/wiki/Asynchronous_I/O)
- [Process States](https://en.wikipedia.org/wiki/Process_state)

