# Estruturas de Dados - Simulador de SO

## Visão Geral

Este documento descreve as estruturas de dados fundamentais implementadas no simulador de sistema operacional, especificamente as classes `Task` e `TCB` (Task Control Block).

**Implementação Completamente Independente**: Todas as classes são implementadas usando apenas recursos básicos do Python, sem dependências de bibliotecas externas (incluindo `enum`, `typing`, `unittest`, etc.).

## Classes Implementadas

### TaskState

Classe utilitária para representar estados de processo, implementada como uma classe simples com constantes de string:

- `TaskState.NOVO`: Processo criado mas ainda não admitido no sistema
- `TaskState.PRONTO`: Processo pronto para execução, aguardando CPU
- `TaskState.EXECUTANDO`: Processo atualmente em execução
- `TaskState.BLOQUEADO`: Processo aguardando I/O ou outro evento
- `TaskState.TERMINADO`: Processo finalizado

#### Métodos Utilitários

```python
# Verificar se estado é válido
TaskState.is_valid_state(estado)

# Obter todos os estados possíveis
TaskState.get_all_states()
```

### Task

A classe `Task` representa uma tarefa/processo básico no sistema operacional simulado.

#### Atributos Principais

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `id` | `str` | Identificador único da tarefa |
| `cor` | `str` | Cor para visualização no diagrama de Gantt |
| `ingresso` | `int` | Tempo de chegada da tarefa no sistema |
| `duracao` | `int` | Tempo total de execução necessário |
| `prioridade` | `int` | Prioridade da tarefa (menor valor = maior prioridade) |
| `tempo_restante` | `int` | Tempo de execução ainda necessário |
| `tempo_espera` | `int` | Tempo total que a tarefa ficou esperando |
| `tempo_resposta` | `int ou None` | Tempo entre chegada e primeira execução |
| `estado` | `str` | Estado atual da tarefa (usando constantes TaskState) |

#### Estados Possíveis

Os estados são representados como strings constantes na classe `TaskState`:

- `NOVO`: Processo criado mas ainda não admitido no sistema
- `PRONTO`: Processo pronto para execução, aguardando CPU
- `EXECUTANDO`: Processo atualmente em execução
- `BLOQUEADO`: Processo aguardando I/O ou outro evento
- `TERMINADO`: Processo finalizado

#### Métodos Principais

```python
# Criação
task = Task("P1", "#FF0000", ingresso=0, duracao=5, prioridade=1)

# Controle de estado
task.admitir()                    # NOVO -> PRONTO
task.iniciar_execucao(tempo)      # PRONTO -> EXECUTANDO
task.pausar()                     # EXECUTANDO -> PRONTO
task.bloquear()                   # EXECUTANDO -> BLOQUEADO
task.desbloquear()               # BLOQUEADO -> PRONTO

# Execução
tempo_executado = task.executar(quantum)

# Métricas
metricas = task.calcular_metricas(tempo_finalizacao)
```

#### Métricas Calculadas

- **Turnaround Time**: Tempo total no sistema (finalização - chegada)
- **Waiting Time**: Tempo total de espera (turnaround - duração)
- **Response Time**: Tempo até primeira execução (primeira execução - chegada)
- **Normalized Turnaround**: Turnaround normalizado (turnaround / duração)

### TCB (Task Control Block)

A classe `TCB` estende `Task` com informações de controle detalhadas para análise avançada.

#### Atributos Adicionais

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `tempo_inicio_execucao` | `int ou None` | Tempo da primeira execução |
| `tempo_fim` | `int ou None` | Tempo de finalização |
| `historico_execucao` | `list` | Histórico detalhado de execução |
| `contexto` | `dict` | Informações de contexto adicional |
| `numero_preempcoes` | `int` | Contador de preempções |
| `tempo_total_cpu` | `int` | Tempo total de CPU utilizado |

#### Funcionalidades Avançadas

```python
# Criação
tcb = TCB("P2", "#00FF00", ingresso=2, duracao=8, prioridade=0)

# Contexto adicional
tcb.adicionar_contexto("cpu_burst", [3, 2, 3])
tcb.adicionar_contexto("io_operations", 2)

# Finalização com logging
tcb.finalizar(tempo_atual)

# Estatísticas detalhadas
stats = tcb.obter_estatisticas()

# Histórico resumido
resumo = tcb.obter_historico_resumido()
```

#### Eventos Registrados no Histórico

- `INICIO_EXECUCAO`: Início de uma execução
- `EXECUCAO`: Execução de quantum
- `PREEMPCAO`: Preempção da tarefa
- `FINALIZACAO`: Finalização da tarefa

## Exemplos de Uso

### Exemplo Básico - Task

```python
from task import Task, TaskState

# Criar tarefa
task = Task("P1", "#FF5733", ingresso=0, duracao=5, prioridade=1)

# Ciclo de vida básico
task.admitir()                    # NOVO -> PRONTO
task.iniciar_execucao(0)          # PRONTO -> EXECUTANDO
task.executar(2)                  # Executa 2 unidades
task.pausar()                     # EXECUTANDO -> PRONTO

# Continuar execução
task.iniciar_execucao(5)
task.executar(3)                  # Completa execução

# Calcular métricas
if task.estado == TaskState.TERMINADO:
    metricas = task.calcular_metricas(8)
    print(f"Turnaround: {metricas['turnaround_time']}")
    print(f"Waiting: {metricas['waiting_time']}")
```

### Exemplo Avançado - TCB

```python
from task import TCB

# Criar TCB
tcb = TCB("P2", "#33FF57", ingresso=2, duracao=8, prioridade=0)

# Adicionar contexto
tcb.adicionar_contexto("memory_requirement", "4MB")
tcb.adicionar_contexto("priority_class", "interactive")

# Simular execução complexa
tcb.admitir()
tcb.iniciar_execucao(2)
tcb.executar(3)                   # Primeira execução

tcb.pausar()                      # Preempção
tcb.iniciar_execucao(6)
tcb.executar(2)                   # Segunda execução

tcb.bloquear()                    # I/O
tcb.desbloquear()
tcb.iniciar_execucao(10)
tcb.executar(3)                   # Execução final

tcb.finalizar(13)

# Análise detalhada
stats = tcb.obter_estatisticas()
print(f"Preempções: {stats['numero_preempcoes']}")
print(f"Eficiência CPU: {stats['eficiencia_cpu']}")

# Histórico resumido
for evento in tcb.obter_historico_resumido():
    print(evento)
```

## Tratamento de Erros

### Validações na Criação

```python
# Erro: duração inválida
Task("P1", "#FF0000", 0, 0, 1)          # ValueError: Duração deve ser maior que zero

# Erro: tempo de ingresso negativo
Task("P1", "#FF0000", -1, 5, 1)         # ValueError: Tempo de ingresso não pode ser negativo
```

### Execução em Estado Inválido

```python
task = Task("P1", "#FF0000", 0, 5, 1)
task.executar()                          # RuntimeError: Tarefa P1 não está em execução
```

### Métricas de Tarefa Não Terminada

```python
task = Task("P1", "#FF0000", 0, 5, 1)
task.calcular_metricas(10)               # ValueError: Só é possível calcular métricas de tarefas terminadas
```

## Integração com o Simulador

As classes `Task` e `TCB` são projetadas para serem utilizadas pelos algoritmos de escalonamento:

1. **Criação**: Tarefas são criadas a partir de arquivos de configuração
2. **Escalonamento**: O escalonador gerencia estados e execução
3. **Análise**: TCBs fornecem dados detalhados para análise de desempenho
4. **Visualização**: Atributo `cor` usado no diagrama de Gantt

## Testes

Execute os testes unitários para validar as implementações:

```bash
python tests/test_scheduler.py
```

Os testes cobrem:
- Criação e validação de parâmetros
- Transições de estado
- Execução e preempção
- Cálculo de métricas
- Logging no TCB
- Casos de erro

**Implementação de Testes Customizada**: Os testes usam uma implementação própria de framework de testes, sem dependência de `unittest` ou outras bibliotecas.

## Padrões de Design

### Máquina de Estados
As transições de estado seguem o modelo clássico de estados de processo em sistemas operacionais.

### Herança
TCB herda de Task, estendendo funcionalidades sem quebrar compatibilidade.

### Encapsulamento
Métodos controlam transições válidas e mantêm invariantes.

### Observer/Logging
TCB registra eventos para análise posterior.

## Considerações de Performance

- Estados são strings simples para comparação eficiente
- Histórico é lista simples para append O(1)
- Contexto é dict para acesso O(1)
- Métricas são calculadas sob demanda
- **Sem overhead de bibliotecas externas**

## Arquitetura de Implementação

### Princípios de Design

1. **Independência Total**: Nenhuma dependência externa, nem mesmo de módulos padrão como `enum` ou `typing`
2. **Compatibilidade**: Funciona com qualquer versão do Python 2.7+
3. **Simplicidade**: Código claro e direto, fácil de entender e modificar
4. **Robustez**: Validações e tratamento de erros abrangentes

### Framework de Testes Customizado

Implementamos nossa própria infraestrutura de testes que inclui:
- Classe `TestCase` base com métodos de asserção
- Context manager para `assertRaises`
- Runner de testes com relatório detalhado
- Suporte a métodos `setUp()` para configuração inicial

```python
class TestCase:
    def assertEqual(self, a, b, msg=None)
    def assertIsNone(self, obj, msg=None)
    def assertIn(self, item, container, msg=None)
    def assertRaises(self, exception_class)
    def run_all_tests(self)
```

## Extensibilidade

As classes podem ser estendidas para:
- Novos tipos de eventos no histórico
- Métricas personalizadas
- Estados adicionais
- Informações de contexto específicas

---

*Este documento é parte da documentação do Simulador de SO. Para mais informações, consulte o README principal do projeto.*