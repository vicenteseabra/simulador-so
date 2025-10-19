"""
Módulo para parsing de arquivos de configuração do simulador de SO.

Este módulo implementa a classe ConfigParser que lê arquivos de configuração
contendo informações sobre o algoritmo de escalonamento e as tarefas a serem
executadas.

Formato esperado do arquivo:
    Linha 1: algoritmo_escalonamento;quantum
    Linhas seguintes: id;cor;ingresso;duracao;prioridade;lista_eventos

Onde:
    - algoritmo_escalonamento: algoritmo de escalonamento a ser usado
    - quantum: período máximo de tempo que uma tarefa pode executar
    - id: identificador único da tarefa
    - cor: cor que identifica a execução da tarefa
    - ingresso: instante de tempo que a tarefa foi criada
    - duracao: tempo de execução da tarefa
    - prioridade: prioridade da tarefa
    - lista_eventos: lista de eventos que ocorre durante a execução da tarefa

Exemplo:
    FIFO;2
    1;#FF0000;0;5;1;
    2;#00FF00;2;3;1;E/S(3,1)
"""


class ConfigParser:
    """
    Parser para arquivos de configuração do simulador.
    
    Lê arquivos de configuração e retorna um dicionário com as configurações
    do sistema e uma lista de objetos Task.
    """
    
    # Algoritmos de escalonamento suportados
    ALGORITMOS_VALIDOS = ['FIFO', 'SRTF', 'PRIORIDADE']
    
    # Valores padrão
    QUANTUM_PADRAO = 1
    PRIORIDADE_PADRAO = 0
    COR_PADRAO = '#808080'  # Cinza
    
    def __init__(self):
        """Inicializa o parser."""
        self.config = {}
        self.tasks = []
        self.erros = []
        self.avisos = []
    
    def parse_file(self, filename):
        """
        Faz o parsing de um arquivo de configuração.
        
        Args:
            filename (str): Caminho do arquivo de configuração
            
        Returns:
            tuple: (config_dict, task_list)
                config_dict: Dicionário com configurações do sistema
                task_list: Lista de objetos Task
                
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            ValueError: Se o formato do arquivo for inválido
        """
        self._resetar_estado()
        
        # Tenta abrir o arquivo
        try:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                linhas = file.readlines()
        except IOError as e:
            raise FileNotFoundError("Arquivo '{}' não encontrado: {}".format(filename, str(e)))
        
        # Valida se o arquivo não está vazio
        if not linhas:
            raise ValueError("Arquivo de configuração está vazio")
        
        # Remove linhas vazias e comentários
        linhas = self._limpar_linhas(linhas)
        
        if not linhas:
            raise ValueError("Arquivo não contém linhas válidas")
        
        # Parse da primeira linha (configuração do sistema)
        self._parse_linha_config(linhas[0], 1)
        
        # Parse das linhas de tarefas
        for i, linha in enumerate(linhas[1:], start=2):
            self._parse_linha_task(linha, i)
        
        # Valida a configuração completa
        self.validar_configuracao()
        
        return (self.config, self.tasks)
    
    def _resetar_estado(self):
        """Reseta o estado interno do parser."""
        self.config = {}
        self.tasks = []
        self.erros = []
        self.avisos = []
    
    def _limpar_linhas(self, linhas):
        """
        Remove linhas vazias, espaços e comentários.
        
        Args:
            linhas (list): Lista de linhas do arquivo
            
        Returns:
            list: Lista de linhas limpas
        """
        linhas_limpas = []
        for linha in linhas:
            # Remove espaços em branco no início e fim
            linha = linha.strip()
            
            # Ignora linhas vazias
            if not linha:
                continue
            
            # Ignora linhas de comentário (começam com #)
            if linha.startswith('#'):
                continue
            
            linhas_limpas.append(linha)
        
        return linhas_limpas
    
    def _parse_linha_config(self, linha, num_linha):
        """
        Faz o parsing da linha de configuração do sistema.
        
        Formato esperado: ALGORITMO;QUANTUM
        
        Args:
            linha (str): Linha a ser parseada
            num_linha (int): Número da linha no arquivo (para mensagens de erro)
            
        Raises:
            ValueError: Se o formato estiver inválido
        """
        partes = linha.split(';')
        
        if len(partes) < 1:
            raise ValueError("Linha {}: Formato inválido para configuração".format(num_linha))
        
        # Parse do algoritmo (obrigatório)
        algoritmo = partes[0].strip().upper()
        
        if not algoritmo:
            raise ValueError("Linha {}: Algoritmo não especificado".format(num_linha))
        
        if algoritmo not in self.ALGORITMOS_VALIDOS:
            raise ValueError(
                "Linha {}: Algoritmo '{}' não é válido. "
                "Algoritmos válidos: {}".format(
                    num_linha, algoritmo, ', '.join(self.ALGORITMOS_VALIDOS)))
        
        self.config['algoritmo'] = algoritmo
        
        # Parse do quantum (opcional, usa padrão se não especificado)
        if len(partes) >= 2 and partes[1].strip():
            try:
                quantum = int(partes[1].strip())
                if quantum <= 0:
                    raise ValueError("Quantum deve ser maior que zero")
                self.config['quantum'] = quantum
            except ValueError as e:
                raise ValueError(
                    "Linha {}: Quantum inválido '{}': {}".format(
                        num_linha, partes[1].strip(), str(e)))
        else:
            self.config['quantum'] = self.QUANTUM_PADRAO
            self.avisos.append(
                "Linha {}: Quantum não especificado, usando valor padrão: {}".format(
                    num_linha, self.QUANTUM_PADRAO))
    
    def _parse_linha_task(self, linha, num_linha):
        """
        Faz o parsing de uma linha de tarefa.
        
        Formato esperado: id;cor;ingresso;duracao;prioridade;lista_eventos
        
        Args:
            linha (str): Linha a ser parseada
            num_linha (int): Número da linha no arquivo
        """
        partes = linha.split(';')
        
        # Remove último elemento se for vazio (por causa do ; final)
        if partes and not partes[-1].strip():
            partes = partes[:-1]
        
        if len(partes) < 4:
            self.erros.append(
                "Linha {}: Formato inválido para tarefa. "
                "Esperado: id;cor;ingresso;duracao;prioridade;lista_eventos".format(num_linha))
            return
        
        try:
            # Parse dos campos obrigatórios
            task_id = partes[0].strip()
            cor = partes[1].strip() if partes[1].strip() else self.COR_PADRAO
            ingresso = int(partes[2].strip())
            duracao = int(partes[3].strip())
            
            # Parse dos campos opcionais
            # Prioridade (campo 5)
            if len(partes) >= 5 and partes[4].strip():
                prioridade = int(partes[4].strip())
            else:
                prioridade = self.PRIORIDADE_PADRAO
                self.avisos.append(
                    "Linha {}: Prioridade não especificada para tarefa '{}', "
                    "usando valor padrão: {}".format(
                        num_linha, task_id, self.PRIORIDADE_PADRAO))
            
            # Lista de eventos (campo 6) - opcional
            lista_eventos = []
            if len(partes) >= 6 and partes[5].strip():
                lista_eventos_str = partes[5].strip()
                # Parse da lista de eventos (formato: E/S(tempo,duracao);E/S(tempo,duracao))
                lista_eventos = self._parse_eventos(lista_eventos_str, task_id, num_linha)
            
            # Validações básicas
            if not task_id:
                raise ValueError("ID da tarefa não pode ser vazio")
            
            if ingresso < 0:
                raise ValueError("Tempo de ingresso não pode ser negativo")
            
            if duracao <= 0:
                raise ValueError("Duração deve ser maior que zero")
            
            # Valida formato da cor (hexadecimal)
            if not self._validar_cor(cor):
                self.avisos.append(
                    "Linha {}: Cor '{}' pode não estar em formato válido. "
                    "Formato esperado: #RRGGBB".format(num_linha, cor))
            
            # Importa Task aqui para evitar dependências circulares
            from task import Task
            
            # Cria a tarefa
            task = Task(task_id, cor, ingresso, duracao, prioridade)
            
            # Armazena a lista de eventos na tarefa (usando atributo dinâmico)
            task.lista_eventos = lista_eventos
            
            self.tasks.append(task)
            
        except ValueError as e:
            self.erros.append(
                "Linha {}: Erro ao criar tarefa: {}".format(num_linha, str(e)))
        except Exception as e:
            self.erros.append(
                "Linha {}: Erro inesperado: {}".format(num_linha, str(e)))
    
    def _validar_cor(self, cor):
        """
        Valida se a cor está em formato hexadecimal válido.
        
        Args:
            cor (str): String da cor a validar
            
        Returns:
            bool: True se a cor é válida, False caso contrário
        """
        if not cor:
            return False
        
        # Formato #RRGGBB ou #RGB
        if not cor.startswith('#'):
            return False
        
        hex_part = cor[1:]
        
        # Deve ter 6 ou 3 caracteres hexadecimais
        if len(hex_part) not in [3, 6]:
            return False
        
        # Todos os caracteres devem ser hexadecimais
        for char in hex_part:
            if char not in '0123456789ABCDEFabcdef':
                return False
        
        return True
    
    def _parse_eventos(self, eventos_str, task_id, num_linha):
        """
        Faz o parsing da lista de eventos.
        
        Formato esperado: E/S(tempo,duracao) ou E/S(tempo,duracao);E/S(tempo,duracao)
        
        Args:
            eventos_str (str): String com os eventos
            task_id (str): ID da tarefa (para mensagens de erro)
            num_linha (int): Número da linha (para mensagens de erro)
            
        Returns:
            list: Lista de dicionários com eventos parseados
        """
        if not eventos_str:
            return []
        
        eventos = []
        
        # Separa múltiplos eventos se houver ponto-e-vírgula
        # mas não dentro dos parênteses
        eventos_individuais = self._separar_eventos(eventos_str)
        
        for evento_str in eventos_individuais:
            evento_str = evento_str.strip()
            if not evento_str:
                continue
            
            try:
                # Formato: E/S(tempo,duracao)
                if evento_str.startswith('E/S(') and evento_str.endswith(')'):
                    # Remove 'E/S(' e ')'
                    parametros = evento_str[4:-1]
                    partes = parametros.split(',')
                    
                    if len(partes) != 2:
                        self.avisos.append(
                            "Linha {}: Evento '{}' para tarefa '{}' "
                            "tem formato inválido".format(num_linha, evento_str, task_id))
                        continue
                    
                    tempo = int(partes[0].strip())
                    duracao_evento = int(partes[1].strip())
                    
                    if tempo < 0 or duracao_evento < 0:
                        self.avisos.append(
                            "Linha {}: Evento com valores negativos ignorado "
                            "na tarefa '{}'".format(num_linha, task_id))
                        continue
                    
                    eventos.append({
                        'tipo': 'E/S',
                        'tempo': tempo,
                        'duracao': duracao_evento
                    })
                else:
                    self.avisos.append(
                        "Linha {}: Formato de evento '{}' não reconhecido "
                        "na tarefa '{}'".format(num_linha, evento_str, task_id))
            
            except ValueError as e:
                self.avisos.append(
                    "Linha {}: Erro ao parsear evento '{}' na tarefa '{}': {}".format(
                        num_linha, evento_str, task_id, str(e)))
        
        return eventos
    
    def _separar_eventos(self, eventos_str):
        """
        Separa múltiplos eventos, respeitando parênteses.
        
        Args:
            eventos_str (str): String com eventos
            
        Returns:
            list: Lista de strings, cada uma representando um evento
        """
        eventos = []
        evento_atual = []
        nivel_parenteses = 0
        
        for char in eventos_str:
            if char == '(':
                nivel_parenteses += 1
                evento_atual.append(char)
            elif char == ')':
                nivel_parenteses -= 1
                evento_atual.append(char)
            elif char == ';' and nivel_parenteses == 0:
                # Fim de um evento
                if evento_atual:
                    eventos.append(''.join(evento_atual))
                    evento_atual = []
            else:
                evento_atual.append(char)
        
        # Adiciona último evento
        if evento_atual:
            eventos.append(''.join(evento_atual))
        
        return eventos
    
    def validar_configuracao(self):
        """
        Valida a configuração completa parseada.
        
        Verifica:
        - Se há pelo menos uma tarefa
        - Se não há IDs de tarefa duplicados
        - Se há erros acumulados durante o parsing
        
        Raises:
            ValueError: Se a configuração for inválida
        """
        # Verifica se há erros acumulados
        if self.erros:
            mensagem_erro = "Erros encontrados durante o parsing:\n"
            for erro in self.erros:
                mensagem_erro += "  - {}\n".format(erro)
            raise ValueError(mensagem_erro.rstrip())
        
        # Verifica se há pelo menos uma tarefa
        if not self.tasks:
            raise ValueError("Nenhuma tarefa válida foi encontrada no arquivo")
        
        # Verifica IDs duplicados
        ids_vistos = {}
        for task in self.tasks:
            if task.id in ids_vistos:
                raise ValueError(
                    "ID de tarefa duplicado: '{}' aparece múltiplas vezes".format(task.id))
            ids_vistos[task.id] = True
        
        # Validações específicas por algoritmo
        algoritmo = self.config.get('algoritmo', '')
        
        if algoritmo == 'RR' and self.config.get('quantum', 0) <= 0:
            raise ValueError("Algoritmo Round Robin requer quantum > 0")
    
    def obter_avisos(self):
        """
        Retorna lista de avisos gerados durante o parsing.
        
        Returns:
            list: Lista de strings com avisos
        """
        return self.avisos[:]  # Retorna uma cópia
    
    def obter_resumo(self):
        """
        Retorna um resumo da configuração parseada.
        
        Returns:
            dict: Dicionário com informações resumidas
        """
        if not self.config or not self.tasks:
            return {
                'valido': False,
                'mensagem': 'Configuração não carregada ou inválida'
            }
        
        # Calcula estatísticas das tarefas
        total_duracao = sum(task.duracao for task in self.tasks)
        min_ingresso = min(task.ingresso for task in self.tasks)
        max_ingresso = max(task.ingresso for task in self.tasks)
        
        prioridades = {}
        for task in self.tasks:
            prioridades[task.prioridade] = prioridades.get(task.prioridade, 0) + 1
        
        return {
            'valido': True,
            'algoritmo': self.config['algoritmo'],
            'quantum': self.config['quantum'],
            'total_tarefas': len(self.tasks),
            'duracao_total': total_duracao,
            'tempo_chegada_minimo': min_ingresso,
            'tempo_chegada_maximo': max_ingresso,
            'distribuicao_prioridades': prioridades,
            'ids_tarefas': [task.id for task in self.tasks],
            'avisos': len(self.avisos)
        }


if __name__ == '__main__':
    """
    Testes básicos do parser.
    """
    print("=== Testes do ConfigParser ===\n")
    
    # Teste 1: Parse de arquivo de exemplo
    print("Teste 1: Parsing de config_fifo.txt")
    try:
        parser = ConfigParser()
        config, tasks = parser.parse_file('../examples/config_fifo.txt')
        
        print("Configuração:")
        print("  Algoritmo: {}".format(config['algoritmo']))
        print("  Quantum: {}".format(config['quantum']))
        print("\nTarefas carregadas: {}".format(len(tasks)))
        for task in tasks:
            eventos_info = ""
            if hasattr(task, 'lista_eventos') and task.lista_eventos:
                eventos_info = " ({} eventos)".format(len(task.lista_eventos))
            print("  - Task {}: ingresso={}, duracao={}, prioridade={}{}".format(
                task.id, task.ingresso, task.duracao, task.prioridade, eventos_info))
        
        # Mostra resumo
        print("\nResumo:")
        resumo = parser.obter_resumo()
        for chave, valor in resumo.items():
            print("  {}: {}".format(chave, valor))
        
        # Mostra avisos
        avisos = parser.obter_avisos()
        if avisos:
            print("\nAvisos:")
            for aviso in avisos:
                print("  - {}".format(aviso))
        
        print("\n✓ Teste 1 passou!")
        
    except Exception as e:
        print("✗ Erro no teste 1: {}".format(str(e)))
    
    print("\n" + "="*50 + "\n")
    
    # Teste 2: Validação de erros
    print("Teste 2: Testando validação de erros")
    try:
        parser = ConfigParser()
        
        # Tenta parsear arquivo inexistente
        try:
            parser.parse_file('arquivo_inexistente.txt')
            print("✗ Deveria ter lançado FileNotFoundError")
        except FileNotFoundError:
            print("✓ FileNotFoundError capturado corretamente")
        
        print("\n✓ Teste 2 passou!")
        
    except Exception as e:
        print("✗ Erro no teste 2: {}".format(str(e)))
