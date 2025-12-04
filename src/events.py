"""
Módulo contendo definições de eventos para o simulador.
"""

class Event:
    """Classe base para eventos."""
    def __init__(self, tipo, tempo_relativo, task_id=''):
        self.tipo = tipo
        self.tempo_relativo = tempo_relativo
        self.task_id = task_id


class IOEvent(Event):
    """Evento de operação de I/O."""
    def __init__(self, tipo, tempo_relativo, task_id='', duracao=0):
        super().__init__(tipo, tempo_relativo, task_id)
        self.duracao = duracao


class MutexLockEvent(Event):
    """Evento de lock de mutex."""
    def __init__(self, tipo, tempo_relativo, task_id='', mutex_id=''):
        super().__init__(tipo, tempo_relativo, task_id)
        self.mutex_id = mutex_id


class MutexUnlockEvent(Event):
    """Evento de unlock de mutex."""
    def __init__(self, tipo, tempo_relativo, task_id='', mutex_id=''):
        super().__init__(tipo, tempo_relativo, task_id)
        self.mutex_id = mutex_id
