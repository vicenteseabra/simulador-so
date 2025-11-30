import time
from src.clock import Clock
from src.task import Task, TaskState
from src.gantt import GanttChart
from src.mutex_manager import MutexManager
from src.io_manager import IOManager


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
        tipo_algo = getattr(scheduler, 'tipo_escalonamento', scheduler.__class__.__name__)
        self.gantt = GanttChart(tipo_escalonamento=tipo_algo)

        # Gerenciadores de recursos
        self.mutex_manager = MutexManager()
        self.io_manager = IOManager()

        # Eventos pendentes por tarefa: task_id -> [eventos...]
        self.eventos_pendentes = {}

        # Estruturas para suporte a bloqueio e mutex (compatibilidade)
        # _blocked: task_id -> {'tipo': 'io'|'mutex', 'remaining': int|None, 'mutex_id': str|None}
        self._blocked = {}
        # mutexes: mutex_id -> owner_task_id or None (mantido para compatibilidade)
        self.mutexes = {}
        # filas de espera por mutex: mutex_id -> [task_id,...] (mantido para compatibilidade)
        self._mutex_queues = {}

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
                self.gantt.registrar_ingresso_fila(task.id, tempo_atual)

    def verificar_io_conclusoes(self):
        """
        Verifica operações de I/O concluídas e desbloqueia tarefas correspondentes.
        Usa o IOManager para obter lista de tarefas com I/O completo.
        """
        tempo_atual = self.clock.get_tempo()
        conclusoes = self.io_manager.verificar_conclusoes(tempo_atual)

        for task_id in conclusoes:
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task and task.estado == TaskState.BLOQUEADO:
                task.desbloquear()
                # Remove da estrutura de bloqueio legada
                if task_id in self._blocked:
                    self._blocked.pop(task_id, None)
                # Adiciona tarefa de volta à fila de prontos
                # IMPORTANTE: verificamos se já não está na fila para evitar duplicatas
                if task not in self.scheduler.fila_prontos:
                    self.scheduler.adicionar_tarefa(task)
                    # DEBUG (desativado)
                    # print(f"[DEBUG] Tarefa {task_id} desbloqueada e adicionada à fila no tempo {tempo_atual}")

    def processar_eventos_tarefa(self, tarefa, tempo_atual):
        """
        Processa eventos da tarefa que devem ocorrer no tick atual.
        Verifica eventos com tempo relativo igual ao tempo de execução da tarefa.

        Args:
            tarefa: Tarefa em execução
            tempo_atual: Tempo atual do sistema
        """
        if not hasattr(tarefa, 'eventos') or not tarefa.eventos:
            return

        # Identifica eventos a disparar neste tick
        # Eventos são disparados quando tempo_execucao da tarefa atinge tempo_relativo do evento
        eventos_a_disparar = [
            ev for ev in list(tarefa.eventos)
            if hasattr(ev, 'tempo_relativo') and tarefa.tempo_execucao == int(ev.tempo_relativo)
        ]

        for evento in eventos_a_disparar:
            try:
                # Executa o evento
                resultado = evento.executar(self, tarefa)

                # Registra no histórico (opcional)
                if resultado:
                    if tarefa.id not in self.eventos_pendentes:
                        self.eventos_pendentes[tarefa.id] = []
                    self.eventos_pendentes[tarefa.id].append({
                        'tempo': tempo_atual,
                        'tipo': evento.tipo,
                        'resultado': resultado
                    })

            except Exception as e:
                # Não deixamos uma exceção de evento quebrar a simulação
                print(f"Aviso: Erro ao processar evento {evento.tipo} da tarefa {tarefa.id}: {e}")

            # Remove evento disparado
            if evento in tarefa.eventos:
                tarefa.eventos.remove(evento)

    # Execução de um ciclo
    def executar_tick(self):
        """
        Executa um ciclo de simulação (1 unidade de tempo) com novo fluxo integrado:
        1. Desbloqueia tarefas com I/O completo
        2. Verifica novas tarefas
        3. Aplica envelhecimento (se scheduler suportar)
        4. Seleciona e executa próxima tarefa
        5. Processa eventos da tarefa executada
        6. Atualiza estados e histórico
        7. Avança o relógio
        """
        tempo_atual = self.clock.get_tempo()

        # PASSO 1: Desbloquear tarefas com I/O completo
        self.verificar_io_conclusoes()

        # PASSO 2: Verificar chegada de novas tarefas
        self.verificar_novas_tarefas()

        # Identifica tarefa atualmente executando
        tarefa_executando = None
        for t in self.scheduler.fila_prontos:
            if t.estado == TaskState.EXECUTANDO:
                tarefa_executando = t
                break
        
        # PASSO 3: Aplicar envelhecimento (se scheduler suportar)
        if hasattr(self.scheduler, 'aplicar_envelhecimento'):
            self.scheduler.aplicar_envelhecimento()

        # PASSO 4: Selecionar próxima tarefa (lógica normal de escalonamento)
        tarefa = self.scheduler.selecionar_proxima_tarefa()
        
        # Se mudou de tarefa, pausa a anterior (preempção)
        if tarefa_executando and tarefa != tarefa_executando:
            tarefa_executando.preemptar()
        
        # PASSO 5: Executar tarefa selecionada
        if tarefa:
            # Se a tarefa selecionada estava PRONTO, ela agora INICIA a execução
            if tarefa.estado == TaskState.PRONTO:
                tarefa.iniciar()

            # Executa um tick da tarefa
            tarefa.executar(tempo_atual)
            self.historico_execucao.append((tempo_atual, tarefa.id))

            # PASSO 6: Processar eventos da tarefa DEPOIS de executar
            # (eventos são disparados após a execução do tick)
            if tarefa.estado != TaskState.TERMINADO:
                self.processar_eventos_tarefa(tarefa, tempo_atual)

            # Verifica se tarefa terminou
            if tarefa.estado == TaskState.TERMINADO:
                self.scheduler.remover_tarefa(tarefa)
        else:
            # Nenhuma tarefa disponível (CPU ociosa)
            self.historico_execucao.append((tempo_atual, None))

        # PASSO 7: Atualizar bloqueios legados e avançar o relógio
        # Mantém compatibilidade com código existente
        self._update_blocked_tasks()
        self.clock.tick()

    # --- Bloqueio e Mutex API (integração com src/events.py) ---
    def bloquear_tarefa(self, task_id: str, duracao: int):
        """
        Bloqueia a tarefa por `duracao` ticks (I/O).
        Usa IOManager para gerenciar a operação de I/O.
        """
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return False

        # Bloqueia a tarefa
        task.bloquear()

        # Remove da fila de prontos se estiver lá
        if task in self.scheduler.fila_prontos:
            self.scheduler.remover_tarefa(task)

        # Registra operação de I/O no IOManager
        tempo_atual = self.clock.get_tempo()
        self.io_manager.iniciar_io(task_id, duracao, tempo_atual)

        # Mantém estrutura legada para compatibilidade
        self._blocked[task_id] = {'tipo': 'io', 'remaining': int(duracao), 'mutex_id': None}

        return True

    # alias com nome em inglês
    def block_task(self, task_id: str, duracao: int):
        return self.bloquear_tarefa(task_id, duracao)

    def solicitar_mutex(self, task_id: str, mutex_id: str) -> bool:
        """
        Solicita o mutex; retorna True se concedido, False se enfileirado.
        Usa MutexManager para gerenciar mutexes.
        """
        # Usa o MutexManager
        concedido = self.mutex_manager.solicitar_mutex(mutex_id, task_id)

        if not concedido:
            # Mutex não foi concedido - bloqueia a tarefa
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task:
                task.bloquear()
                # Remove da fila de prontos
                if task in self.scheduler.fila_prontos:
                    self.scheduler.remover_tarefa(task)
                # Mantém estrutura legada para compatibilidade
                self._blocked[task_id] = {'tipo': 'mutex', 'remaining': None, 'mutex_id': mutex_id}

        # Sincroniza estruturas legadas
        self.mutexes = {mid: self.mutex_manager.mutexes.get(mid, {}).get('dono')
                       for mid in self.mutex_manager.mutexes}
        self._mutex_queues = {mid: list(self.mutex_manager.mutexes.get(mid, {}).get('fila_espera', []))
                             for mid in self.mutex_manager.mutexes}

        return concedido

    def request_mutex(self, task_id: str, mutex_id: str) -> bool:
        return self.solicitar_mutex(task_id, mutex_id)

    def liberar_mutex(self, task_id: str, mutex_id: str) -> bool:
        """
        Libera o mutex; se houver fila de espera, concede ao próximo e desbloqueia-o.
        Usa MutexManager para gerenciar mutexes.
        """
        # Usa o MutexManager
        try:
            next_task_id = self.mutex_manager.liberar_mutex(mutex_id, task_id)

            # Se há próxima tarefa na fila, desbloqueia ela
            if next_task_id:
                next_task = next((t for t in self.tasks if t.id == next_task_id), None)
                if next_task:
                    next_task.desbloquear()
                    # Remove do bloqueio
                    if next_task_id in self._blocked:
                        self._blocked.pop(next_task_id, None)
                    # Adiciona de volta à fila de prontos
                    if next_task not in self.scheduler.fila_prontos:
                        self.scheduler.adicionar_tarefa(next_task)

            # Sincroniza estruturas legadas
            self.mutexes = {mid: self.mutex_manager.mutexes.get(mid, {}).get('dono')
                           for mid in self.mutex_manager.mutexes}
            self._mutex_queues = {mid: list(self.mutex_manager.mutexes.get(mid, {}).get('fila_espera', []))
                                 for mid in self.mutex_manager.mutexes}

            return True

        except ValueError:
            # Tentativa de liberar mutex que não é de propriedade
            return False

    def release_mutex(self, task_id: str, mutex_id: str) -> bool:
        return self.liberar_mutex(task_id, mutex_id)

    def _update_blocked_tasks(self):
        """
        Atualiza estruturas legadas de bloqueio.
        NOTA: A lógica de I/O agora é gerenciada pelo IOManager em verificar_io_conclusoes().
        Este método mantido apenas para compatibilidade com código legado de mutex.
        """
        # Removida lógica de I/O - agora gerenciada por IOManager
        # A verificação de mutex já é feita em liberar_mutex()
        pass

    # Controle de término
    def tem_tarefas_pendentes(self):
        """
        Verifica se ainda há alguma tarefa que não terminou (NOVO, PRONTO, EXECUTANDO, BLOQUEADO).
        Usado para determinar o fim da simulação.
        """
        return any(t.estado != TaskState.TERMINADO for t in self.tasks)

    # Execução completa da simulação
    def executar(self, tempo_max=None, log=False):
        """
        Executa a simulação até todas as tarefas terminarem
        ou até atingir o tempo máximo (se definido).
        Função interna para converter o histórico de execução tick-a-tick
        em intervalos consolidados para o Gráfico de Gantt.
        Evita que o Gantt tenha que desenhar milhares de barras de 1 tick.
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
        
        # Processa histórico para preencher o gantt
        self._processar_historico_gantt()
        
        return self.historico_execucao
    
    def executar_completo(self):
        """
        Executa a simulação completa (sem logs) e retorna estatísticas finais.
        """
        start_time = time.time()
        
        self.clock.reset()

        # Loop principal: executa tick por tick até que não haja mais tarefas pendentes
        while self.tem_tarefas_pendentes():
            self.executar_tick()

        end_time = time.time()
        
        # Cálculo de estatísticas de tempo real e tempo de simulação
        tempo_execucao_real_ms = (end_time - start_time) * 1000
        tempo_total_ticks = self.clock.get_tempo()

        estatisticas = {
            'tempo_total_ticks': tempo_total_ticks,
            'tempo_execucao_real_ms': tempo_execucao_real_ms,
            'historico_execucao': self.historico_execucao
        }
        
        # Processa histórico para preencher o gantt
        self._processar_historico_gantt()

        return estatisticas

    def _processar_historico_gantt(self):
        """
        Processa o histórico de execução e adiciona intervalos ao gantt.
        Agrupa execuções consecutivas da mesma tarefa em um único intervalo.
        """
        if not self.historico_execucao:
            return
        
        # Cria um dicionário de cores por tarefa
        cores = {task.id: task.cor for task in self.tasks}
        
        # Agrupa intervalos consecutivos
        intervalo_atual = None
        
        for tempo, task_id in self.historico_execucao:
            if task_id is None:  # CPU ociosa
                if intervalo_atual:
                    # Finaliza intervalo anterior
                    self.gantt.adicionar_intervalo(
                        intervalo_atual['task_id'],
                        intervalo_atual['inicio'],
                        tempo,
                        intervalo_atual['cor']
                    )
                    intervalo_atual = None
            else:
                if intervalo_atual and intervalo_atual['task_id'] == task_id:
                    # Continua no mesmo intervalo (não faz nada)
                    pass
                else:
                    # Nova tarefa
                    if intervalo_atual:
                        # Finaliza intervalo anterior
                        self.gantt.adicionar_intervalo(
                            intervalo_atual['task_id'],
                            intervalo_atual['inicio'],
                            tempo,
                            intervalo_atual['cor']
                        )
                    # Inicia novo intervalo
                    intervalo_atual = {
                        'task_id': task_id,
                        'inicio': tempo,
                        'cor': cores.get(task_id, '#999999')
                    }
        
        # Finaliza último intervalo se existir
        if intervalo_atual:
            self.gantt.adicionar_intervalo(
                intervalo_atual['task_id'],
                intervalo_atual['inicio'],
                self.clock.get_tempo(),
                intervalo_atual['cor']
            )

    def _exibir_estado_sistema(self):
        """Exibe o estado atual do sistema de forma formatada."""
        tempo = self.clock.get_tempo()
        
        # Tarefa em execução
        exec_task = next((t for t in self.tasks if t.estado == TaskState.EXECUTANDO), None)
        exec_str = f"Task {exec_task.id}" if exec_task else "IDLE"
        
        # Tarefas prontas
        prontos = [t.id for t in self.scheduler.fila_prontos if t.estado == TaskState.PRONTO]
        
        # Tarefas finalizadas
        finalizados = [t.id for t in self.tasks if t.estado == TaskState.TERMINADO]
        
        print(f"[Tick {tempo}] Executando: {exec_str} | "
            f"Prontos: {prontos} | Finalizados: {finalizados}")

    def _exibir_info_tarefa(self, task_id):
        """
        Exibe informações detalhadas de uma tarefa.
        
        Args:
            task_id (str): ID da tarefa
        """
        task = next((t for t in self.tasks if t.id == task_id), None)
        
        if not task:
            print(f"Tarefa '{task_id}' não encontrada.")
            return
        
        print(f"\n=== Tarefa {task.id} ===")
        print(f"Estado: {task.estado}")
        print(f"Prioridade: {task.prioridade}")
        print(f"Ingresso: {task.ingresso}")
        print(f"Duração: {task.duracao}")
        print(f"Restante: {task.tempo_restante}")
        print(f"Executado: {task.tempo_execucao}")
        print(f"Início: {task.tempo_inicio if task.tempo_inicio is not None else 'N/A'}")
        
        if task.tempo_fim is not None:
            print(f"Fim: {task.tempo_fim}")
        
        if task.estado == TaskState.TERMINADO:
            m = task.calcular_metricas()
            if m:
                print(f"Turnaround: {m['turnaround_time']}")
                print(f"Waiting: {m['waiting_time']}")
                print(f"Response: {m['response_time']}")
        print()

    def _exibir_status_geral(self):
        """Exibe status geral do sistema."""
        print(f"\n=== Status do Sistema ===")
        print(f"Tempo: {self.clock.get_tempo()}")
        print(f"Algoritmo: {self.scheduler.__class__.__name__}")
        
        # Conta estados
        estados = {
            TaskState.NOVO: 0,
            TaskState.PRONTO: 0,
            TaskState.EXECUTANDO: 0,
            TaskState.BLOQUEADO: 0,
            TaskState.TERMINADO: 0
        }
        for task in self.tasks:
            estados[task.estado] += 1
        
        print(f"Tarefas: {len(self.tasks)}")
        print(f"  Novas: {estados[TaskState.NOVO]}")
        print(f"  Prontas: {estados[TaskState.PRONTO]}")
        print(f"  Executando: {estados[TaskState.EXECUTANDO]}")
        print(f"  Bloqueadas: {estados[TaskState.BLOQUEADO]}")
        print(f"  Terminadas: {estados[TaskState.TERMINADO]}")
        print()

    def executar_passo_a_passo(self):
        """
        Executa simulação em modo passo-a-passo (debugger).
        
        Comandos:
            Enter: próximo passo
            q/quit: sair
            info <id>: detalhes da tarefa
            status: status geral
            continue: executar até o fim
        """
        self.clock.reset()
        modo_continue = False
        
        print("\n=== Modo Passo-a-Passo ===")
        print("Comandos: Enter (próximo) | q (sair) | info <id> | status | continue")
        print("=" * 60 + "\n")
        
        while self.tem_tarefas_pendentes():
            self.executar_tick()
            self._exibir_estado_sistema()
            
            if modo_continue:
                continue
            
            # Loop de comandos
            while True:
                try:
                    cmd = input("> ").strip().lower()
                    
                    # Enter - próximo tick
                    if not cmd:
                        break
                    
                    # Sair
                    if cmd in ['q', 'quit']:
                        print("Encerrando simulação.")
                        return self.historico_execucao
                    
                    # Continue
                    if cmd == 'continue':
                        print("Executando até o fim...\n")
                        modo_continue = True
                        break
                    
                    # Status
                    if cmd == 'status':
                        self._exibir_status_geral()
                        continue
                    
                    # Info
                    if cmd.startswith('info '):
                        task_id = cmd.split(maxsplit=1)[1].strip()
                        self._exibir_info_tarefa(task_id)
                        continue
                    
                    print(f"Comando '{cmd}' não reconhecido.")
                    
                except KeyboardInterrupt:
                    print("\nInterrompido.")
                    return self.historico_execucao
                except Exception as e:
                    print(f"Erro: {e}")
        
        # Processa histórico para preencher o gantt
        self._processar_historico_gantt()
        
        print("\n=== Simulação Concluída ===")
        self._exibir_status_geral()
        return self.historico_execucao
