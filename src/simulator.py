import time
from clock import Clock
from task import Task, TaskState
from gantt import GanttChart


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
        self.gantt = GanttChart()
        self.fila_io = [] # Fila de tarefas bloqueadas por E/S

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
            if tarefa.estado == TaskState.PRONTO:
                tarefa.iniciar()

            # 1. Verifica se há um evento de E/S para o tempo atual
            # 1. Verifica se há um evento de E/S para o tempo de execução atual da tarefa
            # O evento IO:X-Y deve ocorrer *após* o X-ésimo tick de execução.
            # tempo_execucao é o número de ticks que a tarefa já executou.
            # Se tempo_execucao é 3, a tarefa está prestes a executar seu 4º tick.
            # Um evento em tempo=4 deve ser verificado *antes* da execução do 4º tick.
            # A verificação deve ser feita para o tempo de execução que será atingido *após* este tick.
            # Se a tarefa executou 3 ticks (tempo_execucao=3), o próximo tick a ser executado será o 4º.
            # O evento IO:4-2 deve ser verificado quando tempo_execucao == 3.
            # O valor de 'tempo' no evento IO é o tempo de execução *relativo* na tarefa.
            # Se a tarefa executou 'tempo_execucao' ticks, ela está prestes a executar o 'tempo_execucao + 1' tick.
            evento_io = next((e for e in tarefa.eventos 
                             if e["tipo"] == "IO" and e["tempo"] == tarefa.tempo_execucao), None)
            
            if evento_io:
                # Executa a tarefa por 1 tick ANTES de verificar o evento de I/O
                tarefa.executar(tempo_atual)
                self.historico_execucao.append((tempo_atual, tarefa.id))
            else:
                tarefa.executar(tempo_atual)
                self.historico_execucao.append((tempo_atual, tarefa.id))

            # 2. Verifica se um evento de I/O deve ocorrer *após* a execução
            # O evento IO:X-Y ocorre no final do X-ésimo tick (quando tempo_execucao == X)
            evento_io = next((e for e in tarefa.eventos 
                             if e['tipo'] == 'IO' and e['tempo'] == tarefa.tempo_execucao), None)

            if evento_io:
                # Bloqueia a tarefa para E/S
                tarefa.bloquear()
                self.scheduler.remover_tarefa(tarefa)
                # tempo_fim é o tick em que a tarefa será desbloqueada (tempo_atual + duracao)
                self.fila_io.append({
                    'tarefa': tarefa,
                    'tempo_fim': tempo_atual + evento_io['duracao']
                })
                # Remove o evento para não ser processado novamente
                # É importante que o evento seja removido, senão a tarefa pode bloquear novamente.
                tarefa.eventos.remove(evento_io)
            
            # 3. Verifica finalização (só se não foi bloqueada)
            if tarefa.estado == TaskState.TERMINADO:
                self.scheduler.remover_tarefa(tarefa)
        else:
            # Nenhuma tarefa disponível (CPU ociosa)
            self.historico_execucao.append((tempo_atual, None))

        # 4. Trata a fila de E/S
        self._tratar_fila_io(tempo_atual)

        # Avança o relógio
        self.clock.tick()

    # Controle de término
    def tem_tarefas_pendentes(self):
        """
        Retorna True enquanto existir alguma tarefa não terminada (NOVO, PRONTO, EXECUTANDO, BLOQUEADO).
        """
        return any(t.estado != TaskState.TERMINADO for t in self.tasks) or len(self.fila_io) > 0

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
        
        # Processa histórico para preencher o gantt
        self._processar_historico_gantt()
        
        return self.historico_execucao
    
    def executar_completo(self):
        """
        Executa a simulação completa (sem logs) e retorna estatísticas finais.
        Implementação da TASK 2.3.
        """
        start_time = time.time()
        
        self.clock.reset()

        while self.tem_tarefas_pendentes():
            self.executar_tick()

        end_time = time.time()
        
        tempo_execucao_real_ms = (end_time - start_time) * 1000
        tempo_total_ticks = self.clock.get_tempo()

        estatisticas = {
            'tempo_total': tempo_total_ticks,
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
        
        print("\n=== Simulação Concluída ===")
        self._exibir_status_geral()
        return self.historico_execucao


    def _tratar_fila_io(self, tempo_atual):
        """
        Verifica tarefas na fila de E/S e as move para a fila de prontos
        quando o tempo de E/S termina.
        """
        tarefas_desbloqueadas = []
        
        # Filtra tarefas que terminaram a E/S
        # O desbloqueio ocorre no início do tick em que item['tempo_fim'] é igual ao tempo_atual.
        for item in self.fila_io[:]: # Itera sobre uma cópia
            if item['tempo_fim'] == tempo_atual:
                tarefas_desbloqueadas.append(item['tarefa'])
        
        # Remove da fila de E/S e desbloqueia
        for tarefa in tarefas_desbloqueadas:
            # Remove da fila_io
            self.fila_io.remove(next(i for i in self.fila_io if i['tarefa'] == tarefa))
            
            # Desbloqueia e adiciona ao escalonador
            if tarefa.estado == TaskState.BLOQUEADO:
                tarefa.desbloquear()
                self.scheduler.adicionar_tarefa(tarefa)
                self.gantt.registrar_ingresso_fila(tarefa.id, tempo_atual) # Entra na fila no tick atual (tempo_atual)
