"""Sistema de Histórico (Snapshot) para o Simulador de SO."""

from __future__ import annotations

import copy
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.task import Task

class SystemSnapshot:
    """Representa um snapshot completo do estado do sistema."""

    def __init__(self, tempo: int, tasks_state: Dict[str, Any],
                 scheduler_state: Dict[str, Any], mutex_state: Dict[str, Any],
                 io_state: Dict[str, Any]):
        self.tempo = tempo
        self.tasks_state = tasks_state
        self.scheduler_state = scheduler_state
        self.mutex_state = mutex_state
        self.io_state = io_state

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tempo': self.tempo,
            'tasks_state': self.tasks_state,
            'scheduler_state': self.scheduler_state,
            'mutex_state': self.mutex_state,
            'io_state': self.io_state
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SystemSnapshot:
        return cls(
            tempo=data['tempo'],
            tasks_state=data['tasks_state'],
            scheduler_state=data['scheduler_state'],
            mutex_state=data['mutex_state'],
            io_state=data['io_state']
        )

    def __repr__(self) -> str:
        return f"SystemSnapshot(tempo={self.tempo}, tasks={len(self.tasks_state)})"


class HistoryManager:
    """Gerencia histórico de snapshots."""

    def __init__(self, max_snapshots: int = 1000):
        self.snapshots: List[SystemSnapshot] = []
        self.indice_atual: int = -1
        self.max_snapshots: int = max_snapshots

    def salvar_snapshot(self, simulator) -> None:
        """Captura e salva um snapshot completo."""
        tempo = simulator.clock.get_tempo()

        # Estado das tarefas
        tasks_state = {}
        for task in simulator.tasks:
            tasks_state[task.id] = self._serialize_task(task)

        # Estado do escalonador
        scheduler_state = self._serialize_scheduler(simulator.scheduler)

        # Estado dos mutexes
        mutex_state = self._serialize_mutex_state(simulator)

        # Estado das operações de I/O
        io_state = self._serialize_io_state(simulator)

        snapshot = SystemSnapshot(
            tempo=tempo,
            tasks_state=copy.deepcopy(tasks_state),
            scheduler_state=copy.deepcopy(scheduler_state),
            mutex_state=copy.deepcopy(mutex_state),
            io_state=copy.deepcopy(io_state)
        )

        if self.indice_atual < len(self.snapshots) - 1:
            self.snapshots = self.snapshots[:self.indice_atual + 1]

        self.snapshots.append(snapshot)
        self.indice_atual = len(self.snapshots) - 1

        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)
            self.indice_atual -= 1

    def restaurar_snapshot(self, index: int) -> Optional[Dict[str, Any]]:
        if not (0 <= index < len(self.snapshots)):
            return None
        self.indice_atual = index
        return self.snapshots[index].to_dict()

    def avancar(self) -> Optional[Dict[str, Any]]:
        if self.indice_atual < len(self.snapshots) - 1:
            return self.restaurar_snapshot(self.indice_atual + 1)
        return None

    def retroceder(self) -> Optional[Dict[str, Any]]:
        if self.indice_atual > 0:
            return self.restaurar_snapshot(self.indice_atual - 1)
        return None

    def limpar_historico(self) -> None:
        self.snapshots.clear()
        self.indice_atual = -1

    def _serialize_task(self, task: Task) -> Dict[str, Any]:
        """Serializa uma tarefa para dicionário."""
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

        if hasattr(task, 'eventos') and task.eventos is not None:
            task_dict['eventos'] = []
            for evento in task.eventos:
                # Usa deepcopy para garantir que nenhuma referência seja mantida
                task_dict['eventos'].append(copy.deepcopy(evento))
        else:
            task_dict['eventos'] = []

        return task_dict

    def _serialize_scheduler(self, scheduler) -> Dict[str, Any]:
        scheduler_dict = {
            'tipo': scheduler.__class__.__name__,
            'quantum': getattr(scheduler, 'quantum', None),
            'fila_prontos': [task.id for task in scheduler.fila_prontos]
        }
        
        if hasattr(scheduler, 'alpha'):
            scheduler_dict['alpha'] = scheduler.alpha
        if hasattr(scheduler, 'tempo_atual_quantum'):
            scheduler_dict['tempo_atual_quantum'] = scheduler.tempo_atual_quantum
            
        # Salva prioridades dinâmicas (Correção do Bug de Determinismo)
        if hasattr(scheduler, 'prioridades_dinamicas'):
            scheduler_dict['prioridades_dinamicas'] = copy.deepcopy(scheduler.prioridades_dinamicas)
            
        return scheduler_dict

    def _serialize_mutex_state(self, simulator) -> Dict[str, Any]:
        """Serializa o estado dos mutexes."""
        return {
            # Salva o dicionário legado self.mutexes (que é simples: id -> dono)
            'mutexes': copy.deepcopy(getattr(simulator, 'mutexes', {})),
            'mutex_queues': copy.deepcopy(getattr(simulator, '_mutex_queues', {}))
        }

    def _serialize_io_state(self, simulator) -> Dict[str, Any]:
        io_state = {
            'blocked': copy.deepcopy(getattr(simulator, '_blocked', {}))
        }
        if hasattr(simulator, 'io_manager'):
            io_state['operacoes'] = copy.deepcopy(getattr(simulator.io_manager, 'operacoes', []))
        return io_state