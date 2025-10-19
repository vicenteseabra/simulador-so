"""
Módulo contendo as classes Task e TCB (Task Control Block) para o simulador.

Este módulo implementa as estruturas de dados fundamentais para representar
processos/tarefas no sistema operacional simulado.

"""


class TaskState:
    """
    Representar os possíveis estados de uma tarefa/processo.
    
    Estados baseados no modelo clássico de estados de processo em SO:
    - NOVO: Processo criado mas ainda não admitido no sistema
    - PRONTO: Processo pronto para execução, aguardando CPU
    - EXECUTANDO: Processo atualmente em execução
    - BLOQUEADO: Processo aguardando I/O ou outro evento
    - TERMINADO: Processo finalizado
    """
    NOVO = "NOVO"
    PRONTO = "PRONTO"
    EXECUTANDO = "EXECUTANDO"
    BLOQUEADO = "BLOQUEADO"
    TERMINADO = "TERMINADO"
    
    @classmethod
    def get_all_states(cls):
        """Retorna todos os estados possíveis."""
        return [cls.NOVO, cls.PRONTO, cls.EXECUTANDO, cls.BLOQUEADO, cls.TERMINADO]
    
    @classmethod
    def is_valid_state(cls, state):
        """Verifica se um estado é válido."""
        return state in cls.get_all_states()


class Task:
    """
    Representa uma tarefa/processo no simulador de SO.
    
    Contém todos os atributos básicos necessários para o escalonamento
    e controle de processos.
    
    Attributes:
        id (str): Identificador único da tarefa
        cor (str): Cor para visualização no diagrama de Gantt
        ingresso (int): Tempo de chegada da tarefa no sistema
        duracao (int): Tempo total de execução necessário
        prioridade (int): Prioridade da tarefa (menor valor = maior prioridade)
        tempo_restante (int): Tempo de execução ainda necessário
        tempo_espera (int): Tempo total que a tarefa ficou esperando
        tempo_resposta (int ou None): Tempo entre chegada e primeira execução
        estado (str): Estado atual da tarefa
    """
    
    def __init__(self, task_id, cor, ingresso, duracao, prioridade=0):
        """
        Args:
            task_id (str): Identificador único da tarefa
            cor (str): Cor para visualização (formato hexadecimal ou nome)
            ingresso (int): Tempo de chegada no sistema
            duracao (int): Tempo total de execução necessário
            prioridade (int, optional): Prioridade da tarefa. Defaults to 0.
        
        Raises:
            ValueError: Se duração ou tempo de ingresso forem negativos
        """
        if duracao <= 0:
            raise ValueError("Duração deve ser maior que zero")
        if ingresso < 0:
            raise ValueError("Tempo de ingresso não pode ser negativo")
            
        self.id = task_id
        self.cor = cor
        self.ingresso = ingresso
        self.duracao = duracao
        self.prioridade = prioridade
        
        # Atributos de controle de execução
        self.tempo_restante = duracao
        self.tempo_espera = 0
        self.tempo_resposta = None
        self.estado = TaskState.NOVO
    
    def executar(self, quantum=1):
        """
        Executa a tarefa por um quantum de tempo.
        
        Args:
            quantum (int): Tempo de execução (default: 1)
            
        Returns:
            int: Tempo efetivamente executado
            
        Raises:
            RuntimeError: Se tarefa não estiver em estado executável
        """
        if self.estado != TaskState.EXECUTANDO:
            raise RuntimeError("Tarefa {} não está em execução".format(self.id))
            
        tempo_executado = min(quantum, self.tempo_restante)
        self.tempo_restante -= tempo_executado
        
        if self.tempo_restante == 0:
            self.estado = TaskState.TERMINADO
            
        return tempo_executado
    
    def pausar(self):
        """Pausa a execução da tarefa, mudando estado para PRONTO."""
        if self.estado == TaskState.EXECUTANDO:
            self.estado = TaskState.PRONTO
    
    def iniciar_execucao(self, tempo_atual):
        """
        Inicia a execução da tarefa.
        
        Args:
            tempo_atual (int): Tempo atual do sistema
        """
        if self.estado == TaskState.PRONTO:
            self.estado = TaskState.EXECUTANDO
            # Calcula tempo de resposta na primeira execução
            if self.tempo_resposta is None:
                self.tempo_resposta = tempo_atual - self.ingresso
    
    def bloquear(self):
        """Bloqueia a tarefa (para operações de I/O, por exemplo)."""
        if self.estado == TaskState.EXECUTANDO:
            self.estado = TaskState.BLOQUEADO
    
    def desbloquear(self):
        """Desbloqueia a tarefa, colocando-a no estado PRONTO."""
        if self.estado == TaskState.BLOQUEADO:
            self.estado = TaskState.PRONTO
    
    def admitir(self):
        """Admite a tarefa no sistema, mudando de NOVO para PRONTO."""
        if self.estado == TaskState.NOVO:
            self.estado = TaskState.PRONTO
    
    def calcular_metricas(self, tempo_finalizacao):
        """
        Calcula métricas de desempenho da tarefa.
        
        Args:
            tempo_finalizacao (int): Tempo em que a tarefa foi finalizada
            
        Returns:
            dict: Dicionário com as métricas calculadas
            - turnaround_time: Tempo total no sistema
            - waiting_time: Tempo total de espera
            - response_time: Tempo de resposta
            - normalized_turnaround: Turnaround normalizado
        
        Raises:
            ValueError: Se a tarefa não estiver terminada
        """
        if self.estado != TaskState.TERMINADO:
            raise ValueError("Só é possível calcular métricas de tarefas terminadas")
            
        turnaround_time = tempo_finalizacao - self.ingresso
        waiting_time = turnaround_time - self.duracao
        response_time = self.tempo_resposta if self.tempo_resposta is not None else 0
        normalized_turnaround = turnaround_time / self.duracao if self.duracao > 0 else 0
        
        return {
            'turnaround_time': turnaround_time,
            'waiting_time': waiting_time,
            'response_time': response_time,
            'normalized_turnaround': normalized_turnaround
        }
    
    def __str__(self):
        """
        Representação string da tarefa para debug.
        
        Returns:
            str: String formatada com informações da tarefa
        """
        return ("Task(id={}, estado={}, "
                "ingresso={}, duracao={}, "
                "prioridade={}, restante={}, "
                "espera={}, resposta={})".format(
                    self.id, self.estado, self.ingresso, self.duracao,
                    self.prioridade, self.tempo_restante,
                    self.tempo_espera, self.tempo_resposta))
    
    def __repr__(self):
        """Representação para debug."""
        return self.__str__()


class TCB(Task):
    """
    Task Control Block - Extende a classe Task com informações de controle detalhadas.
    
    O TCB mantém informações adicionais sobre o histórico de execução,
    tempos de início e fim, e outras informações de controle necessárias
    para o escalonador e análise de desempenho.

    Atributos:
        tempo_inicio_execucao (int ou None): Tempo da primeira execução
        tempo_fim (int ou None): Tempo de finalização
        historico_execucao (list): Histórico detalhado de execução
        contexto (dict): Informações de contexto adicional
    """
    
    def __init__(self, task_id, cor, ingresso, duracao, prioridade=0):
        """
        Inicializa um novo TCB.
        
        Args:
            task_id (str): Identificador único da tarefa
            cor (str): Cor para visualização
            ingresso (int): Tempo de chegada no sistema
            duracao (int): Tempo total de execução necessário
            prioridade (int, optional): Prioridade da tarefa. Defaults to 0.
        """
        super(TCB, self).__init__(task_id, cor, ingresso, duracao, prioridade)

        self.tempo_inicio_execucao = None
        self.tempo_fim = None
        self.historico_execucao = []
        self.contexto = {}
        
        # Contadores para análise
        self.numero_preempcoes = 0
        self.tempo_total_cpu = 0
    
    def iniciar_execucao(self, tempo_atual):
        """
        Inicia a execução da tarefa com logging detalhado.
        
        Args:
            tempo_atual (int): Tempo atual do sistema
        """
        super(TCB, self).iniciar_execucao(tempo_atual)
        
        # Registra primeira execução
        if self.tempo_inicio_execucao is None:
            self.tempo_inicio_execucao = tempo_atual
            
        # Adiciona entrada no histórico
        self.historico_execucao.append({
            'evento': 'INICIO_EXECUCAO',
            'tempo': tempo_atual,
            'estado_anterior': TaskState.PRONTO,
            'estado_novo': TaskState.EXECUTANDO
        })
    
    def executar(self, quantum=1):
        """
        Executa a tarefa com logging detalhado.
        
        Args:
            quantum (int): Tempo de execução
            
        Returns:
            int: Tempo efetivamente executado
        """
        tempo_executado = super(TCB, self).executar(quantum)
        self.tempo_total_cpu += tempo_executado
        
        # Log no histórico
        self.historico_execucao.append({
            'evento': 'EXECUCAO',
            'tempo_executado': tempo_executado,
            'tempo_restante': self.tempo_restante,
            'quantum_usado': quantum
        })
        
        return tempo_executado
    
    def pausar(self):
        """Pausa a execução com logging de preempção."""
        if self.estado == TaskState.EXECUTANDO:
            super(TCB, self).pausar()
            self.numero_preempcoes += 1
            
            self.historico_execucao.append({
                'evento': 'PREEMPCAO',
                'numero_preempcao': self.numero_preempcoes,
                'estado_anterior': TaskState.EXECUTANDO,
                'estado_novo': TaskState.PRONTO
            })
    
    def finalizar(self, tempo_atual):
        """
        Finaliza a tarefa com logging completo.
        
        Args:
            tempo_atual (int): Tempo de finalização
        """
        if self.estado in [TaskState.EXECUTANDO, TaskState.TERMINADO]:
            self.tempo_fim = tempo_atual
            self.estado = TaskState.TERMINADO
            
            self.historico_execucao.append({
                'evento': 'FINALIZACAO',
                'tempo': tempo_atual,
                'tempo_total_sistema': tempo_atual - self.ingresso,
                'tempo_total_cpu': self.tempo_total_cpu
            })
    
    def adicionar_contexto(self, chave, valor):
        """
        Adiciona informação de contexto ao TCB.
        
        Args:
            chave (str): Chave da informação
            valor: Valor da informação
        """
        self.contexto[chave] = valor
    
    def obter_estatisticas(self):
        """
        Obtém estatísticas detalhadas da tarefa.
        
        Returns:
            dict: Estatísticas completas da tarefa
        """
        if self.tempo_fim is None:
            raise ValueError("Tarefa ainda não foi finalizada")
            
        metricas_basicas = self.calcular_metricas(self.tempo_fim)
        
        # Cria uma cópia do contexto para não modificar o original
        contexto_copia = {}
        for chave, valor in self.contexto.items():
            contexto_copia[chave] = valor
        
        # Combina métricas básicas com informações do TCB
        result = {}
        for chave, valor in metricas_basicas.items():
            result[chave] = valor
            
        result['tempo_inicio_execucao'] = self.tempo_inicio_execucao
        result['tempo_fim'] = self.tempo_fim
        result['numero_preempcoes'] = self.numero_preempcoes
        result['tempo_total_cpu'] = self.tempo_total_cpu
        result['eficiencia_cpu'] = self.tempo_total_cpu / self.duracao if self.duracao > 0 else 0
        result['total_eventos'] = len(self.historico_execucao)
        result['contexto'] = contexto_copia
        
        return result
    
    def obter_historico_resumido(self):
        """
        Obtém um resumo textual do histórico de execução.
        
        Returns:
            list: Lista de strings descrevendo o histórico
        """
        resumo = []
        for evento in self.historico_execucao:
            if evento['evento'] == 'INICIO_EXECUCAO':
                resumo.append("t={}: Iniciou execução".format(evento['tempo']))
            elif evento['evento'] == 'EXECUCAO':
                resumo.append("Executou {}u, restam {}u".format(
                    evento['tempo_executado'], evento['tempo_restante']))
            elif evento['evento'] == 'PREEMPCAO':
                resumo.append("Preempção #{}".format(evento['numero_preempcao']))
            elif evento['evento'] == 'FINALIZACAO':
                resumo.append("t={}: Finalizada".format(evento['tempo']))
        return resumo
    
    def __str__(self):
        """
        Representação string detalhada do TCB.
        
        Returns:
            str: String formatada com informações do TCB
        """
        base_info = super(TCB, self).__str__()
        tcb_info = (", inicio_exec={}, "
                   "fim={}, preempcoes={}, "
                   "cpu_total={}".format(
                       self.tempo_inicio_execucao, self.tempo_fim,
                       self.numero_preempcoes, self.tempo_total_cpu))
        
        return base_info.replace(')', tcb_info + ')')