
## Clock - Documentação

### Visão Geral
O módulo `src/clock.py` define a classe `Clock`, que funciona como o relógio global e centralizado do simulador de Sistema Operacional. Ele gerencia o avanço do tempo da simulação, onde cada "tick" representa uma unidade discreta de tempo (ex: 1ms, 1 ciclo de CPU).

### Conceitos
- **Relógio (`Clock`)**: Classe que mantém e controla o tempo atual da simulação.
- **Tick**: Uma unidade de tempo da simulação, que avança o `tempo_atual` em $+1$.

### Classe `Clock`
Gerencia o tempo da simulação.

#### Atributos
- `tempo_atual` (int): O valor atual do tempo da simulação, iniciado em 0.

#### Métodos
- **`__init__(self)`**  
    Inicializa o relógio, definindo o `tempo_atual` como 0.  
    **Retorna:**  
    - `None`

- **`tick(self)`**  
    Avança o relógio em uma unidade de tempo (+1).  
    **Nota:** Este método também imprime uma mensagem de debug indicando o novo tempo.  
    **Retorna:**  
    - `None`

- **`get_tempo(self)`**  
    Retorna o valor atual do tempo do relógio.  
    **Retorna:**  
    - `int`: O tempo atual (`self.tempo_atual`).

- **`reset(self)`**  
    Reinicia o relógio, definindo o `tempo_atual` de volta para 0.  
    **Retorna:**  
    - `None`

---

### Exemplo de Uso
```python
relogio = Clock()
print(f"Tempo inicial: {relogio.get_tempo()}")  # Saída: 0

relogio.tick()  # Imprime [DEBUG] Tick -> tempo_atual = 1
relogio.tick()  # Imprime [DEBUG] Tick -> tempo_atual = 2
print(f"Tempo atual: {relogio.get_tempo()}")   # Saída: 2

relogio.reset()
print(f"Tempo após reset: {relogio.get_tempo()}") # Saída: 0
```
