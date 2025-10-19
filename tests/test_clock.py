from src.clock import Clock

clock = Clock()
print(clock.get_tempo())  # Esperado: 0
clock.tick()
print(clock.get_tempo())  # Esperado: 1
clock.tick()
print(clock.get_tempo())  # Esperado: 2
clock.reset()
print(clock.get_tempo())  # Esperado: 0
