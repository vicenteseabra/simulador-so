# src/simulator.py

from src.clock import Clock
from src.task import TCB, TaskState


class Simulator:
    """
    Classe principal que orquestra a simulação do sistema operacional.
    Controla:
    - Avanço do relógio
    - Chegada e execução das tarefas
    - Comunicação com o escalonador
    - Registro do histórico de execução
    """

    def __init__(self, scheduler):
        """
        Inicializa o simulador com um escalonador e o relógio zerado.
        """
        self.clock = Clock()
        self.clock.reset()
        self.scheduler = scheduler
        self.tasks = []
        self.historico_execucao = []

    # Carregamento e controle de tarefas
    def carregar_tarefas(self, tasks):
        """
        Recebe uma lista de TCBs e prepara as tarefas para a simulação.
        """
        self.tasks = tasks
        for task in self.tasks:
            task.estado = TaskState.NOVO

    def verificar_novas_tarefas(self):
        """
        Admite tarefas cujo tempo de ingresso é igual ao tempo atual.
        """
        tempo_atual = self.clock.get_tempo()
        for task in self.tasks:
            if task.estado == TaskState.NOVO and task.ingresso == tempo_atual:
                task.admitir()
                self.scheduler.adicionar_tarefa(task)

    # Execução de um ciclo
    def executar_tick(self):
        """
        Executa um ciclo de simulação (1 unidade de tempo):
        1. Verifica novas tarefas
        2. Pede ao escalonador a próxima tarefa
        3. Executa a tarefa (1 unidade)
        4. Atualiza estados e histórico
        5. Avança o relógio
        """
        tempo_atual = self.clock.get_tempo()
        self.verificar_novas_tarefas()

        # Chama o método correto do scheduler
        tarefa = self.scheduler.selecionar_proxima_tarefa()
        if tarefa:
            if tarefa.estado == TaskState.PRONTO:
                tarefa.iniciar_execucao(tempo_atual)

            tarefa.executar(1)
            self.historico_execucao.append((tempo_atual, tarefa.id))

            if tarefa.estado == TaskState.TERMINADO:
                tarefa.finalizar(tempo_atual + 1)
                self.scheduler.remover_tarefa(tarefa)
        else:
            # Nenhuma tarefa disponível (CPU ociosa)
            self.historico_execucao.append((tempo_atual, None))
        # Avança o relógio
        self.clock.tick()

    # Controle de término
    def tem_tarefas_pendentes(self):
        """
        Retorna True enquanto existir alguma tarefa não terminada.
        """
        return any(t.estado != TaskState.TERMINADO for t in self.tasks)

    # Execução completa da simulação
    def executar(self, tempo_max=None, log=False):
        """
        Executa a simulação até todas as tarefas terminarem
        ou até atingir o tempo máximo (se definido).
        """
        self.clock.reset()  # sempre inicia o relógio do zero

        while self.tem_tarefas_pendentes():
            if tempo_max is not None and self.clock.get_tempo() >= tempo_max:
                print("Tempo máximo atingido, encerrando simulação.")
                break

            if log:
                print(f"[t={self.clock.get_tempo()}] Executando tick...")

            self.executar_tick()

        if log:
            print("Simulação encerrada.")
        return self.historico_execucao
