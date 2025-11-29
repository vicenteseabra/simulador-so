#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Teste simples da SchedulerFactory
try:
    from scheduler import SchedulerFactory, PrioridadeEnvScheduler
    print("✅ Import realizado com sucesso")

    # Teste 1: Criar scheduler PRIOPEnv com parâmetros completos
    scheduler = SchedulerFactory.criar_scheduler('PRIOPEnv', quantum=5, alpha=1.0)
    print(f"✅ Scheduler criado: {scheduler.__class__.__name__}")
    print(f"   Quantum: {scheduler.quantum}")
    print(f"   Alpha: {scheduler.alpha}")

    # Teste 2: Criar scheduler PRIOPEnv com alpha padrão
    scheduler2 = SchedulerFactory.criar_scheduler('PRIOPEnv', quantum=3)
    print(f"✅ Scheduler com alpha padrão: alpha={scheduler2.alpha}")

    # Teste 3: Testar case-insensitive
    scheduler3 = SchedulerFactory.criar_scheduler('priopenv', quantum=2, alpha=0.5)
    print(f"✅ Case-insensitive funcionou: alpha={scheduler3.alpha}")

    # Teste 4: Tentar sem quantum (deve dar erro)
    try:
        SchedulerFactory.criar_scheduler('PRIOPEnv')
        print("❌ Deveria ter dado erro!")
    except ValueError as e:
        print(f"✅ Validação funcionou: {e}")

    # Teste 5: Outros algoritmos ainda funcionam
    fifo = SchedulerFactory.criar_scheduler('FIFO')
    print(f"✅ FIFO ainda funciona: {fifo.__class__.__name__}")

    print("\n🎉 Todos os testes passaram!")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
