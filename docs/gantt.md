# GanttChart

## Visão Geral
Classe para armazenar intervalos de execução e exportar diagramas de Gantt em formato SVG puro.

## Atributos
- `intervalos` (`List[Dict]`): Lista de intervalos com `task_id`, `inicio`, `fim`, `cor`

## Métodos Principais

### `adicionar_intervalo(task_id: str, inicio: int, fim: int, cor: str)`
Adiciona intervalo de execução. Ignora intervalos inválidos (fim ≤ inicio).

### `get_dados() -> Dict[str, List[Dict]]`
Retorna dados organizados por tarefa:
```python
{
    'T1': [{'inicio': 0, 'fim': 2, 'cor': '#FF0000'}],
    'T2': [{'inicio': 2, 'fim': 4, 'cor': '#00FF00'}]
}
```

### `calcular_dimensoes() -> Dict[str, int]`
Retorna dimensões do gráfico:
- `largura`: Tempo total (maior fim)
- `altura`: Número de tarefas únicas

### `exportar_svg(filename: str) -> str`
Exporta SVG para `output/`. Adiciona extensão `.svg` se necessário.
Retorna caminho do arquivo salvo.  
