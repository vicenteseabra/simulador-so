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