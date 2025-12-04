"""
Módulo para parsing de arquivos de configuração do simulador de SO.

Formatos suportados:
    Linha 1: ALGORITMO;QUANTUM ou PRIOPEnv;QUANTUM;ALPHA
    Linhas seguintes: ID;COR;INGRESSO;DURACAO;PRIORIDADE;EVENTOS

Eventos:
    - IO:xx-yy → IOEvent (tempo xx, duração yy)
    - MLxx:yy → MutexLockEvent (mutex_id xx, tempo yy)
    - MUxx:yy → MutexUnlockEvent (mutex_id xx, tempo yy)
"""
from src.task import Task
from src.events import IOEvent, MutexLockEvent, MutexUnlockEvent
class ConfigParser:
    """Parser para arquivos de configuração do simulador."""
    ALGORITMOS_VALIDOS = ['FIFO', 'SRTF', 'PRIORIDADE', 'PRIOPENV']
    QUANTUM_PADRAO = 1
    PRIORIDADE_PADRAO = 0
    COR_PADRAO = '#808080'  # Cinza
    
    def __init__(self):
        self.config = {}
        self.tasks = []
        self.avisos = []
    
    def parse_file(self, filename):
        """
        Faz o parsing de um arquivo de configuração.
        Args:
            filename (str): Caminho do arquivo
        Returns:
            tuple: (config_dict, task_list)
        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se o formato for inválido
        """
        self._resetar()
        # Lê arquivo
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                linhas = f.readlines()
        except IOError:
            raise FileNotFoundError(f"Arquivo '{filename}' não encontrado")
        
        if not linhas:
            raise ValueError("Arquivo vazio")
        
        # Limpa linhas
        linhas = [l.strip() for l in linhas if l.strip() and not l.strip().startswith('#')]
        
        if not linhas:
            raise ValueError("Arquivo sem linhas válidas")
        
        # Parse da configuração
        self._parse_config(linhas[0])
        
        # Parse das tarefas
        for i, linha in enumerate(linhas[1:], start=2):
            self._parse_task(linha, i)
        
        # Valida
        if not self.tasks:
            raise ValueError("Nenhuma tarefa válida encontrada")
        
        # Verifica IDs duplicados
        ids = [t.id for t in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de tarefas duplicados")
        
        return (self.config, self.tasks)
    
    def _resetar(self):
        """Reseta estado interno."""
        self.config = {}
        self.tasks = []
        self.avisos = []
    
    def _parse_config(self, linha):
        """Parse da linha de configuração: ALGORITMO;QUANTUM ou PRIOPEnv;QUANTUM;ALPHA"""
        partes = linha.split(';')

        # Algoritmo
        algoritmo = partes[0].strip().upper()
        if algoritmo not in self.ALGORITMOS_VALIDOS:
            raise ValueError(
                f"Algoritmo '{algoritmo}' inválido. "
                f"Use: {', '.join(self.ALGORITMOS_VALIDOS)}"
            )
        
        self.config['algoritmo'] = algoritmo
        
        # Quantum (opcional para alguns algoritmos, obrigatório para PRIOPEnv)
        if len(partes) >= 2 and partes[1].strip():
            try:
                quantum = int(partes[1].strip())
                if quantum <= 0:
                    raise ValueError("Quantum deve ser > 0")
                self.config['quantum'] = quantum
            except ValueError as e:
                raise ValueError(f"Quantum inválido: {e}")
        else:
            self.config['quantum'] = self.QUANTUM_PADRAO

        # Alpha (apenas para PRIOPEnv)
        if algoritmo == 'PRIOPENV':
            if len(partes) >= 3 and partes[2].strip():
                try:
                    alpha = float(partes[2].strip())
                    if alpha <= 0:
                        raise ValueError("Alpha deve ser > 0")
                    self.config['alpha'] = alpha
                except ValueError as e:
                    raise ValueError(f"Alpha inválido: {e}")
            else:
                self.config['alpha'] = 1.0  # Padrão

    def _parse_task(self, linha, num_linha):
        """Parse de uma linha de tarefa: ID;COR;INGRESSO;DURACAO;PRIORIDADE;EVENTOS"""
        partes = [p.strip() for p in linha.split(';')]
        # Remove último se vazio (por causa do ; final)
        if partes and not partes[-1]:
            partes.pop()
        
        if len(partes) < 4:
            raise ValueError(
                f"Linha {num_linha}: formato inválido. "
                "Esperado: ID;COR;INGRESSO;DURACAO;PRIORIDADE;EVENTOS"
            )
        try:
            # Campos obrigatórios
            task_id = partes[0]
            cor = partes[1] if partes[1] else self.COR_PADRAO
            # Normaliza cor: garante que comece com '#' e seja hex válido
            if cor:
                cor = cor.strip()
                if not cor.startswith('#'):
                    cor = f"#{cor}"
                # Validação simples: deve ser '#RRGGBB'
                if len(cor) != 7 or not all(c in '0123456789ABCDEFabcdef#' for c in cor):
                    # Se inválido, usa cor padrão e registra aviso
                    self.avisos.append(f"Cor inválida na linha {num_linha}: '{partes[1]}'. Usando cor padrão.")
                    cor = self.COR_PADRAO
            ingresso = int(partes[2])
            duracao = int(partes[3])
            if not task_id:
                raise ValueError("ID vazio")
            if ingresso < 0:
                raise ValueError("Ingresso deve ser >= 0")
            if duracao <= 0:
                raise ValueError("Duração deve ser > 0")
            # Prioridade (opcional)
            prioridade = self.PRIORIDADE_PADRAO
            if len(partes) >= 5 and partes[4]:
                prioridade = int(partes[4])
            # Eventos (opcional)
            eventos = []
            if len(partes) >= 6:
                eventos_str = ';'.join(partes[5:])
                if eventos_str:
                    eventos = self._parse_eventos(eventos_str)
                    # Configura task_id nos eventos
                    for evento in eventos:
                        evento.task_id = task_id

            # Cria tarefa
            task = Task(task_id, cor, ingresso, duracao, prioridade, eventos)
            self.tasks.append(task)
            
        except ValueError as e:
            raise ValueError(f"Linha {num_linha}: {e}")
    
    def _parse_eventos(self, eventos_str):
        """
        Parse de eventos: IO:tempo-duracao;ML:tempo;MU:tempo
        
        Returns:
            list: Lista de dicts com eventos parseados
        """
        eventos = []

        for evento_str in eventos_str.split(';'):
            evento_str = evento_str.strip()
            if not evento_str:
                continue

            try:
                if evento_str.startswith('IO:'):
                    # IO:xx-yy
                    params = evento_str[3:].split('-')
                    if len(params) != 2:
                        self.avisos.append(f"Evento IO mal formatado: {evento_str}")
                        continue
                    tempo = int(params[0])
                    duracao = int(params[1])
                    if tempo < 0 or duracao <= 0:
                        self.avisos.append(f"Evento IO com valores inválidos: {evento_str}")
                        continue
                    eventos.append(IOEvent(tipo='IO', tempo_relativo=tempo, task_id='', duracao=duracao))

                elif evento_str.startswith('ML') and ':' in evento_str:
                    # MLxx:yy
                    idx = evento_str.find(':')
                    mutex_id = evento_str[2:idx]
                    tempo = int(evento_str[idx+1:])
                    if tempo < 0:
                        self.avisos.append(f"Tempo negativo em: {evento_str}")
                        continue
                    eventos.append(MutexLockEvent(tipo='MUTEX_LOCK', tempo_relativo=tempo, task_id='', mutex_id=mutex_id))

                elif evento_str.startswith('MU') and ':' in evento_str:
                    # MUxx:yy
                    idx = evento_str.find(':')
                    mutex_id = evento_str[2:idx]
                    tempo = int(evento_str[idx+1:])
                    if tempo < 0:
                        self.avisos.append(f"Tempo negativo em: {evento_str}")
                        continue
                    eventos.append(MutexUnlockEvent(tipo='MUTEX_UNLOCK', tempo_relativo=tempo, task_id='', mutex_id=mutex_id))

                else:
                    self.avisos.append(f"Formato de evento inválido: {evento_str}")

            except (ValueError, IndexError) as e:
                self.avisos.append(f"Erro ao parsear evento '{evento_str}': {e}")
        
        return eventos
    
    def obter_avisos(self):
        """Retorna lista de avisos."""
        return self.avisos[:]
    
    def obter_resumo(self):
        """Retorna resumo da configuração."""
        if not self.config or not self.tasks:
            return {'valido': False}

        resumo = {
            'valido': True,
            'algoritmo': self.config['algoritmo'],
            'quantum': self.config['quantum'],
            'total_tarefas': len(self.tasks),
            'duracao_total': sum(t.duracao for t in self.tasks),
            'avisos': len(self.avisos)
        }

        # Adiciona alpha se PRIOPEnv
        if self.config.get('alpha') is not None:
            resumo['alpha'] = self.config['alpha']

        return resumo

def criar_arquivo_exemplo(filename, algoritmo='FIFO', quantum=1, alpha=None):
    """Cria arquivo de exemplo com eventos.

    Args:
        filename: Nome do arquivo
        algoritmo: FIFO, SRTF, PRIORIDADE, ou PRIOPENV
        quantum: Quantum para o algoritmo
        alpha: Alpha para PRIOPEnv (opcional)
    """
    with open(filename, 'w', encoding='utf-8') as f:
        if algoritmo == 'PRIOPENV' and alpha is not None:
            f.write(f"{algoritmo};{quantum};{alpha}\n")
        else:
            f.write(f"{algoritmo};{quantum}\n")

        # Exemplos com eventos
        f.write("t01;#FF0000;0;5;2;IO:2-1;ML01:1;MU01:4\n")
        f.write("t02;#00FF00;1;3;1;IO:1-2;ML02:2\n")
        f.write("t03;#0000FF;2;4;3;ML01:0;MU01:3\n")


# Teste básico
if __name__ == '__main__':
    print("=== Teste do ConfigParser ===\n")
    
    try:
        parser = ConfigParser()
        config, tasks = parser.parse_file('../examples/config_fifo.txt')
        
        print(f"Algoritmo: {config['algoritmo']}")
        print(f"Quantum: {config['quantum']}")
        print(f"Tarefas: {len(tasks)}\n")
        
        for task in tasks:
            eventos_info = f" ({len(task.eventos)} eventos)" if task.eventos else ""
            print(f"  {task.id}: ingresso={task.ingresso}, "
                  f"duracao={task.duracao}{eventos_info}")
        
        avisos = parser.obter_avisos()
        if avisos:
            print("\nAvisos:")
            for aviso in avisos:
                print(f"  - {aviso}")
        
        print("\n✓ Teste passou!")
        
    except Exception as e:
        print(f"✗ Erro: {e}")