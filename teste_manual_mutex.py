"""Teste manual exato conforme especificado na TASK B1.2"""

import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mutex_manager import MutexManager

print("=" * 70)
print("TESTE MANUAL - TASK B1.2")
print("=" * 70)
print()

# Criar o MutexManager
mm = MutexManager()
print("✅ mm = MutexManager()")
print()

# Teste 1: t01 solicita mutex 01
print(">>> mm.solicitar_mutex('01', 't01')")
result1 = mm.solicitar_mutex('01', 't01')
print(f"Resultado: {result1}")
print(f"Esperado: True")
print(f"Status: {'✅ PASSOU' if result1 == True else '❌ FALHOU'}")
print()

# Teste 2: t02 solicita mutex 01 (bloqueado)
print(">>> mm.solicitar_mutex('01', 't02')")
result2 = mm.solicitar_mutex('01', 't02')
print(f"Resultado: {result2}")
print(f"Esperado: False (bloqueado)")
print(f"Status: {'✅ PASSOU' if result2 == False else '❌ FALHOU'}")
print()

# Estado atual
print("Estado atual do MutexManager:")
print(mm)
print()

# Teste 3: t01 libera mutex 01 (t02 recebe automaticamente)
print(">>> mm.liberar_mutex('01', 't01')")
next_owner = mm.liberar_mutex('01', 't01')
print(f"Próximo dono: {next_owner}")
print(f"Esperado: t02 recebe automaticamente")
print(f"Status: {'✅ PASSOU' if next_owner == 't02' else '❌ FALHOU'}")
print()

# Verificar que t02 agora possui o mutex
owns = mm.tarefa_possui_mutex('t02', '01')
print(f"Verificação: t02 possui mutex 01? {owns}")
print(f"Status: {'✅ PASSOU' if owns == True else '❌ FALHOU'}")
print()

# Estado final
print("Estado final do MutexManager:")
print(mm)
print()

# Resumo
print("=" * 70)
if result1 == True and result2 == False and next_owner == 't02' and owns == True:
    print("✅✅✅ TESTE MANUAL COMPLETO: TODOS OS REQUISITOS ATENDIDOS! ✅✅✅")
else:
    print("❌ TESTE FALHOU")
print("=" * 70)

