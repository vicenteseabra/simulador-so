# ConfigParser - Documentação Essencial

## Formato do Arquivo

### Estrutura
```
ALGORITMO;QUANTUM
ID;COR;INGRESSO;DURACAO;PRIORIDADE;EVENTOS
```

### Linha 1: Configuração do Sistema
- **ALGORITMO**: `FIFO`, `SRTF`, `PRIORIDADE` (obrigatório)
- **QUANTUM**: inteiro positivo (opcional, padrão: 1)

### Linhas Seguintes: Tarefas
- **ID**: identificador único (obrigatório)
- **COR**: hexadecimal `#RRGGBB` ou qualquer string (obrigatório)
- **INGRESSO**: tempo de chegada, inteiro ≥ 0 (obrigatório)
- **DURACAO**: tempo de execução, inteiro > 0 (obrigatório)
- **PRIORIDADE**: inteiro (opcional, padrão: 0, menor = maior prioridade)
- **EVENTOS**: lista de eventos separados por `;` (opcional)

**Observação:** IDs podem ser numéricos (1, 2, 3) ou alfanuméricos (t01, t02, t03).

### Tipos de Eventos
- **IO:tempo-duracao**: Operação I/O (ex: `IO:2-1` = I/O no tempo 2 por 1 unidade)
- **ML:tempo**: Mutex Lock (ex: `ML:1` = trava mutex no tempo 1)
- **MU:tempo**: Mutex Unlock (ex: `MU:3` = libera mutex no tempo 3)

**Múltiplos eventos:** Separar por `;` (ex: `IO:2-1;ML:1;MU:3`)

## Exemplos

### FIFO Básico
```
FIFO;2
t01;#FF0000;0;5;1;
t02;#00FF00;2;3;1;
t03;#0000FF;4;4;1;
```

### SRTF com I/O
```
SRTF;1
t01;#FF0000;0;8;1;IO:2-1
t02;#00FF00;1;4;1;IO:3-2
t03;#0000FF;2;6;1;
```

### Prioridade com Mutex
```
PRIORIDADE;1
t01;#FF0000;0;5;0;ML:1;MU:3
t02;#00FF00;1;8;1;ML:2;MU:4
t03;#0000FF;2;6;2;
```

### Exemplo Completo (Múltiplos Eventos)
```
FIFO;2
t01;#FF0000;0;5;1;IO:2-1;ML:1;MU:4
t02;#00FF00;2;3;1;IO:1-2
t03;#0000FF;4;4;2;ML:1;IO:2-1;MU:3
```

## Uso Básico
```python
from config_parser import ConfigParser

# Parse do arquivo
parser = ConfigParser()
config, tasks = parser.parse_file('config.txt')

# Acessar configuração
algoritmo = config['algoritmo']
quantum = config['quantum']

# Acessar tarefas
for task in tasks:
    print(f"{task.id}: chegada={task.ingresso}, duracao={task.duracao}")
    
    # Acessar eventos da tarefa
    if task.eventos:
        for evento in task.eventos:
            print(f"  Evento {evento['tipo']}: tempo={evento['tempo']}")
```

## Métodos Principais

### `parse_file(filename)`
Faz parse do arquivo e retorna `(config_dict, task_list)`

**Retorna:**
- `config_dict`: `{'algoritmo': str, 'quantum': int}`
- `task_list`: Lista de objetos `Task` com atributo `eventos`

**Exceções:**
- `FileNotFoundError`: arquivo não encontrado
- `ValueError`: formato inválido

### `obter_avisos()`
Retorna lista de avisos não-críticos (ex: evento mal formatado)

**Retorna:**
- `list`: Lista de strings com avisos

### `obter_resumo()`
Retorna dicionário com estatísticas da configuração

**Retorna:**
```python
{
    'valido': bool,
    'algoritmo': str,
    'quantum': int,
    'total_tarefas': int,
    'duracao_total': int,
    'avisos': int
}
```

## Estrutura de Eventos

Cada evento é um dicionário com os seguintes campos:

### Evento I/O
```python
{
    'tipo': 'IO',
    'tempo': int,      # tempo relativo ao início da tarefa
    'duracao': int     # duração da operação I/O
}
```

### Evento Mutex Lock
```python
{
    'tipo': 'ML',
    'tempo': int       # tempo relativo ao início da tarefa
}
```

### Evento Mutex Unlock
```python
{
    'tipo': 'MU',
    'tempo': int       # tempo relativo ao início da tarefa
}
```

## Validações

✅ Algoritmo válido (`FIFO`, `SRTF`, `PRIORIDADE`)  
✅ Quantum positivo (se especificado)  
✅ IDs únicos  
✅ Duração > 0  
✅ Ingresso ≥ 0  
✅ Pelo menos uma tarefa  
✅ Eventos com tempos válidos (≥ 0)  

## Recursos

- **Comentários**: linhas começando com `#` são ignoradas
- **Linhas vazias**: ignoradas automaticamente
- **Encoding**: UTF-8 com suporte a BOM
- **Espaços**: removidos automaticamente
- **Eventos inválidos**: geram avisos mas não interrompem o parsing

## Tratamento de Erros
```python
from config_parser import ConfigParser

try:
    parser = ConfigParser()
    config, tasks = parser.parse_file('config.txt')
    
    # Verifica avisos (não-críticos)
    avisos = parser.obter_avisos()
    if avisos:
        print("⚠️  Avisos encontrados:")
        for aviso in avisos:
            print(f"  - {aviso}")
    
    # Processa tarefas
    print(f"✓ {len(tasks)} tarefas carregadas")
    
except FileNotFoundError:
    print("❌ Arquivo não encontrado")
except ValueError as e:
    print(f"❌ Erro de formato: {e}")
```

## Exemplo Completo de Uso
```python
from config_parser import ConfigParser

# Carrega configuração
parser = ConfigParser()
config, tasks = parser.parse_file('config.txt')

# Exibe resumo
resumo = parser.obter_resumo()
print(f"Algoritmo: {resumo['algoritmo']}")
print(f"Quantum: {resumo['quantum']}")
print(f"Tarefas: {resumo['total_tarefas']}")
print(f"Duração total: {resumo['duracao_total']}")

# Processa cada tarefa
for task in tasks:
    print(f"\nTarefa {task.id}:")
    print(f"  Chegada: {task.ingresso}")
    print(f"  Duração: {task.duracao}")
    print(f"  Prioridade: {task.prioridade}")
    
    # Processa eventos
    if task.eventos:
        print(f"  Eventos ({len(task.eventos)}):")
        for evento in task.eventos:
            if evento['tipo'] == 'IO':
                print(f"    - I/O no tempo {evento['tempo']} por {evento['duracao']}u")
            elif evento['tipo'] == 'ML':
                print(f"    - Mutex Lock no tempo {evento['tempo']}")
            elif evento['tipo'] == 'MU':
                print(f"    - Mutex Unlock no tempo {evento['tempo']}")

# Verifica avisos
avisos = parser.obter_avisos()
if avisos:
    print("\n⚠️  Avisos:")
    for aviso in avisos:
        print(f"  {aviso}")
```

## Mensagens de Erro Comuns

### Arquivo não encontrado
```
FileNotFoundError: Arquivo 'config.txt' não encontrado
```
**Solução:** Verifique o caminho do arquivo

### Algoritmo inválido
```
ValueError: Linha 1: Algoritmo 'RR' inválido. Use: FIFO, SRTF, PRIORIDADE
```
**Solução:** Use um dos algoritmos válidos

### Formato de tarefa inválido
```
ValueError: Linha 2: formato inválido. Esperado: ID;COR;INGRESSO;DURACAO;PRIORIDADE;EVENTOS
```
**Solução:** Verifique se todos os campos obrigatórios estão presentes

### IDs duplicados
```
ValueError: IDs de tarefas duplicados
```
**Solução:** Use IDs únicos para cada tarefa

### Evento mal formatado (aviso)
```
⚠️ Evento IO mal formatado: IO:2
```
**Solução:** Use formato correto `IO:tempo-duracao`

---

**Nota Importante:** Tempos em eventos são sempre **relativos ao início da execução da tarefa**, não ao tempo global do sistema.

**Exemplo:** Se uma tarefa com `ingresso=5` tem evento `IO:2-1`, o I/O ocorrerá no tempo global 5+2=7 (após 2 unidades de execução da tarefa).