"""Gerenciador de Mutex para sincronização de tarefas.

Este módulo fornece uma classe :class:`MutexManager` para lidar com travas de
exclusão mútua (mutexes) entre tarefas no simulador. Suporta:

- Aquisição de mutexes (concedendo posse ou enfileirando tarefas aguardando)
- Liberação de mutexes (transferindo posse para a próxima tarefa aguardando)
- Consulta de posse de mutex
- Utilitários de debug para inspecionar o estado de todos os mutexes

Protocolo de Uso
----------------

1. **Adquirir um mutex**: Chame ``solicitar_mutex(mutex_id, task_id)``.
   - Se o mutex estiver livre, a tarefa se torna dona imediatamente (retorna True).
   - Se o mutex for possuído por outra tarefa, a tarefa solicitante é adicionada à
     fila de espera (retorna False).

2. **Liberar um mutex**: Chame ``liberar_mutex(mutex_id, task_id)``.
   - A tarefa deve ser a dona atual do mutex, caso contrário um erro é lançado.
   - Se houver tarefas aguardando na fila, a posse é automaticamente
     transferida para a próxima tarefa na fila (ordem FIFO).
   - Se a fila estiver vazia, o mutex fica livre.

3. **Consultar posse**: Use ``tarefa_possui_mutex(task_id, mutex_id)`` para verificar
   se uma tarefa específica possui um mutex específico.

4. **Debugging**: Use ``obter_donos_mutex()`` para obter um dicionário mapeando cada
   mutex_id para seu dono atual (ou None se livre).

Tratamento de Erros
-------------------
- Tentar liberar um mutex não possuído pela tarefa lança um ``ValueError``.
- Todas as outras operações são seguras e idempotentes.

Notas de Integração
-------------------
O MutexManager é projetado para ser usado pela classe Simulator. Quando uma tarefa
executa um MutexLockEvent, o simulador deve chamar ``solicitar_mutex()``.
Quando uma tarefa executa um MutexUnlockEvent, o simulador deve chamar
``liberar_mutex()``.

Se uma tarefa solicita um mutex e retorna False, o simulador deve tipicamente
bloquear essa tarefa até que o mutex seja concedido. O gerenciador não lida com o
bloqueio de tarefas diretamente - essa é a responsabilidade do escalonador/simulador.
"""

from __future__ import annotations

from typing import Dict, List, Optional


class MutexManager:
    """Gerencia travas de exclusão mútua para sincronização de tarefas.

    Esta classe mantém um dicionário de mutexes, onde cada mutex pode ser possuído
    por no máximo uma tarefa por vez. Tarefas que solicitam um mutex já possuído
    são colocadas em uma fila de espera FIFO.

    Attributes:
        mutexes: Dicionário mapeando mutex_id para estado do mutex.
                 Cada estado é um dicionário com:
                 - 'dono': task_id do dono (None se livre)
                 - 'fila_espera': lista de task_ids aguardando pelo mutex
    """

    def __init__(self):
        """Inicializa um MutexManager vazio sem mutexes."""
        self.mutexes: Dict[str, Dict[str, Optional[str] | List[str]]] = {}

    def solicitar_mutex(self, mutex_id: str, task_id: str) -> bool:
        """Solicita um mutex para uma tarefa.

        Se o mutex estiver livre (ainda não criado ou sem dono), a tarefa se torna
        dona imediatamente e este método retorna True.

        Se o mutex já for possuído por outra tarefa, a tarefa solicitante é
        adicionada à fila de espera e este método retorna False.

        Se a tarefa já possui o mutex, isso é um no-op e retorna True.

        Args:
            mutex_id: Identificador do mutex a solicitar.
            task_id: Identificador da tarefa solicitando o mutex.

        Returns:
            True se o mutex foi concedido imediatamente, False se a tarefa foi enfileirada.
        """
        # Inicializa mutex se não existir
        if mutex_id not in self.mutexes:
            self.mutexes[mutex_id] = {
                'dono': None,
                'fila_espera': []
            }

        mutex = self.mutexes[mutex_id]

        # Verifica se mutex está livre
        if mutex['dono'] is None:
            mutex['dono'] = task_id
            return True

        # Verifica se tarefa já possui o mutex (requisição reentrante)
        if mutex['dono'] == task_id:
            return True

        # Mutex é possuído por outra tarefa - adiciona à fila de espera
        fila = mutex['fila_espera']
        if task_id not in fila:  # Evita entradas duplicadas
            fila.append(task_id)

        return False

    def liberar_mutex(self, mutex_id: str, task_id: str) -> Optional[str]:
        """Libera um mutex possuído por uma tarefa.

        A tarefa deve ser a dona atual do mutex. Se houver tarefas
        aguardando na fila, a posse é automaticamente transferida para a
        próxima tarefa na fila (FIFO). Se a fila estiver vazia, o mutex fica livre.

        Args:
            mutex_id: Identificador do mutex a liberar.
            task_id: Identificador da tarefa liberando o mutex.

        Returns:
            O task_id do próximo dono (da fila), ou None se o
            mutex ficar livre.

        Raises:
            ValueError: Se o mutex não existir, ou a tarefa não for a dona.
        """
        # Verifica se mutex existe
        if mutex_id not in self.mutexes:
            raise ValueError(
                f"Erro: tentativa de liberar mutex '{mutex_id}' que não existe. "
                f"Task: {task_id}"
            )

        mutex = self.mutexes[mutex_id]

        # Valida que a tarefa possui o mutex
        if mutex['dono'] != task_id:
            current_owner = mutex['dono'] or 'nenhum'
            raise ValueError(
                f"Erro: task '{task_id}' tentou liberar mutex '{mutex_id}', "
                f"mas o dono atual é '{current_owner}'"
            )

        # Transfere posse para próxima tarefa na fila, ou libera o mutex
        fila = mutex['fila_espera']

        if fila:
            # Transfere para próxima tarefa aguardando
            next_owner = fila.pop(0)
            mutex['dono'] = next_owner
            return next_owner
        else:
            # Nenhuma tarefa aguardando - mutex fica livre
            mutex['dono'] = None
            return None

    def tarefa_possui_mutex(self, task_id: str, mutex_id: str) -> bool:
        """Verifica se uma tarefa possui um mutex específico.

        Args:
            task_id: Identificador da tarefa a verificar.
            mutex_id: Identificador do mutex a verificar.

        Returns:
            True se a tarefa possui o mutex, False caso contrário.
        """
        if mutex_id not in self.mutexes:
            return False

        return self.mutexes[mutex_id]['dono'] == task_id

    def obter_donos_mutex(self) -> Dict[str, Optional[str]]:
        """Obtém um dicionário de todos os donos de mutex (para debugging).

        Returns:
            Dicionário mapeando mutex_id para o task_id do dono atual.
            Se um mutex estiver livre, o valor é None.
        """
        return {
            mutex_id: mutex['dono']
            for mutex_id, mutex in self.mutexes.items()
        }

    def obter_fila_espera(self, mutex_id: str) -> List[str]:
        """Obtém a fila de espera para um mutex específico (para debugging).

        Args:
            mutex_id: Identificador do mutex.

        Returns:
            Lista de task_ids aguardando pelo mutex. Lista vazia se nenhuma tarefa aguardando
            ou se o mutex não existir.
        """
        if mutex_id not in self.mutexes:
            return []

        return list(self.mutexes[mutex_id]['fila_espera'])

    def obter_estado_completo(self) -> Dict[str, Dict]:
        """Obtém o estado completo de todos os mutexes (para debugging/testes).

        Returns:
            Cópia profunda do dicionário de mutexes com todas as informações de estado.
        """
        return {
            mutex_id: {
                'dono': mutex['dono'],
                'fila_espera': list(mutex['fila_espera'])
            }
            for mutex_id, mutex in self.mutexes.items()
        }

    def limpar(self):
        """Limpa todos os mutexes (útil para testes/reset)."""
        self.mutexes.clear()

    def __repr__(self) -> str:
        """Representação string para debugging."""
        return f"MutexManager(mutexes={len(self.mutexes)})"

    def __str__(self) -> str:
        """Representação string legível para humanos."""
        if not self.mutexes:
            return "MutexManager: nenhum mutex"

        lines = ["MutexManager:"]
        for mutex_id, mutex in self.mutexes.items():
            dono = mutex['dono'] or 'livre'
            fila = mutex['fila_espera']
            fila_str = f", fila: {fila}" if fila else ""
            lines.append(f"  {mutex_id}: dono={dono}{fila_str}")

        return "\n".join(lines)

