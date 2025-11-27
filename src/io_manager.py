"""Gerenciador de operações de E/S para o simulador.

Gerencia operações de I/O de tarefas, mantendo uma lista ordenada de operações
ativas com seus respectivos tempos de conclusão.

Funcionalidades principais:
- iniciar_io(): registra operação e retorna tempo de conclusão
- verificar_conclusoes(): retorna e remove operações concluídas
- cancelar_io(): cancela operação de uma tarefa
- operacoes_ativas(): lista todas as operações para debug

Estrutura de dados: lista de tuplas (task_id, tempo_conclusao) ordenada por tempo.

"""

from __future__ import annotations

from typing import List, Tuple, Optional


class IOManager:
    """Gerencia operações de entrada/saída para sincronização de tarefas.

    Esta classe mantém uma lista de operações de I/O em andamento, onde cada
    operação é representada por uma tupla (task_id, tempo_conclusao). A lista
    é mantida ordenada por tempo de conclusão para eficiência.

    Attributes:
        operacoes: Lista de tuplas (task_id, tempo_conclusao) representando
                   operações de I/O ativas, ordenada por tempo de conclusão.
    """

    def __init__(self):
        """Inicializa um IOManager vazio sem operações ativas."""
        self.operacoes: List[Tuple[str, int]] = []

    def iniciar_io(self, task_id: str, duracao: int, tempo_atual: int) -> int:
        """Inicia uma operação de I/O para uma tarefa.

        Calcula tempo de conclusão (tempo_atual + duracao) e insere na lista
        ordenada. Substitui operação anterior da mesma tarefa se existir.

        Args:
            task_id: Identificador da tarefa iniciando I/O.
            duracao: Número de ticks que a operação de I/O levará.
            tempo_atual: Tempo atual do simulador em ticks.

        Returns:
            Tempo de conclusão calculado (tempo_atual + duracao).
        """
        # Cancela operação anterior se existir
        self.cancelar_io(task_id)

        # Calcula tempo de conclusão
        tempo_conclusao = tempo_atual + duracao

        # Insere mantendo ordenação por tempo de conclusão
        nova_operacao = (task_id, tempo_conclusao)

        # Busca posição para inserção ordenada
        posicao = 0
        for i, (_, tempo) in enumerate(self.operacoes):
            if tempo > tempo_conclusao:
                posicao = i
                break
            posicao = i + 1

        self.operacoes.insert(posicao, nova_operacao)

        return tempo_conclusao

    def verificar_conclusoes(self, tempo_atual: int) -> List[str]:
        """Verifica e retorna operações de I/O concluídas.

        Identifica operações com tempo_conclusao <= tempo_atual, remove da
        lista e retorna os task_ids correspondentes.

        Args:
            tempo_atual: Tempo atual do simulador em ticks.

        Returns:
            Lista de task_ids com I/O concluído (vazia se nenhuma concluída).
        """
        concluidas = []

        # Identifica operações concluídas
        # Como a lista está ordenada, podemos parar no primeiro não concluído
        indice_corte = 0
        for i, (task_id, tempo_conclusao) in enumerate(self.operacoes):
            if tempo_conclusao <= tempo_atual:
                concluidas.append(task_id)
                indice_corte = i + 1
            else:
                break

        # Remove operações concluídas da lista
        if concluidas:
            self.operacoes = self.operacoes[indice_corte:]

        return concluidas

    def cancelar_io(self, task_id: str) -> bool:
        """Cancela operação de I/O em andamento.

        Remove a operação da tarefa especificada, se existir.

        Args:
            task_id: Identificador da tarefa cuja operação deve ser cancelada.

        Returns:
            True se cancelou, False se não havia operação ativa.
        """
        # Busca e remove a operação da tarefa
        for i, (tid, _) in enumerate(self.operacoes):
            if tid == task_id:
                self.operacoes.pop(i)
                return True

        return False

    def operacoes_ativas(self) -> List[Tuple[str, int]]:
        """Retorna lista de todas as operações de I/O ativas.

        Returns:
            Lista de tuplas (task_id, tempo_conclusao) ordenada por tempo.
        """
        return list(self.operacoes)

    def tem_io_ativo(self, task_id: str) -> bool:
        """Verifica se tarefa tem operação de I/O ativa.

        Args:
            task_id: Identificador da tarefa a verificar.

        Returns:
            True se tem I/O ativo, False caso contrário.
        """
        return any(tid == task_id for tid, _ in self.operacoes)

    def obter_tempo_conclusao(self, task_id: str) -> Optional[int]:
        """Obtém tempo de conclusão da operação de I/O de uma tarefa.

        Args:
            task_id: Identificador da tarefa.

        Returns:
            Tempo de conclusão se tem I/O ativo, None caso contrário.
        """
        for tid, tempo_conclusao in self.operacoes:
            if tid == task_id:
                return tempo_conclusao
        return None

    def limpar(self):
        """Limpa todas as operações de I/O (útil para testes/reset)."""
        self.operacoes.clear()

    def __len__(self) -> int:
        """Retorna o número de operações de I/O ativas."""
        return len(self.operacoes)

    def __repr__(self) -> str:
        """Representação string para debugging."""
        return f"IOManager(operacoes={len(self.operacoes)})"

    def __str__(self) -> str:
        """Representação string legível para humanos."""
        if not self.operacoes:
            return "IOManager: nenhuma operação ativa"

        lines = ["IOManager:"]
        for task_id, tempo_conclusao in self.operacoes:
            lines.append(f"  {task_id}: conclusão no tempo {tempo_conclusao}")

        return "\n".join(lines)

