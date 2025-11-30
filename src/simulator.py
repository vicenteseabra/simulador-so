import time
from src.clock import Clock
from src.task import Task, TaskState
from src.gantt import GanttChart
from src.mutex_manager import MutexManager
from src.io_manager import IOManager
# IMPORTANTE: Importa o gerenciador de histórico
from src.history import HistoryManager


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
        
        # --- CORREÇÃO DO SEU ERRO ---
        # Inicializa o gerenciador de histórico
        self.history_manager = HistoryManager()
        # ----------------------------

        # Eventos pendentes por tarefa: task_id -> [eventos...]
        self.eventos_pendentes = {}

        # Estruturas para suporte a bloqueio e mutex (compatibilidade)
        self._blocked = {}
        self.mutexes = {}
        self._mutex_queues = {}

    # Carregamento e controle de tarefas
    def carregar_tarefas(self, tasks):
        self.tasks = tasks
        for task in self.tasks:
            task.estado = TaskState.NOVO
            # Reset de contadores para reexecução correta
            task.tempo_execucao = 0
            task.tempo_restante = task.duracao
            task.tempo_inicio = None
            task.tempo_fim = None
        
        # Limpa gerenciadores
        self.io_manager.limpar()
        self.mutex_manager.limpar()
        self.history_manager.limpar_historico()

    def verificar_novas_tarefas(self):
        tempo_atual = self.clock.get_tempo()
        for task in self.tasks:
            if task.estado == TaskState.NOVO and task.ingresso == tempo_atual:
                task.admitir()
                self.scheduler.adicionar_tarefa(task)
                self.gantt.registrar_ingresso_fila(task.id, tempo_atual)

    def verificar_io_conclusoes(self):
        tempo_atual = self.clock.get_tempo()
        conclusoes = self.io_manager.verificar_conclusoes(tempo_atual)

        for task_id in conclusoes:
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task and task.estado == TaskState.BLOQUEADO:
                task.desbloquear()
                if task_id in self._blocked:
                    self._blocked.pop(task_id, None)
                if task not in self.scheduler.fila_prontos:
                    self.scheduler.adicionar_tarefa(task)

    def processar_eventos_tarefa(self, tarefa, tempo_atual):
        """
        Processa eventos da tarefa. Retorna True se a tarefa foi BLOQUEADA.
        """
        if not hasattr(tarefa, 'eventos') or not tarefa.eventos:
            return False

        # Verifica eventos baseados no tempo relativo de execução
        eventos_a_disparar = [
            ev for ev in list(tarefa.eventos)
            if hasattr(ev, 'tempo_relativo') and tarefa.tempo_execucao == int(ev.tempo_relativo)
        ]

        bloqueou = False
        for evento in eventos_a_disparar:
            try:
                # Executa o evento
                resultado = evento.executar(self, tarefa)

                # Remove o evento processado para evitar loop infinito
                if evento in tarefa.eventos:
                    tarefa.eventos.remove(evento)

                if resultado:
                    if tarefa.id not in self.eventos_pendentes:
                        self.eventos_pendentes[tarefa.id] = []
                    self.eventos_pendentes[tarefa.id].append({
                        'tempo': tempo_atual,
                        'tipo': evento.tipo,
                        'resultado': resultado
                    })
                
                # Se o evento causou bloqueio (I/O ou Mutex), paramos de processar
                if tarefa.estado == TaskState.BLOQUEADO:
                    bloqueou = True
                    break

            except Exception as e:
                print(f"Aviso: Erro ao processar evento {evento.tipo} da tarefa {tarefa.id}: {e}")

        return bloqueou

    # Execução de um ciclo
    def executar_tick(self):
        tempo_atual = self.clock.get_tempo()

        # 1. Desbloquear tarefas com I/O completo
        self.verificar_io_conclusoes()

        # 2. Verificar chegada de novas tarefas
        self.verificar_novas_tarefas()

        # Identifica tarefa atualmente executando (para preempção)
        tarefa_executando = None
        for t in self.scheduler.fila_prontos:
            if t.estado == TaskState.EXECUTANDO:
                tarefa_executando = t
                break
        
        # 3. Aplicar envelhecimento
        if hasattr(self.scheduler, 'aplicar_envelhecimento'):
            self.scheduler.aplicar_envelhecimento()

        # 4. Selecionar próxima tarefa
        tarefa = self.scheduler.selecionar_proxima_tarefa()
        
        # Preempção
        if tarefa_executando and tarefa != tarefa_executando:
            tarefa_executando.preemptar()
        
        if tarefa:
            if tarefa.estado == TaskState.PRONTO:
                tarefa.iniciar()

            # Lógica Correta (16 ticks): Processar eventos ANTES de executar
            bloqueou = self.processar_eventos_tarefa(tarefa, tempo_atual)

            if bloqueou:
                # Se bloqueou, remove do scheduler e NÃO executa
                self.scheduler.remover_tarefa(tarefa)
                self.historico_execucao.append((tempo_atual, None))
            else:
                # Se NÃO bloqueou, executa normalmente
                terminou = tarefa.executar(tempo_atual)
                self.historico_execucao.append((tempo_atual, tarefa.id))

                if terminou:
                    self.scheduler.remover_tarefa(tarefa)
        else:
            # Nenhuma tarefa disponível (CPU ociosa)
            self.historico_execucao.append((tempo_atual, None))

        # Atualizar bloqueios legados e avançar o relógio
        self._update_blocked_tasks()
        self.clock.tick()

    # --- Bloqueio e Mutex API ---
    def bloquear_tarefa(self, task_id: str, duracao: int):
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task: return False

        task.bloquear()
        if task in self.scheduler.fila_prontos:
            self.scheduler.remover_tarefa(task)

        self.io_manager.iniciar_io(task_id, duracao, self.clock.get_tempo())
        self._blocked[task_id] = {'tipo': 'io', 'remaining': int(duracao), 'mutex_id': None}
        return True

    def block_task(self, task_id: str, duracao: int): return self.bloquear_tarefa(task_id, duracao)

    def solicitar_mutex(self, task_id: str, mutex_id: str) -> bool:
        concedido = self.mutex_manager.solicitar_mutex(mutex_id, task_id)

        if not concedido:
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task:
                task.bloquear()
                if task in self.scheduler.fila_prontos:
                    self.scheduler.remover_tarefa(task)
                self._blocked[task_id] = {'tipo': 'mutex', 'remaining': None, 'mutex_id': mutex_id}

        self._sincronizar_legado()
        return concedido

    def request_mutex(self, task_id: str, mutex_id: str) -> bool: return self.solicitar_mutex(task_id, mutex_id)

    def liberar_mutex(self, task_id: str, mutex_id: str) -> bool:
        try:
            next_task_id = self.mutex_manager.liberar_mutex(mutex_id, task_id)
            if next_task_id:
                next_task = next((t for t in self.tasks if t.id == next_task_id), None)
                if next_task:
                    next_task.desbloquear()
                    if next_task_id in self._blocked: self._blocked.pop(next_task_id, None)
                    if next_task not in self.scheduler.fila_prontos:
                        self.scheduler.adicionar_tarefa(next_task)

            self._sincronizar_legado()
            return True
        except ValueError:
            return False

    def release_mutex(self, task_id: str, mutex_id: str) -> bool: return self.liberar_mutex(task_id, mutex_id)

    def _sincronizar_legado(self):
        self.mutexes = {mid: self.mutex_manager.mutexes.get(mid, {}).get('dono') for mid in self.mutex_manager.mutexes}
        self._mutex_queues = {mid: list(self.mutex_manager.mutexes.get(mid, {}).get('fila_espera', [])) for mid in self.mutex_manager.mutexes}

    def _update_blocked_tasks(self):
        pass

    def tem_tarefas_pendentes(self):
        return any(t.estado != TaskState.TERMINADO for t in self.tasks)

    # Execução completa
    def executar(self, tempo_max=None, log=False):
        self.clock.reset()
        while self.tem_tarefas_pendentes():
            if tempo_max is not None and self.clock.get_tempo() >= tempo_max: break
            if log: print(f"[t={self.clock.get_tempo()}] Executando tick...")
            self.executar_tick()
        self._processar_historico_gantt()
        return self.historico_execucao
    
    def executar_completo(self):
        start_time = time.time()
        self.clock.reset()
        while self.tem_tarefas_pendentes():
            self.executar_tick()
        end_time = time.time()
        
        estatisticas = {
            'tempo_total_ticks': self.clock.get_tempo(),
            'tempo_execucao_real_ms': (end_time - start_time) * 1000,
            'historico_execucao': self.historico_execucao
        }
        self._processar_historico_gantt()
        return estatisticas

    def _processar_historico_gantt(self):
        """
        Processa o histórico de execução e adiciona intervalos ao gantt.
        """
        self.gantt.intervalos = [] 

        if not self.historico_execucao: return
        
        cores = {task.id: task.cor for task in self.tasks}
        intervalo_atual = None
        
        for tempo, task_id in self.historico_execucao:
            if task_id is None:
                if intervalo_atual:
                    self.gantt.adicionar_intervalo(intervalo_atual['task_id'], intervalo_atual['inicio'], tempo, intervalo_atual['cor'])
                    intervalo_atual = None
            else:
                if intervalo_atual and intervalo_atual['task_id'] == task_id: pass
                else:
                    if intervalo_atual:
                        self.gantt.adicionar_intervalo(intervalo_atual['task_id'], intervalo_atual['inicio'], tempo, intervalo_atual['cor'])
                    intervalo_atual = {'task_id': task_id, 'inicio': tempo, 'cor': cores.get(task_id, '#999999')}
        
        if intervalo_atual:
            self.gantt.adicionar_intervalo(intervalo_atual['task_id'], intervalo_atual['inicio'], self.clock.get_tempo(), intervalo_atual['cor'])

    def _exibir_estado_sistema(self):
        tempo = self.clock.get_tempo()
        exec_task = next((t for t in self.tasks if t.estado == TaskState.EXECUTANDO), None)
        exec_str = f"Task {exec_task.id}" if exec_task else "IDLE"
        prontos = [t.id for t in self.scheduler.fila_prontos if t.estado == TaskState.PRONTO]
        
        bloqueados = [t.id for t in self.tasks if t.estado == TaskState.BLOQUEADO]
        mutex_info = ""
        if self.mutex_manager.mutexes:
            donos = [f"{mid}:{info['dono']}" for mid, info in self.mutex_manager.mutexes.items() if info['dono']]
            if donos: mutex_info = f" | Mutex: {donos}"

        print(f"[Tick {tempo}] Exec: {exec_str} | Prontos: {prontos} | Bloq: {bloqueados}{mutex_info}")

    def _exibir_info_tarefa(self, task_id):
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            print(f"Tarefa '{task_id}' não encontrada.")
            return
        print(f"\n=== Tarefa {task.id} ===")
        print(f"Estado: {task.estado} | Prioridade: {task.prioridade} | Restante: {task.tempo_restante}")
        if hasattr(task, 'eventos'):
            print(f"Eventos pendentes: {len(task.eventos)}")

    def _exibir_status_geral(self):
        print(f"\n=== Status do Sistema (Tick {self.clock.get_tempo()}) ===")
        print(f"Algoritmo: {self.scheduler.__class__.__name__}")

    def executar_passo_a_passo(self):
        """
        Executa simulação em modo passo-a-passo com histórico (Undo/Redo).
        """
        self.carregar_tarefas(self.tasks)
        self.clock.reset()
        
        # Salva estado inicial
        self.history_manager.limpar_historico()
        self.history_manager.salvar_snapshot(self)
        
        modo_continue = False
        
        print("\n=== Modo Passo-a-Passo (Com Histórico) ===")
        print("Comandos: Enter (próximo) | p (voltar) | g (gantt) | status | q (sair)")
        print("=" * 60 + "\n")
        
        while True:
            if not modo_continue:
                self._exibir_estado_sistema()
                
                try:
                    cmd_raw = input(f"[Tick {self.clock.get_tempo()}] > ").strip().lower()
                except EOFError: break
                
                cmd = cmd_raw if cmd_raw else 'next'
                
                if cmd in ['q', 'quit']: break
                
                # --- VOLTAR ---
                if cmd in ['p', 'prev', 'back']:
                    estado = self.history_manager.retroceder()
                    if estado:
                        self._restaurar_estado(estado)
                        print(f"⏪ Voltou para Tick {self.clock.get_tempo()}")
                        # Atualiza histórico visual
                        self.historico_execucao = [h for h in self.historico_execucao if h[0] < self.clock.get_tempo()]
                    else:
                        print("⚠️ Início do histórico.")
                    continue

                # --- GANTT ---
                if cmd in ['g', 'gantt']:
                    self._processar_historico_gantt()
                    self.gantt.exibir_terminal()
                    continue

                if cmd == 'status':
                    self._exibir_status_geral()
                    continue
                
                if cmd.startswith('info '):
                    try:
                        tid = cmd_raw.split()[1]
                        self._exibir_info_tarefa(tid)
                    except IndexError: print("Uso: info <id>")
                    continue

                if cmd == 'continue':
                    modo_continue = True

            # Verifica fim
            if not self.tem_tarefas_pendentes():
                print("\n🏁 Simulação Concluída!")
                self._exibir_status_geral()
                if modo_continue: 
                    modo_continue = False
                    print("Use 'p' para voltar ou 'q' para sair.")
                    continue
                
                # Fim no modo passo-a-passo
                c = input("Fim. (p)ara voltar, (g)antt ou (q) para sair > ").strip().lower()
                if c in ['p', 'prev']:
                    estado = self.history_manager.retroceder()
                    if estado:
                        self._restaurar_estado(estado)
                        print(f"⏪ Voltou para Tick {self.clock.get_tempo()}")
                        continue
                elif c in ['g', 'gantt']:
                    self._processar_historico_gantt()
                    self.gantt.exibir_terminal()
                    continue
                else:
                    break

            # Avançar
            self.executar_tick()
            self.history_manager.salvar_snapshot(self)

        self._processar_historico_gantt() 

        return self.historico_execucao

    def _restaurar_estado(self, state_dict):
        """
        Restaura o estado completo do simulador a partir de um snapshot.
        CORRIGIDO: Trata corretamente Mutexes e clona Eventos.
        """
        import copy
        self.clock.tempo_atual = state_dict['tempo']
        
        # 1. Restaura Tarefas
        tasks_data = state_dict['tasks_state']
        for task in self.tasks:
            if task.id in tasks_data:
                d = tasks_data[task.id]
                task.estado = d['estado']
                task.tempo_restante = d['tempo_restante']
                task.tempo_execucao = d['tempo_execucao']
                task.tempo_inicio = d['tempo_inicio']
                task.tempo_fim = d['tempo_fim']
                task.prioridade = d['prioridade']
                
                if 'eventos' in d:
                    task.eventos = copy.deepcopy(d['eventos'])

        # 2. Restaura Scheduler
        sched_data = state_dict['scheduler_state']
        self.scheduler.fila_prontos = []
        for tid in sched_data['fila_prontos']:
            # Reencontra o objeto tarefa real pelo ID
            t = next((x for x in self.tasks if x.id == tid), None)
            if t: self.scheduler.fila_prontos.append(t)
            
        # Restaura prioridades dinâmicas (para PRIOPEnv)
        if 'prioridades_dinamicas' in sched_data and hasattr(self.scheduler, 'prioridades_dinamicas'):
            self.scheduler.prioridades_dinamicas = copy.deepcopy(sched_data['prioridades_dinamicas'])

        # 3. Restaura IO
        io_state = state_dict['io_state']
        self._blocked = io_state['blocked'] # Legado
        if 'operacoes' in io_state:
            self.io_manager.operacoes = io_state['operacoes'] # Novo Manager
            
        # 4. Restaura Mutexes (Correção do TypeError)
        mutex_state = state_dict['mutex_state']
        self.mutexes = mutex_state['mutexes']
        self._mutex_queues = mutex_state.get('mutex_queues', {})
        
        self.mutex_manager.limpar()
        # Reconstrói o estado interno do MutexManager
        for mid, dono in self.mutexes.items():
            self.mutex_manager.mutexes[mid] = {
                'dono': dono,
                'fila_espera': list(self._mutex_queues.get(mid, []))
            }