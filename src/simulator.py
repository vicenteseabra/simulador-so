import time
from src.clock import Clock
from src.task import Task, TaskState
from src.gantt import GanttChart


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
        # Estruturas para suporte a bloqueio e mutex
        # _blocked: task_id -> {'tipo': 'io'|'mutex', 'remaining': int|None, 'mutex_id': str|None}
        self._blocked = {}
        # mutexes: mutex_id -> owner_task_id or None
        self.mutexes = {}
        # filas de espera por mutex: mutex_id -> [task_id,...]
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

        # Pausa tarefa atualmente executando (para permitir preempção)
        tarefa_executando = None
        for t in self.scheduler.fila_prontos:
            if t.estado == TaskState.EXECUTANDO:
                tarefa_executando = t
                break
        
        # Seleciona próxima tarefa
        tarefa = self.scheduler.selecionar_proxima_tarefa()
        
        # Se mudou de tarefa, pausa a anterior (preempção)
        if tarefa_executando and tarefa != tarefa_executando:
            tarefa_executando.preemptar()
        
        if tarefa:
            # Se a tarefa selecionada estava PRONTO, ela agora INICIA a execução.
            if tarefa.estado == TaskState.PRONTO:
                tarefa.iniciar()

            tarefa.executar(tempo_atual)
            self.historico_execucao.append((tempo_atual, tarefa.id))

            # Após executar um tick, verifica se algum evento da tarefa deve ser disparado
            # Eventos são definidos em termos de tempo relativo de execução (tempo_execucao)
            if tarefa.estado != TaskState.TERMINADO and getattr(tarefa, 'eventos', None):
                to_fire = [ev for ev in list(tarefa.eventos)
                           if hasattr(ev, 'tempo_relativo') and tarefa.tempo_execucao == int(ev.tempo_relativo)]
                for ev in to_fire:
                    try:
                        ev.executar(self, tarefa)
                    except Exception:
                        # Não deixamos uma exceção de evento quebrar a simulação
                        pass
                    # Remove evento disparado
                    if ev in tarefa.eventos:
                        tarefa.eventos.remove(ev)

            if tarefa.estado == TaskState.TERMINADO:
                self.scheduler.remover_tarefa(tarefa)
        else:
            # Nenhuma tarefa disponível (CPU ociosa)
            self.historico_execucao.append((tempo_atual, None))
        # Avança o relógio
        # Atualiza bloqueios (I/O e mutexes) antes de avançar o relógio
        self._update_blocked_tasks()
        self.clock.tick()

    # --- Bloqueio e Mutex API (integração com src/events.py) ---
    def bloquear_tarefa(self, task_id: str, duracao: int):
        """Bloqueia a tarefa por `duracao` ticks (I/O)."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return False
        task.bloquear()
        # registra bloqueio com contador
        self._blocked[task_id] = {'tipo': 'io', 'remaining': int(duracao), 'mutex_id': None}
        return True

    # alias com nome em inglês
    def block_task(self, task_id: str, duracao: int):
        return self.bloquear_tarefa(task_id, duracao)

    def solicitar_mutex(self, task_id: str, mutex_id: str) -> bool:
        """Solicita o mutex; retorna True se concedido, False se enfileirado."""
        owner = self.mutexes.get(mutex_id)
        if owner is None:
            # concede imediatamente
            self.mutexes[mutex_id] = task_id
            return True
        else:
            # coloca na fila de espera e bloqueia a tarefa (aguardando mutex)
            q = self._mutex_queues.setdefault(mutex_id, [])
            if task_id not in q:
                q.append(task_id)
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task:
                task.bloquear()
                self._blocked[task_id] = {'tipo': 'mutex', 'remaining': None, 'mutex_id': mutex_id}
            return False

    def request_mutex(self, task_id: str, mutex_id: str) -> bool:
        return self.solicitar_mutex(task_id, mutex_id)

    def liberar_mutex(self, task_id: str, mutex_id: str) -> bool:
        """Libera o mutex; se houver fila de espera, concede ao próximo e desbloqueia-o."""
        owner = self.mutexes.get(mutex_id)
        if owner != task_id:
            # tentativa de liberar mutex que não é de propriedade
            return False
        queue = self._mutex_queues.get(mutex_id) or []
        if queue:
            next_task_id = queue.pop(0)
            # concede para próximo
            self.mutexes[mutex_id] = next_task_id
            # desbloqueia a próxima tarefa
            next_task = next((t for t in self.tasks if t.id == next_task_id), None)
            if next_task:
                next_task.desbloquear()
                # remove do bloqueio por mutex
                if next_task_id in self._blocked:
                    self._blocked.pop(next_task_id, None)
        else:
            # nenhum esperando -> libera
            self.mutexes[mutex_id] = None
        return True

    def release_mutex(self, task_id: str, mutex_id: str) -> bool:
        return self.liberar_mutex(task_id, mutex_id)

    def _update_blocked_tasks(self):
        """Atualiza contadores de bloqueio e desbloqueia tarefas cujo tempo terminou."""
        to_unblock = []
        for task_id, info in list(self._blocked.items()):
            if info['tipo'] == 'io':
                # decrementa contador
                info['remaining'] -= 1
                if info['remaining'] <= 0:
                    to_unblock.append(task_id)
            else:
                # mutex wait -> nada a fazer aqui (liberação feita em liberar_mutex)
                continue

        for tid in to_unblock:
            task = next((t for t in self.tasks if t.id == tid), None)
            if task:
                task.desbloquear()
            self._blocked.pop(tid, None)

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
