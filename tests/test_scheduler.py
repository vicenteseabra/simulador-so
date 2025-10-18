"""
Testes unitários para as classes Task, TCB e funcionalidades do escalonador.

Este módulo contém testes abrangentes para validar o comportamento
das classes de estrutura de dados do simulador de SO.

"""

from src.task import TCB, Task, TaskState


class TestCase:
    """Classe base para casos de teste."""
    
    def __init__(self):
        self.test_count = 0
        self.failures = 0
        self.errors = []
    
    def assertEqual(self, a, b, msg=None):
        """Verifica se dois valores são iguais."""
        if a != b:
            error_msg = msg or "Expected {} but got {}".format(repr(b), repr(a))
            self.errors.append(error_msg)
            raise AssertionError(error_msg)
    
    def assertIsNone(self, obj, msg=None):
        """Verifica se objeto é None."""
        if obj is not None:
            error_msg = msg or "Expected None but got {}".format(repr(obj))
            self.errors.append(error_msg)
            raise AssertionError(error_msg)
    
    def assertIsNotNone(self, obj, msg=None):
        """Verifica se objeto não é None."""
        if obj is None:
            error_msg = msg or "Expected not None but got None"
            self.errors.append(error_msg)
            raise AssertionError(error_msg)
    
    def assertIn(self, item, container, msg=None):
        """Verifica se item está no container."""
        if item not in container:
            error_msg = msg or "{} not found in {}".format(repr(item), repr(container))
            self.errors.append(error_msg)
            raise AssertionError(error_msg)
    
    def assertRaises(self, exception_class):
        """Context manager para verificar se exceção é levantada."""
        return _AssertRaisesContext(exception_class)
    
    def assertIsInstance(self, obj, cls, msg=None):
        """Verifica se objeto é instância de uma classe."""
        if not isinstance(obj, cls):
            error_msg = msg or "{} is not an instance of {}".format(repr(obj), cls.__name__)
            self.errors.append(error_msg)
            raise AssertionError(error_msg)
    
    def assertAlmostEqual(self, a, b, places=7, msg=None):
        """Verifica se dois números são aproximadamente iguais."""
        if abs(a - b) > 10**(-places):
            error_msg = msg or "{} != {} within {} decimal places".format(a, b, places)
            self.errors.append(error_msg)
            raise AssertionError(error_msg)
    
    def run_test(self, test_method):
        """Executa um método de teste."""
        self.test_count += 1
        try:
            if hasattr(self, 'setUp'):
                self.setUp()
            test_method()
            print("PASS: {}".format(test_method.__name__))
        except Exception as e:
            self.failures += 1
            print("FAIL: {} - {}".format(test_method.__name__, str(e)))
    
    def run_all_tests(self):
        """Executa todos os métodos de teste da classe."""
        test_methods = [getattr(self, method) for method in dir(self) 
                       if method.startswith('test_') and callable(getattr(self, method))]
        
        print("\n=== {} ===".format(self.__class__.__name__))
        for test_method in test_methods:
            self.run_test(test_method)
        
        print("Ran {} tests, {} failures".format(self.test_count, self.failures))
        return self.failures == 0


class _AssertRaisesContext:
    """Context manager para assertRaises."""
    
    def __init__(self, exception_class):
        self.exception_class = exception_class
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            raise AssertionError("Expected {} to be raised".format(self.exception_class.__name__))
        if not issubclass(exc_type, self.exception_class):
            raise AssertionError("Expected {} but got {}".format(
                self.exception_class.__name__, exc_type.__name__))
        return True


class TestTask(TestCase):
    """Testes para a classe Task."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.task = Task("P1", "#FF0000", 0, 5, 1)
    
    def test_criacao_task(self):
        """Testa a criação correta de uma Task."""
        self.assertEqual(self.task.id, "P1")
        self.assertEqual(self.task.cor, "#FF0000")
        self.assertEqual(self.task.ingresso, 0)
        self.assertEqual(self.task.duracao, 5)
        self.assertEqual(self.task.prioridade, 1)
        self.assertEqual(self.task.tempo_restante, 5)
        self.assertEqual(self.task.tempo_espera, 0)
        self.assertIsNone(self.task.tempo_resposta)
        self.assertEqual(self.task.estado, TaskState.NOVO)
    
    def test_validacao_parametros(self):
        """Testa validação de parâmetros na criação."""
        with self.assertRaises(ValueError):
            Task("P1", "#FF0000", 0, 0, 1)  # duração zero
        
        with self.assertRaises(ValueError):
            Task("P1", "#FF0000", -1, 5, 1)  # ingresso negativo
    
    def test_transicoes_estado(self):
        """Testa as transições de estado da Task."""
        # NOVO -> PRONTO
        self.task.admitir()
        self.assertEqual(self.task.estado, TaskState.PRONTO)
        
        # PRONTO -> EXECUTANDO
        self.task.iniciar_execucao(0)
        self.assertEqual(self.task.estado, TaskState.EXECUTANDO)
        self.assertEqual(self.task.tempo_resposta, 0)
        
        # EXECUTANDO -> PRONTO (pausa)
        self.task.pausar()
        self.assertEqual(self.task.estado, TaskState.PRONTO)
        
        # PRONTO -> EXECUTANDO -> BLOQUEADO
        self.task.iniciar_execucao(3)
        self.task.bloquear()
        self.assertEqual(self.task.estado, TaskState.BLOQUEADO)
        
        # BLOQUEADO -> PRONTO
        self.task.desbloquear()
        self.assertEqual(self.task.estado, TaskState.PRONTO)
    
    def test_execucao(self):
        """Testa a execução de uma Task."""
        self.task.admitir()
        self.task.iniciar_execucao(0)
        
        # Executa 2 unidades
        tempo_executado = self.task.executar(2)
        self.assertEqual(tempo_executado, 2)
        self.assertEqual(self.task.tempo_restante, 3)
        self.assertEqual(self.task.estado, TaskState.EXECUTANDO)
        
        # Executa mais que o restante
        tempo_executado = self.task.executar(10)
        self.assertEqual(tempo_executado, 3)  # só executou o restante
        self.assertEqual(self.task.tempo_restante, 0)
        self.assertEqual(self.task.estado, TaskState.TERMINADO)
    
    def test_execucao_estado_invalido(self):
        """Testa erro ao executar em estado inválido."""
        with self.assertRaises(RuntimeError):
            self.task.executar()  # não está em execução
    
    def test_calculo_metricas(self):
        """Testa o cálculo de métricas."""
        # Simula execução completa
        self.task.admitir()
        self.task.iniciar_execucao(2)  # tempo_resposta = 2
        self.task.executar(5)
        
        metricas = self.task.calcular_metricas(7)  # finaliza em t=7
        
        self.assertEqual(metricas['turnaround_time'], 7)  # 7-0
        self.assertEqual(metricas['waiting_time'], 2)    # 7-5
        self.assertEqual(metricas['response_time'], 2)   # 2-0
        self.assertEqual(metricas['normalized_turnaround'], 1.4)  # 7/5
    
    def test_metricas_tarefa_nao_terminada(self):
        """Testa erro ao calcular métricas de tarefa não terminada."""
        with self.assertRaises(ValueError):
            self.task.calcular_metricas(10)
    
    def test_tempo_resposta_unico(self):
        """Testa que tempo de resposta só é calculado na primeira execução."""
        self.task.admitir()
        self.task.iniciar_execucao(5)
        self.assertEqual(self.task.tempo_resposta, 5)
        
        # Pausa e retoma - não deve recalcular tempo_resposta
        self.task.pausar()
        self.task.iniciar_execucao(10)
        self.assertEqual(self.task.tempo_resposta, 5)  # mantém o valor original
    
    def test_string_representation(self):
        """Testa a representação string da Task."""
        task_str = str(self.task)
        self.assertIn("P1", task_str)
        self.assertIn("NOVO", task_str)
        self.assertIn("ingresso=0", task_str)
        self.assertIn("duracao=5", task_str)


class TestTCB(TestCase):
    """Testes para a classe TCB."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.tcb = TCB("P2", "#00FF00", 1, 4, 2)
    
    def test_heranca_task(self):
        """Testa que TCB herda corretamente de Task."""
        self.assertIsInstance(self.tcb, Task)
        self.assertEqual(self.tcb.id, "P2")
        self.assertEqual(self.tcb.duracao, 4)
    
    def test_atributos_tcb(self):
        """Testa atributos específicos do TCB."""
        self.assertIsNone(self.tcb.tempo_inicio_execucao)
        self.assertIsNone(self.tcb.tempo_fim)
        self.assertEqual(self.tcb.historico_execucao, [])
        self.assertEqual(self.tcb.contexto, {})
        self.assertEqual(self.tcb.numero_preempcoes, 0)
        self.assertEqual(self.tcb.tempo_total_cpu, 0)
    
    def test_logging_execucao(self):
        """Testa o logging de execução no TCB."""
        self.tcb.admitir()
        self.tcb.iniciar_execucao(2)
        
        # Verifica primeira execução
        self.assertEqual(self.tcb.tempo_inicio_execucao, 2)
        self.assertEqual(len(self.tcb.historico_execucao), 1)
        
        evento = self.tcb.historico_execucao[0]
        self.assertEqual(evento['evento'], 'INICIO_EXECUCAO')
        self.assertEqual(evento['tempo'], 2)
    
    def test_logging_preempcao(self):
        """Testa o logging de preempções."""
        self.tcb.admitir()
        self.tcb.iniciar_execucao(0)
        
        # Primeira preempção
        self.tcb.pausar()
        self.assertEqual(self.tcb.numero_preempcoes, 1)
        
        # Segunda preempção
        self.tcb.iniciar_execucao(5)
        self.tcb.pausar()
        self.assertEqual(self.tcb.numero_preempcoes, 2)
        
        # Verifica eventos no histórico
        preempcoes = [e for e in self.tcb.historico_execucao if e['evento'] == 'PREEMPCAO']
        self.assertEqual(len(preempcoes), 2)
    
    def test_contexto(self):
        """Testa adição de contexto."""
        self.tcb.adicionar_contexto("priority_boost", True)
        self.tcb.adicionar_contexto("memory_pages", 10)
        
        self.assertEqual(self.tcb.contexto["priority_boost"], True)
        self.assertEqual(self.tcb.contexto["memory_pages"], 10)
    
    def test_finalizacao(self):
        """Testa a finalização com logging."""
        self.tcb.admitir()
        self.tcb.iniciar_execucao(0)
        self.tcb.executar(4)  # execução completa
        self.tcb.finalizar(4)
        
        self.assertEqual(self.tcb.tempo_fim, 4)
        self.assertEqual(self.tcb.estado, TaskState.TERMINADO)
        
        # Verifica evento de finalização
        finalizacao = [e for e in self.tcb.historico_execucao if e['evento'] == 'FINALIZACAO']
        self.assertEqual(len(finalizacao), 1)
        self.assertEqual(finalizacao[0]['tempo'], 4)
    
    def test_estatisticas_completas(self):
        """Testa estatísticas detalhadas do TCB."""
        # Execução com preempção
        self.tcb.admitir()
        self.tcb.iniciar_execucao(1)
        self.tcb.executar(2)
        self.tcb.pausar()
        self.tcb.iniciar_execucao(5)
        self.tcb.executar(2)
        self.tcb.finalizar(7)
        
        stats = self.tcb.obter_estatisticas()
        
        # Verifica métricas básicas
        self.assertEqual(stats['turnaround_time'], 6)  # 7-1
        self.assertEqual(stats['waiting_time'], 2)     # 6-4
        
        # Verifica métricas TCB
        self.assertEqual(stats['tempo_inicio_execucao'], 1)
        self.assertEqual(stats['tempo_fim'], 7)
        self.assertEqual(stats['numero_preempcoes'], 1)
        self.assertEqual(stats['tempo_total_cpu'], 4)
        self.assertEqual(stats['eficiencia_cpu'], 1.0)
    
    def test_historico_resumido(self):
        """Testa o histórico resumido."""
        self.tcb.admitir()
        self.tcb.iniciar_execucao(0)
        self.tcb.executar(2)
        self.tcb.pausar()
        self.tcb.iniciar_execucao(3)
        self.tcb.executar(2)  # completa a execução
        self.tcb.finalizar(5)
        
        resumo = self.tcb.obter_historico_resumido()
        
        self.assertIn("t=0: Iniciou execução", resumo)
        self.assertIn("Executou 2u, restam 2u", resumo)
        self.assertIn("Preempção #1", resumo)
        self.assertIn("t=5: Finalizada", resumo)
    
    def test_string_representation_tcb(self):
        """Testa representação string do TCB."""
        tcb_str = str(self.tcb)
        self.assertIn("P2", tcb_str)
        self.assertIn("inicio_exec=None", tcb_str)
        self.assertIn("preempcoes=0", tcb_str)
        self.assertIn("cpu_total=0", tcb_str)


class TestTaskStates(TestCase):
    """Testes para transições de estado complexas."""
    
    def test_ciclo_vida_completo(self):
        """Testa um ciclo de vida completo de uma tarefa."""
        task = Task("P3", "#0000FF", 0, 3, 0)
        
        # Ciclo: NOVO -> PRONTO -> EXECUTANDO -> BLOQUEADO -> PRONTO -> EXECUTANDO -> TERMINADO
        self.assertEqual(task.estado, TaskState.NOVO)
        
        task.admitir()
        self.assertEqual(task.estado, TaskState.PRONTO)
        
        task.iniciar_execucao(0)
        self.assertEqual(task.estado, TaskState.EXECUTANDO)
        
        task.executar(1)
        task.bloquear()
        self.assertEqual(task.estado, TaskState.BLOQUEADO)
        
        task.desbloquear()
        self.assertEqual(task.estado, TaskState.PRONTO)
        
        task.iniciar_execucao(5)
        self.assertEqual(task.estado, TaskState.EXECUTANDO)
        
        task.executar(2)  # completa execução
        self.assertEqual(task.estado, TaskState.TERMINADO)
    
    def test_transicoes_invalidas(self):
        """Testa que transições inválidas não alteram o estado."""
        task = Task("P4", "#FFFF00", 0, 2, 0)
        
        # Tentar executar sem estar em execução
        with self.assertRaises(RuntimeError):
            task.executar()
        
        # Estado deve permanecer NOVO
        self.assertEqual(task.estado, TaskState.NOVO)


class TestMetricas(TestCase):
    """Testes específicos para cálculos de métricas."""
    
    def test_metricas_execucao_continua(self):
        """Testa métricas para execução sem preempção."""
        task = Task("P1", "#FF0000", 2, 4, 0)
        task.admitir()
        task.iniciar_execucao(2)  # inicia imediatamente
        task.executar(4)          # execução contínua
        
        metricas = task.calcular_metricas(6)
        
        self.assertEqual(metricas['turnaround_time'], 4)    # 6-2
        self.assertEqual(metricas['waiting_time'], 0)       # 4-4
        self.assertEqual(metricas['response_time'], 0)      # 2-2
        self.assertEqual(metricas['normalized_turnaround'], 1.0)  # 4/4
    
    def test_metricas_com_espera(self):
        """Testa métricas para execução com tempo de espera."""
        task = Task("P2", "#00FF00", 0, 3, 0)
        task.admitir()
        task.iniciar_execucao(5)  # espera 5 unidades
        task.executar(3)
        
        metricas = task.calcular_metricas(8)
        
        self.assertEqual(metricas['turnaround_time'], 8)    # 8-0
        self.assertEqual(metricas['waiting_time'], 5)       # 8-3
        self.assertEqual(metricas['response_time'], 5)      # 5-0
        self.assertAlmostEqual(metricas['normalized_turnaround'], 8/3, places=2)


def main():
    """Executa todos os testes."""
    print("Executando testes das estruturas de dados...")
    
    test_classes = [TestTask, TestTCB, TestTaskStates, TestMetricas]
    total_failures = 0
    
    for test_class in test_classes:
        test_instance = test_class()
        success = test_instance.run_all_tests()
        if not success:
            total_failures += test_instance.failures
    
    print("\n" + "="*50)
    if total_failures == 0:
        print("TODOS OS TESTES PASSARAM!")
    else:
        print("FALHAS ENCONTRADAS: {}".format(total_failures))
    
    return total_failures == 0


if __name__ == '__main__':
    # Executa os testes
    main()