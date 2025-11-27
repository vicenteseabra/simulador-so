"""Sistema de eventos para o simulador.

Define uma classe base :class:`Event` e vários tipos concretos de eventos:

- Event: classe base com atributos `tipo`, `tempo_relativo`, `task_id` e um método abstrato `executar(sistema, tarefa)`.
- IOEvent: representa uma operação de E/S que bloqueia a tarefa por `duracao` ticks.
- MutexLockEvent: solicita um mutex com id `mutex_id` em nome da tarefa.
- MutexUnlockEvent: libera um mutex com id `mutex_id` possuído pela tarefa.

Cada evento também expõe `calcular_tempo_absoluto(tempo_inicio_tarefa)` que
converte o `tempo_relativo` do evento (relativo ao início da tarefa) em um
tempo de tick absoluto adicionando `tempo_inicio_tarefa`.

Notas sobre integração (contratos):
- `sistema` é esperado ser o objeto simulador de nível superior usado por
  `src.simulator` / `src.scheduler`. Os métodos concretos usados abaixo são mantidos
  mínimos: `bloquear_tarefa(task_id, duracao)`, `solicitar_mutex(task_id, mutex_id)`,
  e `liberar_mutex(task_id, mutex_id)` são invocados se presentes. Se o
  simulador expõe métodos com nomes diferentes, adapte as chamadas adequadamente.
- `tarefa` é a instância do objeto da tarefa que disparou o evento. Métodos e
  atributos em `tarefa` não são requeridos pela implementação base, mas podem ser
  usados por integradores.

Este módulo intencionalmente mantém as implementações de eventos leves para que
possam ser integradas em diferentes arquiteturas de escalonador/simulador. Cada
evento concreto registra a intenção via API do simulador e retorna um pequeno
dicionário descrevendo a ação realizada (útil para testes e debugging).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Event:
    """Classe base para eventos.

    Attributes:
        tipo: String curta identificando o tipo de evento (ex: 'IO', 'LOCK').
        tempo_relativo: Ticks inteiros após o início da tarefa quando o evento ocorre.
        task_id: Identificador da tarefa que gera o evento.
    """

    tipo: str
    tempo_relativo: int
    task_id: str

    def executar(self, sistema: Any, tarefa: Any) -> Optional[dict]:
        """Executa o evento contra o simulador ``sistema`` e ``tarefa``.

        Esta implementação base é um no-op e retorna ``None``. Subclasses
        devem sobrescrever e realizar as interações necessárias com o simulador.

        Args:
            sistema: A instância do simulador (ponto de integração).
            tarefa: A instância da tarefa que produziu este evento.

        Returns:
            Dicionário opcional com uma breve descrição da ação realizada.
        """

        return None

    def calcular_tempo_absoluto(self, tempo_inicio_tarefa: int) -> int:
        """Retorna o tick absoluto quando este evento deve disparar.

        Tempo absoluto = tempo_inicio_tarefa + tempo_relativo.
        """

        return tempo_inicio_tarefa + int(self.tempo_relativo)


@dataclass
class IOEvent(Event):
    """Evento de E/S que bloqueia a tarefa por uma duração.

    Attributes:
        duracao: Número de ticks que a tarefa será bloqueada realizando E/S.

    Lógica de execução:
        Chama `sistema.bloquear_tarefa(task_id, duracao)` se o simulador
        expõe esse método. Se não presente, tentará `sistema.block_task´.
    """

    duracao: int = 0

    def executar(self, sistema: Any, tarefa: Any) -> dict:
        # Preferencialmente chama uma API bem nomeada do simulador; mantém nomes de fallback
        if hasattr(sistema, "bloquear_tarefa"):
            sistema.bloquear_tarefa(self.task_id, self.duracao)
            action = "bloquear_tarefa"
        elif hasattr(sistema, "block_task"):
            sistema.block_task(self.task_id, self.duracao)
            action = "block_task"
        else:
            # Se nenhuma API adequada existe, não levanta erro — registra o que teria
            # acontecido para que código de nível superior possa se adaptar.
            action = "no_op"

        return {"event": "IO", "task_id": self.task_id, "duracao": self.duracao, "action": action}


@dataclass
class MutexLockEvent(Event):
    """Solicita um mutex para a tarefa.

    Attributes:
        mutex_id: Identificador do mutex a solicitar.

    Lógica de execução:
        Chama `sistema.solicitar_mutex(task_id, mutex_id)` se disponível, ou
        `sistema.request_mutex` como fallback.
    """

    mutex_id: str = ""

    def executar(self, sistema: Any, tarefa: Any) -> dict:
        if hasattr(sistema, "solicitar_mutex"):
            granted = sistema.solicitar_mutex(self.task_id, self.mutex_id)
            action = "solicitar_mutex"
        elif hasattr(sistema, "request_mutex"):
            granted = sistema.request_mutex(self.task_id, self.mutex_id)
            action = "request_mutex"
        else:
            granted = False
            action = "no_op"

        return {"event": "MUTEX_LOCK", "task_id": self.task_id, "mutex_id": self.mutex_id, "granted": granted, "action": action}


@dataclass
class MutexUnlockEvent(Event):
    """Libera um mutex possuído pela tarefa.

    Attributes:
        mutex_id: Identificador do mutex a liberar.

    Lógica de execução:
        Chama `sistema.liberar_mutex(task_id, mutex_id)` se disponível, ou
        `sistema.release_mutex` como fallback.
    """

    mutex_id: str = ""

    def executar(self, sistema: Any, tarefa: Any) -> dict:
        if hasattr(sistema, "liberar_mutex"):
            sistema.liberar_mutex(self.task_id, self.mutex_id)
            action = "liberar_mutex"
        elif hasattr(sistema, "release_mutex"):
            sistema.release_mutex(self.task_id, self.mutex_id)
            action = "release_mutex"
        else:
            action = "no_op"

        return {"event": "MUTEX_UNLOCK", "task_id": self.task_id, "mutex_id": self.mutex_id, "action": action}
