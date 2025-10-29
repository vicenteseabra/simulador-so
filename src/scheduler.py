from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
from src.task import Task, TaskState


class Scheduler(ABC):
    """
    Classe base abstrata para todos os algoritmos de escalonamento.

    Cada escalonador deve manter uma lista de tarefas prontas
    (fila_prontos) e implementar a lógica de seleção de qual tarefa
    deve ser executada a seguir.
    """

    def __init__(self, quantum: Optional[int] = None):
        # Fila de tarefas prontas para execução
        self.fila_prontos: List[Task] = []
        # Quantum opcional associado a escalonadores preemptivos
        self.quantum: Optional[int] = quantum

    def adicionar_tarefa(self, tarefa: Task):
        """
        Adiciona uma tarefa à fila de prontos.
        """
        self.fila_prontos.append(tarefa)

    @abstractmethod
    def selecionar_proxima_tarefa(self) -> Optional[Task]:
        """
        Retorna a próxima tarefa que deve ser executada.
        Cada algoritmo define sua própria estratégia (FIFO, SRTF, etc).
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


class SRTFScheduler(Scheduler):
    """
    Shortest Remaining Time First (SRTF) - Preemptivo.
    
    Seleciona a tarefa com menor tempo restante de execução.
    Permite preempção quando chega uma tarefa com menor tempo restante.
    """

    def selecionar_proxima_tarefa(self) -> Optional[Task]:
        tarefas_disponiveis = [t for t in self.fila_prontos 
                               if t.estado in (TaskState.PRONTO, TaskState.EXECUTANDO)]
        
        if not tarefas_disponiveis:
            return None
        
        # Seleciona tarefa com menor tempo restante
        return min(tarefas_disponiveis, key=lambda t: t.tempo_restante)


class PriorityPreemptiveScheduler(Scheduler):
    """
    Escalonamento por Prioridade Preemptivo.
    
    Seleciona a tarefa com maior prioridade (menor valor numérico).
    Permite preempção quando chega uma tarefa com maior prioridade.
    """

    def selecionar_proxima_tarefa(self) -> Optional[Task]:
        tarefas_disponiveis = [t for t in self.fila_prontos 
                               if t.estado in (TaskState.PRONTO, TaskState.EXECUTANDO)]
        
        if not tarefas_disponiveis:
            return None
        
        # Seleciona tarefa com menor valor de prioridade (maior prioridade)
        return min(tarefas_disponiveis, key=lambda t: t.prioridade)


class SchedulerFactory:
    """Factory para criação de escalonadores suportados.

    A fábrica mantém um registro interno dos algoritmos disponíveis e garante
    que todos sejam instanciados de forma consistente. O parâmetro ``quantum``
    é encaminhado para o construtor do escalonador (quando aplicável),
    permitindo suportar algoritmos time-sliced como Round Robin.

    Para adicionar um novo algoritmo:

    1. Implemente uma subclasse de :class:`Scheduler` com a lógica de seleção
       em ``selecionar_proxima_tarefa``.
    2. Registre a classe no dicionário ``_REGISTRO`` usando uma chave única.
    """

    _REGISTRO: Dict[str, Type[Scheduler]] = {
        "FIFO": FIFOScheduler,
        "SRTF": SRTFScheduler,
        "PRIORIDADE": PriorityPreemptiveScheduler,
    }

    @classmethod
    def criar_scheduler(cls, nome_algoritmo: str, quantum: Optional[int] = None) -> Scheduler:
        """Cria uma instância de escalonador com base no nome do algoritmo.

        Args:
            nome_algoritmo: Nome do algoritmo desejado (case-insensitive).
            quantum: Quantum associado a algoritmos preemptivos (opcional).

        Returns:
            Instância concreta de :class:`Scheduler`.

        Raises:
            ValueError: Se o nome informado não estiver registrado.
        """

        if not nome_algoritmo:
            raise ValueError("Nome de algoritmo não pode ser vazio")

        chave = nome_algoritmo.strip().upper()
        scheduler_cls = cls._REGISTRO.get(chave)

        if scheduler_cls is None:
            algoritmos_suportados = ", ".join(sorted(cls._REGISTRO.keys()))
            raise ValueError(
                f"Algoritmo '{nome_algoritmo}' não suportado. "
                f"Válidos: {algoritmos_suportados}."
            )

        return scheduler_cls(quantum=quantum)

