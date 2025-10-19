from abc import ABC, abstractmethod
from typing import List, Optional
from src.task import Task, TaskState


class Scheduler(ABC):
    """
    Classe base abstrata para todos os algoritmos de escalonamento.

    Cada escalonador deve manter uma lista de tarefas prontas
    (fila_prontos) e implementar a lógica de seleção de qual tarefa
    deve ser executada a seguir.
    """

    def __init__(self):
        # Fila de tarefas prontas para execução
        self.fila_prontos: List[Task] = []

    def adicionar_tarefa(self, tarefa: Task):
        """
        Adiciona uma tarefa à fila de prontos.
        """
        self.fila_prontos.append(tarefa)

    @abstractmethod
    def selecionar_proxima_tarefa(self) -> Optional[Task]:
        """
        Retorna a próxima tarefa que deve ser executada.
        Cada algoritmo define sua própria estratégia (FIFO, Round Robin, etc).
        """
        pass

    def remover_tarefa(self, tarefa: Task):
        """
        Remove uma tarefa da fila de prontos (quando finalizada).
        """
        if tarefa in self.fila_prontos:
            self.fila_prontos.remove(tarefa)

    def __str__(self):
        """
        Representação textual útil para debug.
        """
        nomes = [t.id for t in self.fila_prontos]
        return f"{self.__class__.__name__}(fila_prontos={nomes})"


class FIFOScheduler(Scheduler):
    """
    Implementação do algoritmo de escalonamento FIFO (First In, First Out).

    A tarefa que chega primeiro na fila é a primeira a ser executada.
    Nenhuma preempção é feita: a tarefa atual continua até terminar.
    """

    def selecionar_proxima_tarefa(self) -> Optional[Task]:
        # Retorna a primeira tarefa PRONTO ou EXECUTANDO
        for tarefa in self.fila_prontos:
            if tarefa.estado in (TaskState.PRONTO, TaskState.EXECUTANDO):
                return tarefa
        return None
