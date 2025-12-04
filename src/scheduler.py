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


class PrioridadeEnvScheduler(Scheduler):
    """Escalonamento por Prioridade com Envelhecimento (Aging)."""

    def __init__(self, quantum: int = 5, alpha: float = 1.0):
        super().__init__(quantum)
        self.alpha = alpha
        self.prioridades_dinamicas: Dict[str, float] = {}

    def adicionar_tarefa(self, tarefa: Task):
        super().adicionar_tarefa(tarefa)
        # Garante que a chave exista
        self.prioridades_dinamicas[tarefa.id] = float(tarefa.prioridade)

    def aplicar_envelhecimento(self):
        for tarefa in self.fila_prontos:
            if tarefa.estado == TaskState.PRONTO:
                # CORREÇÃO: Usa .get() para evitar KeyError se a tarefa veio de um snapshot
                prio_atual = self.prioridades_dinamicas.get(tarefa.id, float(tarefa.prioridade))
                self.prioridades_dinamicas[tarefa.id] = prio_atual - self.alpha

    def selecionar_proxima_tarefa(self) -> Optional[Task]:
        tarefas = [t for t in self.fila_prontos if t.estado in (TaskState.PRONTO, TaskState.EXECUTANDO)]
        if not tarefas: return None

        # CORREÇÃO: Usa .get() aqui também
        proxima = min(tarefas, key=lambda t: self.prioridades_dinamicas.get(t.id, float(t.prioridade)))
        
        # Reset da prioridade ao executar
        self.prioridades_dinamicas[proxima.id] = float(proxima.prioridade)
        return proxima

    def remover_tarefa(self, tarefa: Task):
        super().remover_tarefa(tarefa)
        self.prioridades_dinamicas.pop(tarefa.id, None)


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
        "PRIOPENV": PrioridadeEnvScheduler,
    }

    @classmethod
    def criar_scheduler(cls, nome_algoritmo: str, quantum: Optional[int] = None, alpha: Optional[float] = None) -> Scheduler:
        """Cria uma instância de escalonador com base no nome do algoritmo.

        Args:
            nome_algoritmo: Nome do algoritmo desejado (case-insensitive).
            quantum: Quantum associado a algoritmos preemptivos (opcional).
            alpha: Fator de envelhecimento para PRIOPEnv (opcional).

        Returns:
            Instância concreta de :class:`Scheduler`.

        Raises:
            ValueError: Se o nome informado não estiver registrado ou parâmetros obrigatórios estão ausentes.

        Examples:
            >>> scheduler = SchedulerFactory.criar_scheduler('FIFO')
            >>> scheduler = SchedulerFactory.criar_scheduler('SRTF', quantum=5)
            >>> scheduler = SchedulerFactory.criar_scheduler('PRIOPEnv', quantum=5, alpha=1)
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

        # Validação de parâmetros obrigatórios por algoritmo
        if chave == 'PRIOPENV':
            if quantum is None:
                raise ValueError("Algoritmo PRIOPEnv requer parâmetro 'quantum'")
            if alpha is None:
                alpha = 1.0  # Valor padrão
            return scheduler_cls(quantum, alpha)

        # Para outros algoritmos, apenas quantum é usado
        return scheduler_cls(quantum=quantum)

