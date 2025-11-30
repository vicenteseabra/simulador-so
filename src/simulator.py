import time
import copy
from src.clock import Clock
from src.task import Task, TaskState
from src.gantt import GanttChart
from src.mutex_manager import MutexManager
from src.io_manager import IOManager
from src.history import HistoryManager


class Simulator:
    """
    Classe principal que orquestra a simulação do sistema operacional.
    Controla o relógio, execução de tarefas, recursos e interface interativa.
    """

    def __init__(self, scheduler):
        self.clock = Clock()
        self.clock.reset()
        self.scheduler = scheduler
        self.tasks = []
        self.historico_execucao = []
        
        # Define o tipo de escalonamento para o título do gráfico
        tipo_algo = getattr(scheduler, 'tipo_escalonamento', scheduler.__class__.__name__)
        self.gantt = GanttChart(tipo_escalonamento=tipo_algo)

        # Gerenciadores de Recursos e Histórico
        self.mutex_manager = MutexManager()
        self.io_manager = IOManager()
        self.history_manager = HistoryManager()

        # Controle interno
        self.eventos_pendentes = {}
        
        # Estruturas de compatibilidade (Legado para sincronização)
        self._blocked = {}
        self.mutexes = {}
        self._mutex_queues = {}

    # --- Inicialização e Controle ---

    def carregar_tarefas(self, tasks):
        """Carrega tarefas e reseta o estado da simulação."""
        self.tasks = tasks
        for task in self.tasks:
            task.estado = TaskState.NOVO
            task.tempo_execucao = 0
            task.tempo_restante = task.duracao
            task.tempo_inicio = None
            task.tempo_fim = None
        
        # Limpa gerenciadores
        self.io_manager.limpar()
        self.mutex_manager.limpar()
        self.history_manager.limpar_historico()

    def verificar_novas_tarefas(self):
        """Admite tarefas no sistema (NOVO -> PRONTO)."""
        tempo_atual = self.clock.get_tempo()
        for task in self.tasks:
            if task.estado == TaskState.NOVO and task.ingresso == tempo_atual:
                task.admitir()
                self.scheduler.adicionar_tarefa(task)
                self.gantt.registrar_ingresso_fila(task.id, tempo_atual)

    def verificar_io_conclusoes(self):
        """Verifica e desbloqueia tarefas que terminaram I/O."""
        tempo_atual = self.clock.get_tempo()
        conclusoes = self.io_manager.verificar_conclusoes(tempo_atual)

        for task_id in conclusoes:
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task and task.estado == TaskState.BLOQUEADO:
                task.desbloquear()
                # Remove do legado
                if task_id in self._blocked:
                    self._blocked.pop(task_id, None)
                # Adiciona ao scheduler se não estiver lá
                if task not in self.scheduler.fila_prontos:
                    self.scheduler.adicionar_tarefa(task)

    def processar_eventos_tarefa(self, tarefa, tempo_atual):
        """
        Processa eventos da tarefa para o tick atual.
        Retorna True se a tarefa foi BLOQUEADA.
        """
        if not hasattr(tarefa, 'eventos') or not tarefa.eventos:
            return False

        # Filtra eventos que devem ocorrer exatamente agora (tempo relativo)
        eventos_a_disparar = [
            ev for ev in list(tarefa.eventos)
            if hasattr(ev, 'tempo_relativo') and tarefa.tempo_execucao == int(ev.tempo_relativo)
        ]

        bloqueou = False
        for evento in eventos_a_disparar:
            try:
                # Executa o evento (IO, Mutex Lock/Unlock)
                resultado = evento.executar(self, tarefa)

                # CORREÇÃO: Remove o evento da lista para evitar execução repetida
                if evento in tarefa.eventos:
                    tarefa.eventos.remove(evento)

                # Log para debug
                if resultado:
                    if tarefa.id not in self.eventos_pendentes:
                        self.eventos_pendentes[tarefa.id] = []
                    self.eventos_pendentes[tarefa.id].append({
                        'tempo': tempo_atual,
                        'tipo': evento.tipo,
                        'resultado': resultado
                    })
                
                # Se o evento causou bloqueio, interrompe o processamento
                if tarefa.estado == TaskState.BLOQUEADO:
                    bloqueou = True
                    break

            except Exception as e:
                print(f"Aviso: Erro ao processar evento {evento.tipo} da tarefa {tarefa.id}: {e}")

        return bloqueou

    # --- Motor Principal (Tick) ---

    def executar_tick(self):
        """Executa um ciclo lógico da simulação."""
        tempo_atual = self.clock.get_tempo()

        # 1. Desbloqueios de I/O
        self.verificar_io_conclusoes()

        # 2. Entrada de novas tarefas
        self.verificar_novas_tarefas()

        # Identifica tarefa anterior (para lógica de preempção)
        tarefa_executando = next((t for t in self.scheduler.fila_prontos if t.estado == TaskState.EXECUTANDO), None)
        
        # 3. Aging (se aplicável)
        if hasattr(self.scheduler, 'aplicar_envelhecimento'):
            self.scheduler.aplicar_envelhecimento()

        # 4. Seleção da próxima tarefa
        tarefa = self.scheduler.selecionar_proxima_tarefa()
        
        # Preempção se mudou a tarefa
        if tarefa_executando and tarefa != tarefa_executando:
            tarefa_executando.preemptar()
        
        if tarefa:
            if tarefa.estado == TaskState.PRONTO:
                tarefa.iniciar()

            # LÓGICA CRÍTICA: Processar eventos ANTES de computar execução
            # Se a tarefa pedir bloqueio no tempo X, ela não roda no tick X.
            bloqueou = self.processar_eventos_tarefa(tarefa, tempo_atual)

            if bloqueou:
                # Se bloqueou, sai da CPU imediatamente
                self.scheduler.remover_tarefa(tarefa)
                self.historico_execucao.append((tempo_atual, None))
            else:
                # Se não bloqueou, executa 1 tick
                terminou = tarefa.executar(tempo_atual)
                self.historico_execucao.append((tempo_atual, tarefa.id))

                if terminou:
                    self.scheduler.remover_tarefa(tarefa)
        else:
            # CPU Ociosa
            self.historico_execucao.append((tempo_atual, None))

        # Atualiza estruturas legadas e avança relógio
        self._update_blocked_tasks()
        self.clock.tick()

    # --- Interface para Eventos (Callbacks) ---

    def bloquear_tarefa(self, task_id: str, duracao: int):
        """Inicia I/O."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task: return False

        task.bloquear()
        # Remove do scheduler se estiver lá
        if task in self.scheduler.fila_prontos:
            self.scheduler.remover_tarefa(task)

        self.io_manager.iniciar_io(task_id, duracao, self.clock.get_tempo())
        # Compatibilidade
        self._blocked[task_id] = {'tipo': 'io', 'remaining': int(duracao), 'mutex_id': None}
        return True

    def block_task(self, t, d): return self.bloquear_tarefa(t, d)

    def solicitar_mutex(self, task_id: str, mutex_id: str) -> bool:
        """Tenta adquirir mutex."""
        concedido = self.mutex_manager.solicitar_mutex(mutex_id, task_id)

        if not concedido:
            # Se falhou, bloqueia a tarefa
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task:
                task.bloquear()
                if task in self.scheduler.fila_prontos:
                    self.scheduler.remover_tarefa(task)
                self._blocked[task_id] = {'tipo': 'mutex', 'remaining': None, 'mutex_id': mutex_id}

        self._sincronizar_legado()
        return concedido

    def request_mutex(self, t, m): return self.solicitar_mutex(t, m)

    def liberar_mutex(self, task_id: str, mutex_id: str) -> bool:
        """Libera mutex e acorda o próximo da fila."""
        try:
            novo_dono = self.mutex_manager.liberar_mutex(mutex_id, task_id)
            if novo_dono:
                # Desbloqueia o novo dono
                t = next((t for t in self.tasks if t.id == novo_dono), None)
                if t:
                    t.desbloquear()
                    if novo_dono in self._blocked:
                        self._blocked.pop(novo_dono, None)
                    if t not in self.scheduler.fila_prontos:
                        self.scheduler.adicionar_tarefa(t)

            self._sincronizar_legado()
            return True
        except ValueError:
            return False

    def release_mutex(self, t, m): return self.liberar_mutex(t, m)

    def _sincronizar_legado(self):
        """Mantém dicionários antigos sincronizados para evitar quebra de código legado."""
        self.mutexes = {mid: self.mutex_manager.mutexes.get(mid, {}).get('dono') 
                       for mid in self.mutex_manager.mutexes}
        self._mutex_queues = {mid: list(self.mutex_manager.mutexes.get(mid, {}).get('fila_espera', [])) 
                             for mid in self.mutex_manager.mutexes}

    def _update_blocked_tasks(self):
        pass # IOManager cuida do I/O, MutexManager cuida do Mutex.

    def tem_tarefas_pendentes(self):
        return any(t.estado != TaskState.TERMINADO for t in self.tasks)

    # --- Modos de Execução ---

    def executar(self, tempo_max=None, log=False):
        """Modo Backend (Sem interface)."""
        self.clock.reset()
        while self.tem_tarefas_pendentes():
            if tempo_max and self.clock.get_tempo() >= tempo_max:
                break
            if log: print(f"[t={self.clock.get_tempo()}] Executando...")
            self.executar_tick()
        
        self._processar_historico_gantt()
        return self.historico_execucao
    
    def executar_completo(self):
        """Modo Completo (Retorna estatísticas)."""
        start = time.time()
        self.clock.reset()
        while self.tem_tarefas_pendentes():
            self.executar_tick()
        end = time.time()
        
        self._processar_historico_gantt()
        
        return {
            'tempo_total_ticks': self.clock.get_tempo(),
            'tempo_execucao_real_ms': (end - start) * 1000,
            'historico_execucao': self.historico_execucao
        }

    def _processar_historico_gantt(self):
        """Converte histórico de execução em intervalos para o gráfico."""
        # Limpa dados anteriores para permitir "redesenho" ao voltar no tempo
        self.gantt.intervalos = [] 
        
        if not self.historico_execucao: return
        
        cores = {t.id: t.cor for t in self.tasks}
        intervalo_atual = None
        
        for tempo, task_id in self.historico_execucao:
            if task_id is None:
                if intervalo_atual:
                    self.gantt.adicionar_intervalo(
                        intervalo_atual['tid'], intervalo_atual['ini'], tempo, intervalo_atual['cor'])
                    intervalo_atual = None
            else:
                if intervalo_atual and intervalo_atual['tid'] == task_id:
                    pass
                else:
                    if intervalo_atual:
                        self.gantt.adicionar_intervalo(
                            intervalo_atual['tid'], intervalo_atual['ini'], tempo, intervalo_atual['cor'])
                    intervalo_atual = {'tid': task_id, 'ini': tempo, 'cor': cores.get(task_id, '#999')}
        
        if intervalo_atual:
            self.gantt.adicionar_intervalo(
                intervalo_atual['tid'], intervalo_atual['ini'], self.clock.get_tempo(), intervalo_atual['cor'])

    # --- UI / Visualização ---

    def _obter_motivo_bloqueio(self, task):
        if task.estado != TaskState.BLOQUEADO: return ""
        if self.io_manager.tem_io_ativo(task.id): return " (IO)"
        for mid, d in self.mutex_manager.mutexes.items():
            if task.id in d['fila_espera']: return f" (MUTEX:{mid})"
        return " (Bloq)"

    def _exibir_estado_sistema(self):
        tempo = self.clock.get_tempo()
        
        # Executando
        exec_t = next((t for t in self.tasks if t.estado == TaskState.EXECUTANDO), None)
        if exec_t:
            mtx = [m for m, d in self.mutex_manager.mutexes.items() if d['dono'] == exec_t.id]
            extra = f" [MUTEX:{','.join(mtx)}]" if mtx else ""
            exec_str = f"Task {exec_t.id}{extra}"
        else:
            exec_str = "IDLE"
            
        prontos = [t.id for t in self.scheduler.fila_prontos if t.estado == TaskState.PRONTO]
        
        bloq = []
        for t in self.tasks:
            if t.estado == TaskState.BLOQUEADO:
                bloq.append(f"{t.id}{self._obter_motivo_bloqueio(t)}")
        
        print("-" * 70)
        print(f"[Tick {tempo}] Exec: {exec_str} | Prontos: {prontos} | Bloq: {bloq}")

    def _exibir_ajuda(self):
        print("\n--- Comandos ---")
        print(" n, Enter : Próximo tick")
        print(" p        : Voltar tick")
        print(" jump <N> : Pular para tick N")
        print(" g        : Gráfico Gantt")
        print(" s        : Status detalhado")
        print(" m        : Tabela Mutex")
        print(" i        : Tabela I/O")
        print(" c        : Continuar até o fim")
        print(" q        : Sair")

    def _exibir_tabela_mutex(self):
        print("\n--- Mutexes ---")
        if not self.mutex_manager.mutexes: print("Nenhum.")
        for mid, d in self.mutex_manager.mutexes.items():
            print(f" {mid}: Dono={d['dono'] or 'Livre'}, Fila={d['fila_espera']}")
        print()

    def _exibir_tabela_io(self):
        print("\n--- I/O Ativo ---")
        ops = self.io_manager.operacoes_ativas()
        if not ops: print("Nenhum.")
        for tid, fim in ops:
            print(f" {tid}: Termina em {fim}")
        print()

    def executar_passo_a_passo(self):
        """Modo Interativo Completo."""
        self.carregar_tarefas(self.tasks)
        self.clock.reset()
        self.history_manager.limpar_historico()
        self.history_manager.salvar_snapshot(self)
        
        modo_continue = False
        print("\n=== Modo Passo-a-Passo ===")
        print("Digite 'h' para ajuda. Enter para avançar.")
        
        while True:
            if not modo_continue:
                self._exibir_estado_sistema()
                try:
                    linha = input("> ").strip().lower()
                except EOFError: break
                
                partes = linha.split()
                cmd = partes[0] if partes else 'next'
                arg = partes[1] if len(partes) > 1 else None

                if cmd in ['q', 'quit']: break
                if cmd in ['h', 'help']: self._exibir_ajuda(); continue
                
                # Comandos de Inspeção (Não avançam tempo)
                if cmd in ['s', 'status']: continue 
                if cmd in ['m', 'mutex']: self._exibir_tabela_mutex(); continue
                if cmd in ['i', 'io']: self._exibir_tabela_io(); continue
                if cmd in ['g', 'gantt']: 
                    self._processar_historico_gantt()
                    self.gantt.exibir_terminal()
                    continue

                # Navegação
                if cmd in ['p', 'prev']:
                    st = self.history_manager.retroceder()
                    if st:
                        self._restaurar_estado(st)
                        self.historico_execucao = [h for h in self.historico_execucao if h[0] < self.clock.get_tempo()]
                        print("⏪")
                    else: print("⚠️ Início.")
                    continue

                if cmd == 'jump' and arg and arg.isdigit():
                    alvo = int(arg)
                    now = self.clock.get_tempo()
                    if alvo < now:
                        while self.clock.get_tempo() > alvo:
                            st = self.history_manager.retroceder()
                            if not st: break
                            self._restaurar_estado(st)
                        self.historico_execucao = [h for h in self.historico_execucao if h[0] < self.clock.get_tempo()]
                    elif alvo > now:
                        print("Avançando...")
                        while self.clock.get_tempo() < alvo and self.tem_tarefas_pendentes():
                            self.executar_tick()
                            self.history_manager.salvar_snapshot(self)
                    continue

                if cmd in ['c', 'continue']: modo_continue = True

            if not self.tem_tarefas_pendentes():
                print("\n🏁 Fim da Simulação!")
                if modo_continue:
                    modo_continue = False
                    print("Use 'p' para voltar.")
                    continue
                c = input("Fim. (p)rev, (g)antt, (q)uit > ").lower()
                if c in ['p', 'prev']:
                    st = self.history_manager.retroceder()
                    if st:
                        self._restaurar_estado(st)
                        self.historico_execucao = [h for h in self.historico_execucao if h[0] < self.clock.get_tempo()]
                    continue
                elif c in ['g', 'gantt']:
                    self._processar_historico_gantt()
                    self.gantt.exibir_terminal()
                    continue
                else: break

            self.executar_tick()
            self.history_manager.salvar_snapshot(self)

        self._processar_historico_gantt()
        return self.historico_execucao

    def _restaurar_estado(self, state_dict):
        """Restaura estado do snapshot (cópia segura)."""
        self.clock.tempo_atual = state_dict['tempo']
        
        # Tarefas + Eventos (Cópia profunda)
        t_data = state_dict['tasks_state']
        for t in self.tasks:
            if t.id in t_data:
                d = t_data[t.id]
                t.estado = d['estado']
                t.tempo_restante = d['tempo_restante']
                t.tempo_execucao = d['tempo_execucao']
                t.tempo_inicio = d['tempo_inicio']
                t.tempo_fim = d['tempo_fim']
                t.prioridade = d['prioridade']
                if 'eventos' in d:
                    t.eventos = copy.deepcopy(d['eventos'])
                else:
                    t.eventos = []

        # Scheduler + Prioridades
        s_data = state_dict['scheduler_state']
        self.scheduler.fila_prontos = []
        for tid in s_data['fila_prontos']:
            task = next((x for x in self.tasks if x.id == tid), None)
            if task: self.scheduler.fila_prontos.append(task)
            
        if 'prioridades_dinamicas' in s_data and hasattr(self.scheduler, 'prioridades_dinamicas'):
            self.scheduler.prioridades_dinamicas = copy.deepcopy(s_data['prioridades_dinamicas'])

        # Mutex e IO (Reconstrução)
        mutex_st = state_dict['mutex_state']
        self.mutexes = mutex_st['mutexes']
        self._mutex_queues = mutex_st.get('mutex_queues', {})
        
        self.mutex_manager.limpar()
        for mid, dono in self.mutexes.items():
            self.mutex_manager.mutexes[mid] = {
                'dono': dono,
                'fila_espera': list(self._mutex_queues.get(mid, []))
            }
            
        io_st = state_dict['io_state']
        self._blocked = io_st['blocked']
        if 'operacoes' in io_st:
            self.io_manager.operacoes = copy.deepcopy(io_st['operacoes'])