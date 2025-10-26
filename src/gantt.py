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
        # Armazena o tempo de ingresso de cada tarefa na fila (PRONTO)
        self.tempo_ingresso_fila: Dict[str, int] = {}

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

    def registrar_ingresso_fila(self, task_id: str, tempo: int):
        """
        Registra quando uma tarefa entra na fila de prontos.
        
        Parâmetros:
            task_id (str): O ID da tarefa
            tempo (int): O tempo em que entrou na fila
        """
        if task_id not in self.tempo_ingresso_fila:
            self.tempo_ingresso_fila[task_id] = tempo

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

    def exibir_terminal(self):
        """
        Exibe uma representação ASCII do gráfico de Gantt no terminal.
        
        - '█' (Bloco Cheio) representa tempo de execução.
        - '░' (Bloco Leve) representa tempo de espera/ociosidade.
        """
        dados_por_tarefa = self.get_dados()
        dimensoes = self.calcular_dimensoes()
        tempo_total = dimensoes.get('largura', 0)

        if tempo_total == 0 or not dados_por_tarefa:
            print("Nenhum dado de execução para exibir.")
            print("--- Fim do Gráfico ---")
            return

        CHAR_EXEC = '█'
        CHAR_ESPERA = '░'

        # Encontra o comprimento do ID mais longo para alinhamento
        try:
            max_id_len = max(len(task_id) for task_id in dados_por_tarefa.keys())
        except ValueError:
            max_id_len = 0 # Caso não haja tarefas

        # 1. Exibir cada linha de tarefa (ordem inversa para coincidir com SVG)
        for task_id in sorted(dados_por_tarefa.keys(), reverse=True):
            intervalos_exec = dados_por_tarefa[task_id]
            
            # Começa com uma linha cheia de 'espera'
            linha_grafico = [CHAR_ESPERA] * tempo_total
            
            # Preenche os blocos de 'execução'
            for intervalo in intervalos_exec:
                inicio = intervalo['inicio']
                fim = intervalo['fim']
                # Preenche cada tick de tempo no intervalo
                for i in range(inicio, fim):
                    if i < tempo_total: # Garante que não ultrapasse o limite
                        linha_grafico[i] = CHAR_EXEC
            
            # Formata e imprime a linha
            label = f"  {task_id}:".ljust(max_id_len + 4) # Legenda
            grafico_str = "".join(linha_grafico)
            print(f"{label} [{grafico_str}]")

        # 2. Exibir eixo de tempo
        
        # Padding para alinhar com o início do gráfico '['
        padding_eixo = " " * (max_id_len + 6) 
        
        # Cria a string do eixo
        eixo_str = ['-'] * tempo_total
        
        # Adiciona os números (ticks) de 5 em 5
        for t in range(0, tempo_total, 5):
            tick_label = str(t)
            # Coloca o label no eixo, cuidando para não sobrepor
            for i, char in enumerate(tick_label):
                if (t + i) < tempo_total:
                    eixo_str[t + i] = char

        print(f"{padding_eixo}{''.join(eixo_str)}")
    
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
        M_TOPO, M_ESQ, M_DIR, M_BAIXO = 60, 50, 50, 80
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
        svg += self._barras_espera(dados, M_ESQ, M_TOPO, tempo_total, L_TICK, H_LINHA)
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
        return f'  <text x="{w/2}" y="30" text-anchor="middle" class="title">Diagrama de Gantt</text>\n'

    def _grid(self, m_esq: int, m_topo: int, tempo: int, n_tasks: int, l_tick: int, h_linha: int) -> str:
        """Grid de referência."""
        svg = '  <!-- Grid -->\n'
        
        # Verticais
        for t in range(tempo + 1):
            x = m_esq + (t * l_tick)
            y1, y2 = m_topo, m_topo + (n_tasks * h_linha)
            svg += f'  <line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" class="grid-line"/>\n'
        
        # Horizontais
        for i in range(n_tasks + 1):
            y = m_topo + (i * h_linha)
            x1, x2 = m_esq, m_esq + (tempo * l_tick)
            svg += f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="grid-line"/>\n'
        
        return svg

    def _eixo_tempo(self, m_esq: int, m_topo: int, tempo: int, n_tasks: int, l_tick: int, h_linha: int) -> str:
        """Eixo de tempo."""
        svg = '  <!-- Eixo Tempo -->\n'
        y_texto = m_topo + (n_tasks * h_linha) + 20
        
        for t in range(tempo + 1):
            x = m_esq + (t * l_tick)
            svg += f'  <text x="{x}" y="{y_texto}" text-anchor="middle" class="axis-label">{t}</text>\n'
        
        # Label
        x_label = m_esq + (tempo * l_tick / 2)
        y_label = y_texto + 25
        svg += f'  <text x="{x_label}" y="{y_label}" text-anchor="middle" class="axis-label" font-weight="bold">Tempo (ticks)</text>\n'
        
        return svg

    def _labels_tasks(self, dados: dict, m_esq: int, m_topo: int, h_linha: int) -> str:
        """Labels das tarefas."""
        svg = '  <!-- Labels Tarefas -->\n'
        
        num_tasks = len(dados)
        
        # Labels individuais das tarefas
        for idx, task_id in enumerate(sorted(dados.keys(), reverse=True)):
            y = m_topo + (idx * h_linha) + (h_linha / 2) + 5
            x = m_esq - 10
            svg += f'  <text x="{x}" y="{y}" text-anchor="end" class="task-label">{task_id}</text>\n'
        
        # Título do eixo vertical "Tarefas"
        x_titulo = m_esq - 30
        y_titulo = m_topo + (num_tasks * h_linha / 2)
        svg += f'  <text x="{x_titulo}" y="{y_titulo}" text-anchor="middle" class="axis-label" '
        svg += f'font-weight="bold" transform="rotate(-90 {x_titulo} {y_titulo})">Tarefas</text>\n'
        
        return svg

    def _barras_espera(self, dados: dict, m_esq: int, m_topo: int, tempo_total: int, l_tick: int, h_linha: int) -> str:
        """Barras vazias representando o período desde que a tarefa entra na fila."""
        svg = '  <!-- Barras Espera -->\n'
        PAD = 4
        
        for idx, task_id in enumerate(sorted(dados.keys(), reverse=True)):
            # Pega o tempo de ingresso na fila
            tempo_ingresso = self.tempo_ingresso_fila.get(task_id, 0)
            
            # Desenha barra vazia desde o ingresso até o fim total
            x = m_esq + (tempo_ingresso * l_tick)
            y = m_topo + (idx * h_linha) + PAD
            w = (tempo_total - tempo_ingresso) * l_tick
            h = h_linha - (2 * PAD)
            
            # Barra vazia com borda preta sólida
            svg += f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#333" stroke-width="1"/>\n'
        
        return svg

    def _barras(self, dados: dict, m_esq: int, m_topo: int, l_tick: int, h_linha: int) -> str:
        """Barras de execução."""
        svg = '  <!-- Barras Execução -->\n'
        PAD = 4
        
        for idx, task_id in enumerate(sorted(dados.keys(), reverse=True)):
            for intervalo in dados[task_id]:
                x = m_esq + (intervalo['inicio'] * l_tick)
                y = m_topo + (idx * h_linha) + PAD
                w = (intervalo['fim'] - intervalo['inicio']) * l_tick
                h = h_linha - (2 * PAD)
                cor = intervalo['cor']
                
                # Barra preenchida
                svg += f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{cor}" stroke="#333" stroke-width="1" opacity="0.8"/>\n'
        
        return svg

    def _legenda(self, dados: dict, m_esq: int, m_topo: int, n_tasks: int, h_linha: int) -> str:
        """Legenda."""
        svg = '  <!-- Legenda -->\n'
        y = m_topo + (n_tasks * h_linha) + 60
        x = m_esq
        
        svg += f'  <text x="{x}" y="{y}" class="legend-text" font-weight="bold">Legenda:</text>\n'
        
        x_off = x + 60
        for idx, task_id in enumerate(sorted(dados.keys())):
            cor = dados[task_id][0]['cor']
            x_item = x_off + (idx * 100)
            
            svg += f'  <rect x="{x_item}" y="{y-12}" width="15" height="15" fill="{cor}" stroke="#333" stroke-width="1"/>\n'
            svg += f'  <text x="{x_item+20}" y="{y}" class="legend-text">{task_id}</text>\n'
        
        return svg