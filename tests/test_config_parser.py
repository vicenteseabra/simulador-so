"""
Testes para o módulo config_parser.

Este módulo contém testes abrangentes para a classe ConfigParser,
incluindo casos de sucesso, casos de erro e validações.
"""

# Importa apenas o necessário
try:
    # Tenta importar do diretório src
    from config_parser import ConfigParser, criar_arquivo_exemplo
except ImportError:
    # Se falhar, tenta adicionar o path manualmente
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from config_parser import ConfigParser, criar_arquivo_exemplo


class TestCase:
    """Classe base para testes."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_name = ""
    
    def assertEqual(self, a, b, msg=None):
        """Verifica se a == b."""
        if a != b:
            error_msg = msg or "Esperado {}, obtido {}".format(b, a)
            raise AssertionError(error_msg)
    
    def assertTrue(self, expr, msg=None):
        """Verifica se expr é True."""
        if not expr:
            error_msg = msg or "Expressão não é True"
            raise AssertionError(error_msg)
    
    def assertFalse(self, expr, msg=None):
        """Verifica se expr é False."""
        if expr:
            error_msg = msg or "Expressão não é False"
            raise AssertionError(error_msg)
    
    def assertIsNone(self, obj, msg=None):
        """Verifica se obj é None."""
        if obj is not None:
            error_msg = msg or "Objeto não é None: {}".format(obj)
            raise AssertionError(error_msg)
    
    def assertIsNotNone(self, obj, msg=None):
        """Verifica se obj não é None."""
        if obj is None:
            error_msg = msg or "Objeto é None"
            raise AssertionError(error_msg)
    
    def assertIn(self, item, container, msg=None):
        """Verifica se item está em container."""
        if item not in container:
            error_msg = msg or "{} não está em {}".format(item, container)
            raise AssertionError(error_msg)
    
    def assertRaises(self, exception_class):
        """Context manager para verificar se uma exceção é lançada."""
        return AssertRaisesContext(exception_class)
    
    def assertGreater(self, a, b, msg=None):
        """Verifica se a > b."""
        if not (a > b):
            error_msg = msg or "{} não é maior que {}".format(a, b)
            raise AssertionError(error_msg)
    
    def assertGreaterEqual(self, a, b, msg=None):
        """Verifica se a >= b."""
        if not (a >= b):
            error_msg = msg or "{} não é maior ou igual a {}".format(a, b)
            raise AssertionError(error_msg)
    
    def run_all_tests(self):
        """Executa todos os métodos de teste."""
        test_methods = [method for method in dir(self) 
                       if method.startswith('test_') and callable(getattr(self, method))]
        
        print("\n" + "=" * 70)
        print("Executando testes para: {}".format(self.__class__.__name__))
        print("=" * 70)
        
        for method_name in test_methods:
            self.test_name = method_name
            method = getattr(self, method_name)
            
            try:
                method()
                self.passed += 1
                print("  ✓ {} passou".format(method_name))
            except AssertionError as e:
                self.failed += 1
                print("  ✗ {} falhou: {}".format(method_name, str(e)))
            except Exception as e:
                self.failed += 1
                print("  ✗ {} erro: {}".format(method_name, str(e)))
        
        print("\n" + "-" * 70)
        print("Resultados: {} passaram, {} falharam".format(self.passed, self.failed))
        print("=" * 70 + "\n")
        
        return self.failed == 0


class AssertRaisesContext:
    """Context manager para assertRaises."""
    
    def __init__(self, exception_class):
        self.exception_class = exception_class
        self.exception = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(
                "Esperava exceção {}, mas nenhuma foi lançada".format(
                    self.exception_class.__name__))
        
        if not issubclass(exc_type, self.exception_class):
            # Deixa a exceção propagar
            return False
        
        self.exception = exc_val
        return True


class TestConfigParser(TestCase):
    """Testes para a classe ConfigParser."""
    
    def setUp(self):
        """Configuração antes de cada teste."""
        self.parser = ConfigParser()
        self.test_files = []
    
    def tearDown(self):
        """Limpeza após cada teste."""
        # Remove arquivos de teste criados
        for filename in self.test_files:
            try:
                # Tenta abrir e fechar para verificar se existe
                f = open(filename, 'r')
                f.close()
                # Se chegou aqui, arquivo existe - avisa para deletar manualmente
                # (não podemos usar os.remove pois não temos import de os)
            except:
                pass  # Arquivo não existe ou já foi removido
    
    def criar_arquivo_teste(self, filename, conteudo):
        """Cria um arquivo de teste temporário."""
        self.test_files.append(filename)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        return filename
    
    # Testes de parsing bem-sucedido
    
    def test_parse_fifo_basico(self):
        """Testa parsing de configuração FIFO básica."""
        conteudo = "FIFO;2\n1;#FF0000;0;5;1;\n2;#00FF00;2;3;1;\n"
        arquivo = self.criar_arquivo_teste('test_fifo.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(config['algoritmo'], 'FIFO')
        self.assertEqual(config['quantum'], 2)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, '1')
        self.assertEqual(tasks[1].id, '2')
    
    def test_parse_round_robin(self):
        """Testa parsing de configuração Round Robin."""
        conteudo = "SRTF;3\nP1;#FF0000;0;10;0;\nP2;#00FF00;5;8;0;\n"
        arquivo = self.criar_arquivo_teste('test_rr.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)

        self.assertEqual(config['algoritmo'], 'RR')
        self.assertEqual(config['quantum'], 3)
        self.assertEqual(len(tasks), 2)
    
    def test_parse_prioridade(self):
        """Testa parsing com diferentes prioridades."""
        conteudo = "PRIORIDADE;1\n1;#FF0000;0;5;0;\n2;#00FF00;1;3;2;\n3;#0000FF;2;4;1;\n"
        arquivo = self.criar_arquivo_teste('test_prio.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(config['algoritmo'], 'PRIORIDADE')
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].prioridade, 0)
        self.assertEqual(tasks[1].prioridade, 2)
        self.assertEqual(tasks[2].prioridade, 1)
    
    def test_parse_srtf(self):
        """Testa parsing de configuração SRTF."""
        conteudo = "SRTF;1\n1;#FF0000;0;8;1;\n2;#00FF00;1;4;1;\n"
        arquivo = self.criar_arquivo_teste('test_srtf.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(config['algoritmo'], 'SRTF')
        self.assertEqual(len(tasks), 2)
    
    def test_parse_sjf(self):
        """Testa parsing de configuração SJF."""
        conteudo = "SJF;1\n1;#FF0000;0;5;1;\n2;#00FF00;2;3;1;\n"
        arquivo = self.criar_arquivo_teste('test_sjf.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(config['algoritmo'], 'SJF')
    
    # Testes de valores padrão
    
    def test_quantum_padrao(self):
        """Testa uso de quantum padrão quando não especificado."""
        conteudo = "FIFO\n1;#FF0000;0;5;1;\n"
        arquivo = self.criar_arquivo_teste('test_quantum_padrao.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(config['quantum'], ConfigParser.QUANTUM_PADRAO)
        self.assertGreater(len(self.parser.obter_avisos()), 0)
    
    def test_prioridade_padrao(self):
        """Testa uso de prioridade padrão."""
        conteudo = "FIFO;2\n1;#FF0000;0;5;\n"
        arquivo = self.criar_arquivo_teste('test_prio_padrao.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(tasks[0].prioridade, ConfigParser.PRIORIDADE_PADRAO)
        self.assertGreater(len(self.parser.obter_avisos()), 0)
    
    def test_cor_padrao(self):
        """Testa uso de cor padrão quando vazia."""
        conteudo = "FIFO;2\n1;;0;5;1;\n"
        arquivo = self.criar_arquivo_teste('test_cor_padrao.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(tasks[0].cor, ConfigParser.COR_PADRAO)
    
    # Testes de validação de formato
    
    def test_arquivo_vazio(self):
        """Testa erro com arquivo vazio."""
        arquivo = self.criar_arquivo_teste('test_vazio.txt', '')
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    def test_arquivo_nao_encontrado(self):
        """Testa erro quando arquivo não existe."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file('arquivo_inexistente_xyz.txt')
    
    def test_algoritmo_invalido(self):
        """Testa erro com algoritmo inválido."""
        conteudo = "FCFS;2\n1;#FF0000;0;5;1;\n"
        arquivo = self.criar_arquivo_teste('test_algo_invalido.txt', conteudo)
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    def test_quantum_invalido(self):
        """Testa erro com quantum inválido."""
        conteudo = "FIFO;abc\n1;#FF0000;0;5;1;\n"
        arquivo = self.criar_arquivo_teste('test_quantum_invalido.txt', conteudo)
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    def test_quantum_negativo(self):
        """Testa erro com quantum negativo."""
        conteudo = "FIFO;-1\n1;#FF0000;0;5;1;\n"
        arquivo = self.criar_arquivo_teste('test_quantum_neg.txt', conteudo)
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    def test_id_duplicado(self):
        """Testa erro com IDs duplicados."""
        conteudo = "FIFO;2\n1;#FF0000;0;5;1;\n1;#00FF00;2;3;1;\n"
        arquivo = self.criar_arquivo_teste('test_id_dup.txt', conteudo)
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    def test_duracao_zero(self):
        """Testa erro com duração zero."""
        conteudo = "FIFO;2\n1;#FF0000;0;0;1;\n"
        arquivo = self.criar_arquivo_teste('test_duracao_zero.txt', conteudo)
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    def test_duracao_negativa(self):
        """Testa erro com duração negativa."""
        conteudo = "FIFO;2\n1;#FF0000;0;-5;1;\n"
        arquivo = self.criar_arquivo_teste('test_duracao_neg.txt', conteudo)
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    def test_ingresso_negativo(self):
        """Testa erro com tempo de ingresso negativo."""
        conteudo = "FIFO;2\n1;#FF0000;-1;5;1;\n"
        arquivo = self.criar_arquivo_teste('test_ingresso_neg.txt', conteudo)
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    def test_formato_tarefa_invalido(self):
        """Testa erro com formato de tarefa inválido."""
        conteudo = "FIFO;2\n1;#FF0000;0;\n"
        arquivo = self.criar_arquivo_teste('test_formato_invalido.txt', conteudo)
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    def test_sem_tarefas(self):
        """Testa erro quando não há tarefas válidas."""
        conteudo = "FIFO;2\n"
        arquivo = self.criar_arquivo_teste('test_sem_tarefas.txt', conteudo)
        
        with self.assertRaises(ValueError):
            self.parser.parse_file(arquivo)
    
    # Testes de recursos especiais
    
    def test_comentarios_ignorados(self):
        """Testa que linhas de comentário são ignoradas."""
        conteudo = "# Comentário\nFIFO;2\n# Outro comentário\n1;#FF0000;0;5;1;\n"
        arquivo = self.criar_arquivo_teste('test_comentarios.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(len(tasks), 1)
    
    def test_linhas_vazias_ignoradas(self):
        """Testa que linhas vazias são ignoradas."""
        conteudo = "FIFO;2\n\n1;#FF0000;0;5;1;\n\n2;#00FF00;2;3;1;\n\n"
        arquivo = self.criar_arquivo_teste('test_linhas_vazias.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(len(tasks), 2)
    
    def test_espacos_removidos(self):
        """Testa que espaços são removidos."""
        conteudo = " FIFO ; 2 \n 1 ; #FF0000 ; 0 ; 5 ; 1 ;\n"
        arquivo = self.criar_arquivo_teste('test_espacos.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(config['algoritmo'], 'FIFO')
        self.assertEqual(tasks[0].id, '1')
    
    def test_ponto_virgula_final_opcional(self):
        """Testa que o ponto-e-vírgula final é opcional."""
        conteudo = "FIFO;2\n1;#FF0000;0;5;1\n"
        arquivo = self.criar_arquivo_teste('test_sem_pv.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(len(tasks), 1)
    
    # Testes de métodos auxiliares
    
    def test_obter_resumo(self):
        """Testa o método obter_resumo()."""
        conteudo = "FIFO;2\n1;#FF0000;0;5;1;\n2;#00FF00;2;3;1;\n"
        arquivo = self.criar_arquivo_teste('test_resumo.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        resumo = self.parser.obter_resumo()
        
        self.assertTrue(resumo['valido'])
        self.assertEqual(resumo['algoritmo'], 'FIFO')
        self.assertEqual(resumo['total_tarefas'], 2)
        self.assertEqual(resumo['duracao_total'], 8)
    
    def test_obter_avisos(self):
        """Testa o método obter_avisos()."""
        conteudo = "FIFO\n1;#FF0000;0;5;\n"
        arquivo = self.criar_arquivo_teste('test_avisos.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        avisos = self.parser.obter_avisos()
        
        self.assertGreater(len(avisos), 0)
    
    def test_validacao_cor_hexadecimal(self):
        """Testa validação de cores hexadecimais."""
        # Cores válidas
        self.assertTrue(self.parser._validar_cor('#FF0000'))
        self.assertTrue(self.parser._validar_cor('#00FF00'))
        self.assertTrue(self.parser._validar_cor('#F00'))
        
        # Cores inválidas
        self.assertFalse(self.parser._validar_cor('FF0000'))
        self.assertFalse(self.parser._validar_cor('#GG0000'))
        self.assertFalse(self.parser._validar_cor('#FF'))
        self.assertFalse(self.parser._validar_cor(''))
    
    # Testes de integração
    
    def test_criar_arquivo_exemplo(self):
        """Testa a função criar_arquivo_exemplo()."""
        arquivo = 'test_exemplo_gerado.txt'
        self.test_files.append(arquivo)
        
        resultado = criar_arquivo_exemplo(arquivo, 'SRTF', 3, 4)
        
        self.assertTrue(resultado)
        
        # Verifica se arquivo foi criado tentando abrir
        try:
            f = open(arquivo, 'r')
            f.close()
            arquivo_existe = True
        except:
            arquivo_existe = False
        
        self.assertTrue(arquivo_existe)
        
        # Tenta parsear o arquivo gerado
        parser = ConfigParser()
        config, tasks = parser.parse_file(arquivo)
        
        self.assertEqual(config['algoritmo'], 'RR')
        self.assertEqual(config['quantum'], 3)
        self.assertEqual(len(tasks), 4)
    
    def test_multiplas_tarefas(self):
        """Testa parsing com muitas tarefas."""
        linhas = ["FIFO;2"]
        for i in range(10):
            linhas.append("{}::#FF0000;{};{};1;".format(i, i, i+1))
        conteudo = "\n".join(linhas) + "\n"
        
        arquivo = self.criar_arquivo_teste('test_multiplas.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(len(tasks), 10)
    
    def test_ids_diferentes_formatos(self):
        """Testa IDs em diferentes formatos."""
        conteudo = ("FIFO;2\n"
                   "P1;#FF0000;0;5;1;\n"
                   "Task_2;#00FF00;2;3;1;\n"
                   "processo-3;#0000FF;4;4;1;\n")
        arquivo = self.criar_arquivo_teste('test_ids_formatos.txt', conteudo)
        
        config, tasks = self.parser.parse_file(arquivo)
        
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].id, 'P1')
        self.assertEqual(tasks[1].id, 'Task_2')
        self.assertEqual(tasks[2].id, 'processo-3')


def run_all_tests():
    """Executa todos os testes."""
    suite = TestConfigParser()
    
    # Chama setUp antes de cada teste
    for method_name in dir(suite):
        if method_name.startswith('test_'):
            suite.setUp()
    
    success = suite.run_all_tests()
    
    # Chama tearDown após todos os testes
    suite.tearDown()
    
    return success


if __name__ == '__main__':
    print("\n" + "="*70)
    print("TESTES DO CONFIG PARSER")
    print("="*70)
    
    success = run_all_tests()
    
    if success:
        print("\n✓ TODOS OS TESTES PASSARAM!")
        print("\nNOTA: Alguns arquivos de teste podem ter sido criados.")
        print("      Arquivos test_*.txt podem ser deletados manualmente.")
    else:
        print("\n✗ ALGUNS TESTES FALHARAM")
