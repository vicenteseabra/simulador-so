"""
Módulo para parsing de arquivos de configuração do simulador de SO.

Formato esperado:
    Linha 1: ALGORITMO;QUANTUM
    Linhas seguintes: ID;COR;INGRESSO;DURACAO;PRIORIDADE;EVENTOS

Eventos suportados:
    - IO:tempo-duracao (ex: IO:2-1)
    - ML:tempo (ex: ML:1)
    - MU:tempo (ex: MU:3)
"""
from src.task import Task
class ConfigParser:
    """Parser para arquivos de configuração do simulador."""
    ALGORITMOS_VALIDOS = ['FIFO', 'SRTF', 'PRIORIDADE']
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
        """Parse da linha de configuração: ALGORITMO;QUANTUM"""
        partes = linha.split(';')
        # Algoritmo
        algoritmo = partes[0].strip().upper()
        if algoritmo not in self.ALGORITMOS_VALIDOS:
            raise ValueError(
                f"Algoritmo '{algoritmo}' inválido. "
                f"Use: {', '.join(self.ALGORITMOS_VALIDOS)}"
            )
        
        self.config['algoritmo'] = algoritmo
        
        # Quantum (opcional)
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
                # Junta todos os campos restantes (caso tenha ; nos eventos)
                eventos_str = ';'.join(partes[5:])
                if eventos_str:
                    eventos = self._parse_eventos(eventos_str)
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
        # Separa por ; (eventos múltiplos)
        for evento_str in eventos_str.split(';'):
            evento_str = evento_str.strip()
            if not evento_str:
                continue
            try:
                # IO:tempo-duracao
                if evento_str.startswith('IO:'):
                    params = evento_str[3:].split('-')
                    if len(params) != 2:
                        self.avisos.append(f"Evento IO mal formatado: {evento_str}")
                        continue
                    tempo = int(params[0])
                    duracao = int(params[1])
                    if tempo < 0 or duracao < 0:
                        self.avisos.append(f"Evento IO com valores negativos: {evento_str}")
                        continue
                    eventos.append({
                        'tipo': 'IO',
                        'tempo': tempo,
                        'duracao': duracao
                    })
                # ML:tempo (Mutex Lock)
                elif evento_str.startswith('ML:'):
                    tempo = int(evento_str[3:])
                    if tempo < 0:
                        self.avisos.append(f"Evento ML com tempo negativo: {evento_str}")
                        continue
                    
                    eventos.append({
                        'tipo': 'ML',
                        'tempo': tempo
                    })
                # MU:tempo (Mutex Unlock)
                elif evento_str.startswith('MU:'):
                    tempo = int(evento_str[3:])
                    if tempo < 0:
                        self.avisos.append(f"Evento MU com tempo negativo: {evento_str}")
                        continue
                    eventos.append({
                        'tipo': 'MU',
                        'tempo': tempo
                    })
                else:
                    self.avisos.append(f"Tipo de evento desconhecido: {evento_str}")
            
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
        return {
            'valido': True,
            'algoritmo': self.config['algoritmo'],
            'quantum': self.config['quantum'],
            'total_tarefas': len(self.tasks),
            'duracao_total': sum(t.duracao for t in self.tasks),
            'avisos': len(self.avisos)
        }    

def criar_arquivo_exemplo(filename, algoritmo, quantum=1, num_tarefas=1):
    """
    Cria um arquivo de exemplo com configuração de tarefas.
    Retorna True se conseguiu criar.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{algoritmo};{quantum}\n")
        for i in range(num_tarefas):
            f.write(f"{i+1};#FF0000;0;1;1;\n")
    return True


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