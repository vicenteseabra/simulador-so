# ConfigParser - Documentação

## Visão Geral

O módulo `config_parser.py` implementa a classe `ConfigParser` responsável por ler e validar arquivos de configuração para o simulador de Sistema Operacional.

**Implementação Completamente Independente**: Não utiliza nenhuma biblioteca externa, apenas recursos básicos do Python.

## Formato do Arquivo de Configuração

### Estrutura Geral

```
ALGORITMO;QUANTUM
ID;COR;INGRESSO;DURACAO;PRIORIDADE;
ID;COR;INGRESSO;DURACAO;PRIORIDADE;
...
```

### Linha 1: Configuração do Sistema

```
ALGORITMO;QUANTUM
```

- **ALGORITMO** (obrigatório): Nome do algoritmo de escalonamento
  - Valores válidos: `FIFO`,`SRTF`, `PRIORIDADE`
  
- **QUANTUM** (opcional): Tamanho do quantum para algoritmos preemptivos
  - Valor padrão: `1`
  - Deve ser um inteiro positivo

### Linhas Seguintes: Definição de Tarefas

```
ID;COR;INGRESSO;DURACAO;PRIORIDADE;
```

- **ID** (obrigatório): Identificador único da tarefa
  - Tipo: String
  - Exemplo: `"1"`, `"P1"`, `"TaskA"`

- **COR** (obrigatório): Cor para visualização no diagrama de Gantt
  - Formato: Hexadecimal `#RRGGBB` ou `#RGB`
  - Exemplo: `"#FF0000"` (vermelho), `"#00FF00"` (verde)
  - Valor padrão se vazio: `"#808080"` (cinza)

- **INGRESSO** (obrigatório): Tempo de chegada da tarefa no sistema
  - Tipo: Inteiro não-negativo
  - Exemplo: `0`, `2`, `10`

- **DURACAO** (obrigatório): Tempo total de execução necessário
  - Tipo: Inteiro positivo (> 0)
  - Exemplo: `5`, `10`, `20`

- **PRIORIDADE** (opcional): Prioridade da tarefa
  - Tipo: Inteiro (menor valor = maior prioridade)
  - Valor padrão: `0`
  - Exemplo: `0`, `1`, `2`

**Nota**: O ponto-e-vírgula final é opcional mas recomendado.

## Exemplos de Arquivos

### Exemplo 1: FIFO Básico

```
FIFO;2
1;#FF0000;0;5;1;
2;#00FF00;2;3;1;
3;#0000FF;4;4;1;
```

### Exemplo 2: Round Robin com Várias Tarefas

```
RR;3
P1;#FF5733;0;10;0;
P2;#33FF57;2;5;0;
P3;#3357FF;4;8;0;
P4;#FF33A1;6;3;0;
```

### Exemplo 3: Prioridade com Diferentes Níveis

```
PRIORIDADE;1
Alta;#FF0000;0;5;0;
Media;#FFFF00;1;8;1;
Baixa;#00FF00;2;6;2;
```

### Exemplo 4: SRTF (Shortest Remaining Time First)

```
SRTF;1
1;#FF5733;0;8;1;
2;#33FF57;1;4;1;
3;#3357FF;2;2;1;
4;#FF33A1;3;6;1;
```

### Exemplo 5: Usando Valores Padrão

```
FIFO
TaskA;#FF0000;0;5;
TaskB;#00FF00;2;3;
TaskC;#0000FF;4;4;
```

Neste exemplo:
- Quantum será `1` (padrão)
- Todas as prioridades serão `0` (padrão)

## Classe ConfigParser

### Métodos Principais

#### `parse_file(filename)`

Faz o parsing de um arquivo de configuração.

**Parâmetros:**
- `filename` (str): Caminho do arquivo de configuração

**Retorna:**
- `tuple`: (config_dict, task_list)
  - `config_dict`: Dicionário com configurações do sistema
  - `task_list`: Lista de objetos Task

**Exceções:**
- `FileNotFoundError`: Se o arquivo não for encontrado
- `ValueError`: Se o formato do arquivo for inválido

**Exemplo:**
```python
from config_parser import ConfigParser

parser = ConfigParser()
config, tasks = parser.parse_file('config_fifo.txt')

print("Algoritmo:", config['algoritmo'])
print("Quantum:", config['quantum'])
print("Número de tarefas:", len(tasks))
```

#### `validar_configuracao()`

Valida a configuração completa parseada.

Verifica:
- Se há pelo menos uma tarefa
- Se não há IDs de tarefa duplicados
- Se há erros acumulados durante o parsing
- Validações específicas por algoritmo

**Exceções:**
- `ValueError`: Se a configuração for inválida

#### `obter_avisos()`

Retorna lista de avisos gerados durante o parsing.

**Retorna:**
- `list`: Lista de strings com avisos

**Exemplo:**
```python
parser = ConfigParser()
config, tasks = parser.parse_file('config.txt')

avisos = parser.obter_avisos()
for aviso in avisos:
    print("⚠️", aviso)
```

#### `obter_resumo()`

Retorna um resumo da configuração parseada.

**Retorna:**
- `dict`: Dicionário com informações resumidas
  - `valido`: Se a configuração é válida
  - `algoritmo`: Algoritmo de escalonamento
  - `quantum`: Quantum configurado
  - `total_tarefas`: Número de tarefas
  - `duracao_total`: Soma das durações
  - `tempo_chegada_minimo`: Menor tempo de ingresso
  - `tempo_chegada_maximo`: Maior tempo de ingresso
  - `distribuicao_prioridades`: Contagem por prioridade
  - `ids_tarefas`: Lista de IDs das tarefas
  - `avisos`: Número de avisos

**Exemplo:**
```python
parser = ConfigParser()
config, tasks = parser.parse_file('config.txt')

resumo = parser.obter_resumo()
print("Resumo da Configuração:")
for chave, valor in resumo.items():
    print(f"  {chave}: {valor}")
```

### Constantes da Classe

```python
ALGORITMOS_VALIDOS = ['FIFO', 'SJF', 'SRTF', 'PRIORIDADE', 'RR']
QUANTUM_PADRAO = 1
PRIORIDADE_PADRAO = 0
COR_PADRAO = '#808080'
```

## Função Utilitária

### `criar_arquivo_exemplo(filename, algoritmo, quantum, num_tarefas)`

Cria um arquivo de configuração de exemplo.

**Parâmetros:**
- `filename` (str): Nome do arquivo a ser criado
- `algoritmo` (str): Algoritmo de escalonamento (padrão: 'FIFO')
- `quantum` (int): Quantum (padrão: 2)
- `num_tarefas` (int): Número de tarefas (padrão: 3)

**Retorna:**
- `bool`: True se o arquivo foi criado com sucesso

**Exemplo:**
```python
from config_parser import criar_arquivo_exemplo

criar_arquivo_exemplo('meu_teste.txt', 'RR', 3, 5)
```

## Tratamento de Erros

### Erros Comuns e Como Corrigir

#### 1. Arquivo não encontrado
```
FileNotFoundError: Arquivo 'config.txt' não encontrado
```
**Solução**: Verifique se o caminho do arquivo está correto.

#### 2. Arquivo vazio
```
ValueError: Arquivo de configuração está vazio
```
**Solução**: Adicione pelo menos a linha de configuração do sistema.

#### 3. Algoritmo inválido
```
ValueError: Linha 1: Algoritmo 'FCFS' não é válido. Algoritmos válidos: FIFO, SJF, SRTF, PRIORIDADE, RR
```
**Solução**: Use um dos algoritmos válidos listados.

#### 4. Quantum inválido
```
ValueError: Linha 1: Quantum inválido 'abc': invalid literal for int()
```
**Solução**: Use um número inteiro positivo para o quantum.

#### 5. Duração inválida
```
ValueError: Linha 2: Erro ao criar tarefa: Duração deve ser maior que zero
```
**Solução**: Certifique-se de que a duração é um número positivo.

#### 6. ID duplicado
```
ValueError: ID de tarefa duplicado: '1' aparece múltiplas vezes
```
**Solução**: Use IDs únicos para cada tarefa.

#### 7. Formato de tarefa inválido
```
ValueError: Linha 3: Formato inválido para tarefa. Esperado: ID;COR;INGRESSO;DURACAO;PRIORIDADE;
```
**Solução**: Verifique se a linha tem todos os campos obrigatórios separados por ponto-e-vírgula.

## Recursos Especiais

### Comentários

Linhas que começam com `#` são ignoradas:

```
# Este é um comentário
FIFO;2
# Tarefas do sistema
1;#FF0000;0;5;1;
2;#00FF00;2;3;1;
```

### Linhas Vazias

Linhas vazias são automaticamente ignoradas.

### Encoding UTF-8

O parser suporta arquivos UTF-8 com ou sem BOM (Byte Order Mark).

### Tolerância a Espaços

Espaços em branco antes e depois dos valores são automaticamente removidos:

```
FIFO ; 2
1 ; #FF0000 ; 0 ; 5 ; 1 ;
```

## Validações Implementadas

### Durante o Parsing

1. ✅ Arquivo existe e pode ser lido
2. ✅ Arquivo não está vazio
3. ✅ Primeira linha contém algoritmo válido
4. ✅ Quantum é um número inteiro positivo (se especificado)
5. ✅ Cada tarefa tem campos obrigatórios
6. ✅ ID não está vazio
7. ✅ Ingresso não é negativo
8. ✅ Duração é positiva
9. ✅ Cor está em formato hexadecimal válido (aviso se inválido)

### Durante a Validação Final

10. ✅ Pelo menos uma tarefa válida foi parseada
11. ✅ Não há IDs duplicados
12. ✅ Round Robin tem quantum > 0
13. ✅ Nenhum erro foi acumulado durante o parsing

## Integração com o Simulador

O ConfigParser é projetado para ser usado como entrada para o simulador:

```python
from config_parser import ConfigParser
from simulator import Simulator

# Parse da configuração
parser = ConfigParser()
config, tasks = parser.parse_file('config.txt')

# Cria e executa o simulador
sim = Simulator(config['algoritmo'], config['quantum'], tasks)
sim.executar()
```

## Exemplos de Uso Completos

### Exemplo 1: Uso Básico

```python
from config_parser import ConfigParser

try:
    parser = ConfigParser()
    config, tasks = parser.parse_file('examples/config_fifo.txt')
    
    print(f"Algoritmo: {config['algoritmo']}")
    print(f"Quantum: {config['quantum']}")
    print(f"Tarefas: {len(tasks)}")
    
    for task in tasks:
        print(f"  {task.id}: chegada={task.ingresso}, duracao={task.duracao}")
        
except FileNotFoundError as e:
    print(f"Erro: {e}")
except ValueError as e:
    print(f"Erro de validação: {e}")
```

### Exemplo 2: Verificando Avisos

```python
from config_parser import ConfigParser

parser = ConfigParser()
config, tasks = parser.parse_file('config.txt')

# Verifica se há avisos
avisos = parser.obter_avisos()
if avisos:
    print("⚠️  Avisos encontrados:")
    for aviso in avisos:
        print(f"  - {aviso}")
```

### Exemplo 3: Análise Detalhada

```python
from config_parser import ConfigParser

parser = ConfigParser()
config, tasks = parser.parse_file('config.txt')

# Obtém resumo
resumo = parser.obter_resumo()

print("=" * 50)
print("RESUMO DA CONFIGURAÇÃO")
print("=" * 50)
print(f"Algoritmo: {resumo['algoritmo']}")
print(f"Quantum: {resumo['quantum']}")
print(f"Total de tarefas: {resumo['total_tarefas']}")
print(f"Duração total: {resumo['duracao_total']} unidades")
print(f"Chegadas: {resumo['tempo_chegada_minimo']} até {resumo['tempo_chegada_maximo']}")
print(f"\nDistribuição de prioridades:")
for prioridade, count in resumo['distribuicao_prioridades'].items():
    print(f"  Prioridade {prioridade}: {count} tarefas")
```

### Exemplo 4: Validação Robusta

```python
from config_parser import ConfigParser

def carregar_configuracao(arquivo):
    """Carrega configuração com tratamento robusto de erros."""
    try:
        parser = ConfigParser()
        config, tasks = parser.parse_file(arquivo)
        
        # Verifica avisos
        avisos = parser.obter_avisos()
        if avisos:
            print("Avisos:")
            for aviso in avisos:
                print(f"  ⚠️  {aviso}")
        
        # Mostra resumo
        resumo = parser.obter_resumo()
        print(f"\n✓ Configuração válida: {resumo['total_tarefas']} tarefas carregadas")
        
        return config, tasks
        
    except FileNotFoundError as e:
        print(f"❌ Erro: Arquivo não encontrado - {e}")
        return None, None
        
    except ValueError as e:
        print(f"❌ Erro de validação:")
        print(f"   {e}")
        return None, None
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None, None

# Uso
config, tasks = carregar_configuracao('config.txt')
if config and tasks:
    print("Pronto para simular!")
```

## Testes

Para executar os testes integrados:

```bash
cd src
python config_parser.py
```

Os testes cobrem:
- ✅ Parsing de arquivo de exemplo
- ✅ Criação de arquivo de exemplo
- ✅ Validação de erros
- ✅ Tratamento de arquivos inexistentes

## Boas Práticas

1. **Sempre use try-except** ao chamar `parse_file()`
2. **Verifique avisos** após o parsing
3. **Valide IDs únicos** em seus arquivos
4. **Use comentários** para documentar arquivos complexos
5. **Teste com arquivos pequenos** antes de criar grandes configurações
6. **Mantenha quantum apropriado** para Round Robin (geralmente 2-4)

## Referências

- Arquivos de exemplo: `examples/config_*.txt`
- Testes: `tests/test_scheduler.py`
- Documentação das estruturas: `docs/estruturas-dados.md`

---

*Este documento é parte da documentação do Simulador de SO. Para mais informações, consulte o README principal do projeto.*
