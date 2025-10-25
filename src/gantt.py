"""
Módulo para a estrutura de dados do Gráfico de Gantt.

Este módulo define a classe GanttChart, que armazena e processa
os dados de execução das tarefas para posterior renderização
em um gráfico de Gantt.
"""

from typing import List, Dict, Any, Tuple, Optional


class GanttChart:
    """
    Armazena e organiza os dados de execução para um gráfico de Gantt.

    A classe mantém uma lista de intervalos de execução e fornece
    métodos para adicionar novos intervalos e recuperar os dados
    de forma organizada para a renderização.
    """

    def __init__(self):
        """
        Inicializa a estrutura de dados do gráfico de Gantt.

        'intervalos' armazena os dados brutos de execução.
        Formato da lista de intervalos:
        [
            {'task_id': str, 'inicio': int, 'fim': int, 'cor': str},
            ...
        ]
        """
        # Estrutura de dados para armazenar execução
        self.intervalos: List[Dict[str, Any]] = []

    def adicionar_intervalo(self, task_id: str, inicio: int, fim: int, cor: str):
        """
        Adiciona um novo intervalo de execução ao gráfico.

        Parâmetros:
            task_id (str): O ID da tarefa que executou.
            inicio (int): O tempo de início do intervalo.
            fim (int): O tempo de fim do intervalo.
            cor (str): A cor associada à tarefa.
        """
        if fim <= inicio:
            # Ignora intervalos inválidos ou de duração zero
            return

        novo_intervalo = {
            'task_id': task_id,
            'inicio': inicio,
            'fim': fim,
            'cor': cor
        }
        self.intervalos.append(novo_intervalo)

    def get_dados(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retorna a estrutura de dados organizada por tarefa.

        Isso prepara os dados para a renderização, agrupando
        todos os intervalos por 'task_id'.

        Retorna:
            Dict[str, List[Dict[str, Any]]]:
            Um dicionário onde cada chave é um 'task_id' e o valor
            é uma lista de seus intervalos de execução.
            Ex:
            {
                'T1': [
                    {'inicio': 0, 'fim': 2, 'cor': '#FF0000'},
                    {'inicio': 4, 'fim': 5, 'cor': '#FF0000'}
                ],
                'T2': [
                    {'inicio': 2, 'fim': 4, 'cor': '#00FF00'}
                ]
            }
        """
        dados_organizados: Dict[str, List[Dict[str, Any]]] = {}
        
        # Garante uma ordem de tarefas consistente (pelo ID)
        # Primeiro, coleta todas as tarefas únicas em ordem
        ids_tarefas_unicas = sorted(list(set(item['task_id'] for item in self.intervalos)))
        
        for task_id in ids_tarefas_unicas:
            dados_organizados[task_id] = []

        # Adiciona os intervalos a cada tarefa
        for intervalo in self.intervalos:
            task_id = intervalo['task_id']
            dados_organizados[task_id].append({
                'inicio': intervalo['inicio'],
                'fim': intervalo['fim'],
                'cor': intervalo['cor']
            })
            
        return dados_organizados

    def calcular_dimensoes(self) -> Dict[str, int]:
        """
        Calcula a largura e altura total do gráfico.

        - Largura: Baseada no tempo máximo de término de todas as tarefas.
        - Altura: Baseada no número de tarefas únicas que executaram.

        Retorna:
            Dict[str, int]: Um dicionário com 'largura' (tempo total)
                            e 'altura' (número de tarefas).
        """
        if not self.intervalos:
            return {'largura': 0, 'altura': 0}

        # Largura é o tempo máximo de fim
        largura_total = max(intervalo['fim'] for intervalo in self.intervalos)

        # Altura é o número de tarefas únicas
        altura_total = len(self.get_dados().keys())

        return {
            'largura': largura_total,
            'altura': altura_total
        }

    def exportar_svg(self, filename: str):
        """
        Exporta diagrama de Gantt como SVG.
        
        Args:
            filename (str): Nome do arquivo (extensão opcional)
        
        Returns:
            str: Caminho do arquivo salvo
        """
        if not filename.endswith('.svg'):
            filename += '.svg'
        
        filepath = f'output/{filename}'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self._gerar_svg())
        
        return filepath

    def _gerar_svg(self) -> str:
        """Gera conteúdo SVG completo."""
        if not self.intervalos:
            return self._svg_vazio()
        
        # Configurações
        H_LINHA = 40
        M_TOPO, M_ESQ, M_DIR, M_BAIXO = 60, 100, 50, 80
        L_TICK = 50
        
        dados = self.get_dados()
        dim = self.calcular_dimensoes()
        
        num_tasks = dim['altura']
        tempo_total = dim['largura']
        
        w = M_ESQ + (tempo_total * L_TICK) + M_DIR
        h = M_TOPO + (num_tasks * H_LINHA) + M_BAIXO
        
        # Monta SVG
        svg = f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">\n'
        svg += self._estilos()
        svg += f'  <rect width="{w}" height="{h}" fill="#FFF"/>\n'
        svg += self._titulo(w)
        svg += self._grid(M_ESQ, M_TOPO, tempo_total, num_tasks, L_TICK, H_LINHA)
        svg += self._eixo_tempo(M_ESQ, M_TOPO, tempo_total, num_tasks, L_TICK, H_LINHA)
        svg += self._labels_tasks(dados, M_ESQ, M_TOPO, H_LINHA)
        svg += self._barras(dados, M_ESQ, M_TOPO, L_TICK, H_LINHA)
        svg += self._legenda(dados, M_ESQ, M_TOPO, num_tasks, H_LINHA)
        svg += '</svg>'
        
        return svg

    def _svg_vazio(self) -> str:
        """SVG vazio."""
        return '''<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
    <rect width="400" height="200" fill="#F0F0F0"/>
    <text x="200" y="100" text-anchor="middle" font-family="Arial" font-size="16" fill="#666">Sem dados</text>
    </svg>'''

    def _estilos(self) -> str:
        """Estilos CSS."""
        return '''  <defs><style>
        .task-label { font-family: Arial; font-size: 14px; font-weight: bold; }
        .axis-label { font-family: Arial; font-size: 12px; fill: #333; }
        .grid-line { stroke: #E0E0E0; stroke-width: 1; }
        .title { font-family: Arial; font-size: 18px; font-weight: bold; fill: #333; }
        .legend-text { font-family: Arial; font-size: 11px; fill: #333; }
    </style></defs>
    '''

    def _titulo(self, w: int) -> str:
        """Título."""
        return f'  <text x="{w/2}" y="30" text-anchor="middle"  