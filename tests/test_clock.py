import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.clock import Clock

clock = Clock()
print(clock.get_tempo())  # Esperado: 0
clock.tick()
print(clock.get_tempo())  # Esperado: 1
clock.tick()
print(clock.get_tempo())  # Esperado: 2
clock.reset()
print(clock.get_tempo())  # Esperado: 0
