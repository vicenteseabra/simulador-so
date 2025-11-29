"""Sistema de Histórico (Snapshot) para o Simulador de SO.

Este módulo fornece funcionalidades para capturar, armazenar e restaurar
snapshots completos do estado do sistema operacional simulado.

Classes principais:
- SystemSnapshot: Representa um snapshot do sistema em um momento específico
- HistoryManager: Gerencia histórico de snapshots e navegação temporal

Funcionalidades:
- Captura profunda (deep copy) do estado completo do sistema
- Serialização/deserialização de snapshots
- Navegação temporal (avançar/retroceder)
- Limitação automática do tamanho do histórico
- Preservação da integridade dos dados através de deep copy

Uso típico:
    history = HistoryManager()
    history.salvar_snapshot(simulator)
    # ... execução de alguns ticks ...
    estado_anterior = history.retroceder()
    # ... ou ...
    history.avancar()  # volta para snapshot mais recente
"""

from __future__ import annotations

import copy
from typing import Dict, List, Optional, Any
from src.task import Task


class SystemSnapshot:
    """Representa um snapshot completo do estado do sistema em um momento específico.

    Captura o estado de todos os componentes principais do simulador:
    - Tempo atual do sistema
    - Estado de todas as tarefas
    - Estado do escalonador
    - Estado dos mutexes
    - Estado das operações de I/O

    Attributes:
        tempo (int): Tempo atual do sistema no momento do snapshot
        tasks_state (Dict): Estado serializado de todas as tarefas
        scheduler_state (Dict): Estado serializado do escalonador
        mutex_state (Dict): Estado serializado dos mutexes
        io_state (Dict): Estado serializado das operações de I/O
    """

    def __init__(self, tempo: int, tasks_state: Dict[str, Any],
                 scheduler_state: Dict[str, Any], mutex_state: Dict[str, Any],
                 io_state: Dict[str, Any]):
        """Inicializa um snapshot com todos os estados do sistema.

        Args:
            tempo: Tempo atual do sistema
            tasks_state: Estado de todas as tarefas
            scheduler_state: Estado do escalonador
            mutex_state: Estado dos mutexes
            io_state: Estado das operações de I/O
        """
        self.tempo = tempo
        self.tasks_state = tasks_state
        self.scheduler_state = scheduler_state
        self.mutex_state = mutex_state
        self.io_state = io_state

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o snapshot para um dicionário.

        Returns:
            Dicionário contendo todos os dados do snapshot
        """
        return {
            'tempo': self.tempo,
            'tasks_state': self.tasks_state,
            'scheduler_state': self.scheduler_state,
            'mutex_state': self.mutex_state,
            'io_state': self.io_state
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SystemSnapshot:
        """Restaura um snapshot a partir de um dicionário.

        Args:
            data: Dicionário contendo dados do snapshot

        Returns:
            Instância de SystemSnapshot restaurada
        """
        return cls(
            tempo=data['tempo'],
            tasks_state=data['tasks_state'],
            scheduler_state=data['scheduler_state'],
            mutex_state=data['mutex_state'],
            io_state=data['io_state']
        )

    def __repr__(self) -> str:
        """Representação textual do snapshot para debug."""
        return f"SystemSnapshot(tempo={self.tempo}, tasks={len(self.tasks_state)}, " \
               f"scheduler={type(self.scheduler_state).__name__})"


class HistoryManager:
    """Gerencia histórico de snapshots do sistema e navegação temporal.

    Mantém uma lista ordenada cronologicamente de snapshots do sistema,
    permitindo navegação para frente e para trás no tempo. Implementa
    limitação automática do tamanho do histórico para otimização de memória.

    Attributes:
        snapshots (List[SystemSnapshot]): Lista de snapshots ordenada cronologicamente
        indice_atual (int): Índice do snapshot atual na lista
        max_snapshots (int): Número máximo de snapshots a manter
    """

    def __init__(self, max_snapshots: int = 1000):
        """Inicializa o gerenciador de histórico.

        Args:
            max_snapshots: Número máximo de snapshots a manter (padrão: 1000)
        """
        self.snapshots: List[SystemSnapshot] = []
        self.indice_atual: int = -1  # -1 indica que não há snapshots
        self.max_snapshots: int = max_snapshots

    def salvar_snapshot(self, simulator) -> None:
        """Captura e salva um snapshot completo do estado atual do sistema.

        Utiliza deep copy para garantir que o snapshot não seja afetado por
        mudanças posteriores no sistema. Remove snapshots antigos se necessário
        para manter o limite de tamanho.

        Args:
            simulator: Instância do simulador para capturar o estado
        """
        # Captura estados com deep copy para evitar referências
        tempo = simulator.clock.get_tempo()

        # Estado das tarefas
        tasks_state = {}
        for task in simulator.tasks:
            tasks_state[task.id] = self._serialize_task(task)

        # Estado do escalonador
        scheduler_state = self._serialize_scheduler(simulator.scheduler)

        # Estado dos mutexes (se existir mutex manager)
        mutex_state = self._serialize_mutex_state(simulator)

        # Estado das operações de I/O (se existir IO manager)
        io_state = self._serialize_io_state(simulator)

        # Cria o snapshot
        snapshot = SystemSnapshot(
            tempo=tempo,
            tasks_state=copy.deepcopy(tasks_state),
            scheduler_state=copy.deepcopy(scheduler_state),
            mutex_state=copy.deepcopy(mutex_state),
            io_state=copy.deepcopy(io_state)
        )

        # Remove snapshots futuros se estivermos navegando no histórico
        if self.indice_atual < len(self.snapshots) - 1:
            self.snapshots = self.snapshots[:self.indice_atual + 1]

        # Adiciona o novo snapshot
        self.snapshots.append(snapshot)
        self.indice_atual = len(self.snapshots) - 1

        # Limita o tamanho do histórico
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)
            self.indice_atual -= 1

    def restaurar_snapshot(self, index: int) -> Optional[Dict[str, Any]]:
        """Restaura o estado do sistema a partir de um snapshot específico.

        Args:
            index: Índice do snapshot a restaurar

        Returns:
            Dicionário contendo o estado do sistema ou None se índice inválido
        """
        if not (0 <= index < len(self.snapshots)):
            return None

        snapshot = self.snapshots[index]
        self.indice_atual = index

        return snapshot.to_dict()

    def avancar(self) -> Optional[Dict[str, Any]]:
        """Avança para o próximo snapshot no histórico.

        Returns:
            Estado do próximo snapshot ou None se já estiver no último
        """
        if self.indice_atual < len(self.snapshots) - 1:
            return self.restaurar_snapshot(self.indice_atual + 1)
        return None

    def retroceder(self) -> Optional[Dict[str, Any]]:
        """Retrocede para o snapshot anterior no histórico.

        Returns:
            Estado do snapshot anterior ou None se já estiver no primeiro
        """
        if self.indice_atual > 0:
            return self.restaurar_snapshot(self.indice_atual - 1)
        return None

    def obter_snapshot_atual(self) -> Optional[SystemSnapshot]:
        """Obtém o snapshot atual.

        Returns:
            Snapshot atual ou None se não houver snapshots
        """
        if self.indice_atual >= 0:
            return self.snapshots[self.indice_atual]
        return None

    def obter_info_historico(self) -> Dict[str, Any]:
        """Obtém informações sobre o histórico para debug.

        Returns:
            Dicionário com informações do histórico
        """
        return {
            'total_snapshots': len(self.snapshots),
            'indice_atual': self.indice_atual,
            'max_snapshots': self.max_snapshots,
            'tempo_primeiro': self.snapshots[0].tempo if self.snapshots else None,
            'tempo_ultimo': self.snapshots[-1].tempo if self.snapshots else None,
            'tempo_atual': self.snapshots[self.indice_atual].tempo if self.indice_atual >= 0 else None
        }

    def limpar_historico(self) -> None:
        """Remove todos os snapshots do histórico."""
        self.snapshots.clear()
        self.indice_atual = -1

    def _serialize_task(self, task: Task) -> Dict[str, Any]:
        """Serializa uma tarefa para dicionário.

        Args:
            task: Tarefa a ser serializada

        Returns:
            Dicionário representando a tarefa
        """
        task_dict = {
            'id': task.id,
            'cor': task.cor,
            'ingresso': task.ingresso,
            'duracao': task.duracao,
            'prioridade': task.prioridade,
            'tempo_restante': task.tempo_restante,
            'estado': task.estado,
            'tempo_inicio': task.tempo_inicio,
            'tempo_fim': task.tempo_fim,
            'tempo_execucao': task.tempo_execucao,
            'numero_preempcoes': task.numero_preempcoes
        }

        # Serializa eventos se existirem
        if hasattr(task, 'eventos') and task.eventos:
            task_dict['eventos'] = []
            for evento in task.eventos:
                if hasattr(evento, '__dict__'):
                    task_dict['eventos'].append(copy.deepcopy(evento.__dict__))
                else:
                    task_dict['eventos'].append(str(evento))

        return task_dict

    def _serialize_scheduler(self, scheduler) -> Dict[str, Any]:
        """Serializa o escalonador para dicionário.

        Args:
            scheduler: Escalonador a ser serializado

        Returns:
            Dicionário representando o escalonador
        """
        scheduler_dict = {
            'tipo': scheduler.__class__.__name__,
            'quantum': getattr(scheduler, 'quantum', None),
            'fila_prontos': [task.id for task in scheduler.fila_prontos]
        }

        # Adiciona atributos específicos de algoritmos
        if hasattr(scheduler, 'alpha'):  # PrioridadeEnvScheduler
            scheduler_dict['alpha'] = scheduler.alpha

        if hasattr(scheduler, 'tempo_atual_quantum'):
            scheduler_dict['tempo_atual_quantum'] = scheduler.tempo_atual_quantum

        return scheduler_dict

    def _serialize_mutex_state(self, simulator) -> Dict[str, Any]:
        """Serializa o estado dos mutexes.

        Args:
            simulator: Simulador contendo estado dos mutexes

        Returns:
            Dicionário representando estado dos mutexes
        """
        mutex_state = {
            'mutexes': copy.deepcopy(getattr(simulator, 'mutexes', {})),
            'mutex_queues': copy.deepcopy(getattr(simulator, '_mutex_queues', {}))
        }

        return mutex_state

    def _serialize_io_state(self, simulator) -> Dict[str, Any]:
        """Serializa o estado das operações de I/O.

        Args:
            simulator: Simulador contendo estado de I/O

        Returns:
            Dicionário representando estado de I/O
        """
        io_state = {
            'blocked': copy.deepcopy(getattr(simulator, '_blocked', {}))
        }

        # Se existir um IO manager separado
        if hasattr(simulator, 'io_manager'):
            io_state['operacoes'] = copy.deepcopy(
                getattr(simulator.io_manager, 'operacoes', [])
            )

        return io_state

    def __len__(self) -> int:
        """Retorna o número de snapshots no histórico."""
        return len(self.snapshots)

    def __repr__(self) -> str:
        """Representação textual do gerenciador de histórico."""
        return f"HistoryManager(snapshots={len(self.snapshots)}, " \
               f"atual={self.indice_atual}, max={self.max_snapshots})"



