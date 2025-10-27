class Clock:
    """
    Relógio global do simulador.

    Cada tick representa uma unidade de tempo da CPU (ex: 1ms, 1 ciclo, etc).
    """

    def __init__(self):
        """Inicializa o relógio com tempo 0."""
        self.tempo_atual = 0

    def tick(self):
        """Avança o relógio em uma unidade de tempo."""
        self.tempo_atual += 1

    def get_tempo(self):
        """Retorna o tempo atual do relógio."""
        return self.tempo_atual

    def reset(self):
        """Reinicia o relógio para 0."""
        self.tempo_atual = 0