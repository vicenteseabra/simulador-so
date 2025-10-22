"""
Módulo contendo a classe Task (TCB) para o simulador.
Representa processos/tarefas no sistema operacional simulado.
"""


class TaskState:
    """Estados possíveis de uma tarefa no sistema."""
    NOVO = "NOVO"
    PRONTO = "PRONTO"
    EXECUTANDO = "EXECUTANDO"
    BLOQUEADO = "BLOQUEADO"
    TERMINADO = "TERMINADO"


class Task:
    """
    Representa uma tarefa/processo no simulador (Task Control Block).
    
    Attributes:
        id (str): Identificador único
        cor (str): Cor para visualização no Gantt
        ingresso (int): Tempo de chegada no sistema
        duracao (int): Tempo total de execução necessário
        prioridade (int): Prioridade (menor valor = maior prioridade)
        eventos (list): Lista de eventos (IO, ML, MU) da tarefa
        tempo_restante (int): Tempo de execução restante
        estado (str): Estado atual da tarefa
        tempo_inicio (int): Primeiro momento de execução
        tempo_fim (int): Momento de finalização
    """
    
    def __init__(self, task_id, cor, ingresso, duracao, prioridade=0, eventos=None):
        """Inicializa uma nova tarefa."""
        self.id = task_id
        self.cor = cor
        self.ingresso = ingresso
        self.duracao = duracao
        self.prioridade = prioridade
        self.eventos = eventos if eventos else []
        
        # Controle de execução
        self.tempo_restante = duracao
        self.estado = TaskState.NOVO
        self.tempo_inicio = None
        self.tempo_fim = None
        self.tempo_execucao = 0  # Tempo relativo de execução da tarefa
    
    def executar(self, tempo_atual):
        """
        Executa a tarefa por 1 tick.
        
        Args:
            tempo_atual (int): Tempo atual do sistema
            
        Returns:
            bool: True se a tarefa terminou
        """
        if self.estado != TaskState.EXECUTANDO:
            return False
            
        # Registra primeiro momento de execução
        if self.tempo_inicio is None:
            self.tempo_inicio = tempo_atual
        
        self.tempo_restante -= 1
        self.tempo_execucao += 1
        
        # Verifica finalização
        if self.tempo_restante == 0:
            self.estado = TaskState.TERMINADO
            self.tempo_fim = tempo_atual
            return True
            
        return False
    
    def admitir(self):
        """Admite tarefa no sistema (NOVO -> PRONTO)."""
        if self.estado == TaskState.NOVO:
            self.estado = TaskState.PRONTO
    
    def iniciar(self):
        """Inicia execução (PRONTO -> EXECUTANDO)."""
        if self.estado == TaskState.PRONTO:
            self.estado = TaskState.EXECUTANDO
    
    def preemptar(self):
        """Preempta tarefa (EXECUTANDO -> PRONTO)."""
        if self.estado == TaskState.EXECUTANDO:
            self.estado = TaskState.PRONTO
    
    def bloquear(self):
        """Bloqueia tarefa para I/O (EXECUTANDO -> BLOQUEADO)."""
        if self.estado == TaskState.EXECUTANDO:
            self.estado = TaskState.BLOQUEADO
    
    def desbloquear(self):
        """Desbloqueia tarefa (BLOQUEADO -> PRONTO)."""
        if self.estado == TaskState.BLOQUEADO:
            self.estado = TaskState.PRONTO
    
    def calcular_metricas(self):
        """
        Calcula métricas de desempenho.
        
        Returns:
            dict: turnaround_time, waiting_time, response_time
        """
        if self.estado != TaskState.TERMINADO:
            return None
            
        turnaround = self.tempo_fim - self.ingresso
        waiting = turnaround - self.duracao
        response = self.tempo_inicio - self.ingresso if self.tempo_inicio else 0
        
        return {
            'turnaround_time': turnaround,
            'waiting_time': waiting,
            'response_time': response
        }
    
    def __str__(self):
        return f"Task({self.id}, estado={self.estado}, rest={self.tempo_restante})"