"""
Módulo contendo a classe Task (TCB) para o simulador.
Representa processos/tarefas no sistema operacional simulado.
"""


class TaskState:
    """Estados possíveis de uma tarefa no ciclo de vida de um processo no SO."""
    NOVO = "NOVO" # A tarefa foi criada, mas ainda não está pronta para execução
    PRONTO = "PRONTO" # A tarefa está na fila, aguardando a CPU
    EXECUTANDO = "EXECUTANDO"  # A tarefa está atualmente em execução na CPU
    BLOQUEADO = "BLOQUEADO" # A tarefa está aguardando por I/O ou outro evento
    TERMINADO = "TERMINADO" # A tarefa completou sua execução


class Task:
    """
    Representa uma tarefa/processo no simulador (Task Control Block).
    Contém todos os atributos de controle e métricas de tempo.
    
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
        # Parâmetros de entrada
        self.id = task_id
        self.cor = cor
        self.ingresso = ingresso
        self.duracao = duracao
        self.prioridade = prioridade
        # Normaliza eventos: o ConfigParser pode fornecer dicionários (tipo, tempo, duracao)
        # enquanto o subsistema de eventos fornece instâncias de Event. Converte
        # dicionários em objetos do módulo `src.events` quando necessário.
        if eventos:
            normalized = []
            for ev in eventos:
                if isinstance(ev, dict):
                    try:
                        from src import events as _events
                        tipo = ev.get('tipo')
                        tempo = ev.get('tempo')
                        if tipo == 'IO':
                            dur = ev.get('duracao', 0)
                            normalized.append(_events.IOEvent(tipo='IO', tempo_relativo=tempo, duracao=dur, task_id=task_id))
                        elif tipo == 'ML':
                            # Mutex Lock (uses a default mutex id)
                            normalized.append(_events.MutexLockEvent(tipo='ML', tempo_relativo=tempo, mutex_id='m0', task_id=task_id))
                        elif tipo == 'MU':
                            normalized.append(_events.MutexUnlockEvent(tipo='MU', tempo_relativo=tempo, mutex_id='m0', task_id=task_id))
                        else:
                            # Unknown event dict - ignore
                            continue
                    except Exception:
                        # If importing/conversion fails, keep original dict for backward compatibility
                        normalized.append(ev)
                else:
                    # Already an Event instance (or other object)
                    normalized.append(ev)
            self.eventos = normalized
        else:
            self.eventos = []
        
        # Controle de execução
        self.tempo_restante = duracao
        self.estado = TaskState.NOVO
        self.tempo_inicio = None
        self.tempo_fim = None
        self.tempo_execucao = 0  # Tempo relativo de execução da tarefa
        self.numero_preempcoes = 0  # Contador de preempções
    
    def executar(self, tempo_atual):
        """
        Simula a execução da tarefa por um tick de tempo.
        
        Args:
            tempo_atual (int): Tempo atual do sistema
            
        Returns:
            bool: True se a tarefa terminou
        """
        # Checagem de Pré-condição: Só executa se estiver no estado EXECUTANDO.
        if self.estado != TaskState.EXECUTANDO:
            return False
            
        # Registro do Início: Se for a primeira vez que a tarefa executa, registra o tempo.
        if self.tempo_inicio is None:
            self.tempo_inicio = tempo_atual

        # Consumo de CPU: Decrementa o tempo restante e incrementa o tempo total executado.
        self.tempo_restante -= 1
        self.tempo_execucao += 1
        
        # Verificação de Finalização: Se o tempo restante chegou a zero, a tarefa terminou.
        if self.tempo_restante == 0:
            self.estado = TaskState.TERMINADO
            self.tempo_fim = tempo_atual + 1  # Tempo após completar execução
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
            self.numero_preempcoes += 1
    
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