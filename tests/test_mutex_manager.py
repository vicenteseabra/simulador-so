"""Testes para a classe MutexManager."""

import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mutex_manager import MutexManager


def test_basic_usage():
    """Testa fluxo básico de solicitação e liberação de mutex."""
    print("=" * 60)
    print("TEST: Basic Usage")
    print("=" * 60)

    mm = MutexManager()

    # Teste 1: t01 solicita mutex 01 (deve ser concedido)
    result = mm.solicitar_mutex('01', 't01')
    print(f"t01 solicita mutex 01: {result}")
    assert result == True, "Expected True (granted)"
    print(f"Estado: {mm}")
    print()

    # Teste 2: t02 solicita mutex 01 (deve ser enfileirado)
    result = mm.solicitar_mutex('01', 't02')
    print(f"t02 solicita mutex 01: {result}")
    assert result == False, "Expected False (queued)"
    print(f"Estado: {mm}")
    print()

    # Teste 3: t01 libera mutex 01 (t02 deve se tornar dono)
    next_owner = mm.liberar_mutex('01', 't01')
    print(f"t01 libera mutex 01, próximo dono: {next_owner}")
    assert next_owner == 't02', "Expected t02 to become owner"
    print(f"Estado: {mm}")
    print()

    # Teste 4: Verifica que t02 possui o mutex
    owns = mm.tarefa_possui_mutex('t02', '01')
    print(f"t02 possui mutex 01? {owns}")
    assert owns == True, "Expected t02 to own mutex 01"
    print()

    # Teste 5: Obtém donos dos mutexes
    owners = mm.obter_donos_mutex()
    print(f"Donos dos mutexes: {owners}")
    assert owners == {'01': 't02'}, "Expected only t02 as owner"
    print()

    print("✅ Test PASSED\n")


def test_multiple_waiting_tasks():
    """Testa múltiplas tarefas aguardando pelo mesmo mutex."""
    print("=" * 60)
    print("TEST: Multiple Waiting Tasks")
    print("=" * 60)

    mm = MutexManager()

    # t01 adquire mutex
    mm.solicitar_mutex('M1', 't01')
    print(f"t01 adquire M1")

    # t02, t03, t04 entram na fila
    mm.solicitar_mutex('M1', 't02')
    mm.solicitar_mutex('M1', 't03')
    mm.solicitar_mutex('M1', 't04')
    print(f"t02, t03, t04 entram na fila")
    print(f"Estado: {mm}")
    print()

    # Libera e verifica ordem
    next_owner = mm.liberar_mutex('M1', 't01')
    print(f"t01 libera M1, próximo: {next_owner}")
    assert next_owner == 't02', "Expected t02"

    next_owner = mm.liberar_mutex('M1', 't02')
    print(f"t02 libera M1, próximo: {next_owner}")
    assert next_owner == 't03', "Expected t03"

    next_owner = mm.liberar_mutex('M1', 't03')
    print(f"t03 libera M1, próximo: {next_owner}")
    assert next_owner == 't04', "Expected t04"

    next_owner = mm.liberar_mutex('M1', 't04')
    print(f"t04 libera M1, próximo: {next_owner}")
    assert next_owner is None, "Expected None (mutex free)"

    print(f"Estado final: {mm}")
    print()
    print("✅ Test PASSED\n")


def test_multiple_mutexes():
    """Testa múltiplos mutexes independentes."""
    print("=" * 60)
    print("TEST: Multiple Independent Mutexes")
    print("=" * 60)

    mm = MutexManager()

    # Diferentes tarefas adquirem diferentes mutexes
    mm.solicitar_mutex('M1', 't01')
    mm.solicitar_mutex('M2', 't02')
    mm.solicitar_mutex('M3', 't03')

    print(f"Estado: {mm}")
    print()

    owners = mm.obter_donos_mutex()
    print(f"Donos: {owners}")
    assert owners == {'M1': 't01', 'M2': 't02', 'M3': 't03'}

    # Verifica posse
    assert mm.tarefa_possui_mutex('t01', 'M1') == True
    assert mm.tarefa_possui_mutex('t01', 'M2') == False
    assert mm.tarefa_possui_mutex('t02', 'M2') == True
    print("Verificações de posse: OK")
    print()

    print("✅ Test PASSED\n")


def test_error_release_not_owned():
    """Testa erro ao liberar mutex não possuído."""
    print("=" * 60)
    print("TEST: Error - Release Not Owned Mutex")
    print("=" * 60)

    mm = MutexManager()

    mm.solicitar_mutex('M1', 't01')

    # Tenta liberar com tarefa errada
    try:
        mm.liberar_mutex('M1', 't02')
        print("❌ Expected ValueError but none was raised")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✅ ValueError raised correctly: {e}")

    print()
    print("✅ Test PASSED\n")


def test_error_release_nonexistent():
    """Testa erro ao liberar mutex inexistente."""
    print("=" * 60)
    print("TEST: Error - Release Nonexistent Mutex")
    print("=" * 60)

    mm = MutexManager()

    # Tenta liberar mutex que nunca foi criado
    try:
        mm.liberar_mutex('M99', 't01')
        print("❌ Expected ValueError but none was raised")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✅ ValueError raised correctly: {e}")

    print()
    print("✅ Test PASSED\n")


def test_reentrant_request():
    """Testa tarefa solicitando mutex que já possui."""
    print("=" * 60)
    print("TEST: Reentrant Request")
    print("=" * 60)

    mm = MutexManager()

    # t01 adquire mutex
    result = mm.solicitar_mutex('M1', 't01')
    print(f"t01 solicita M1: {result}")
    assert result == True

    # t01 solicita novamente (deve ainda retornar True)
    result = mm.solicitar_mutex('M1', 't01')
    print(f"t01 solicita M1 novamente: {result}")
    assert result == True

    # Verifica que a fila está vazia
    fila = mm.obter_fila_espera('M1')
    print(f"Fila de espera: {fila}")
    assert fila == [], "Queue should be empty"

    print()
    print("✅ Test PASSED\n")


def test_manual_scenario():
    """Executa o teste manual exato da descrição da task."""
    print("=" * 60)
    print("TEST: Manual Scenario from Task")
    print("=" * 60)

    mm = MutexManager()

    # mm.solicitar_mutex('01', 't01')  # True
    result1 = mm.solicitar_mutex('01', 't01')
    print(f"mm.solicitar_mutex('01', 't01'): {result1}")
    assert result1 == True, "Expected True"

    # mm.solicitar_mutex('01', 't02')  # False (bloqueado)
    result2 = mm.solicitar_mutex('01', 't02')
    print(f"mm.solicitar_mutex('01', 't02'): {result2}")
    assert result2 == False, "Expected False"

    # mm.liberar_mutex('01', 't01')    # t02 recebe automaticamente
    next_owner = mm.liberar_mutex('01', 't01')
    print(f"mm.liberar_mutex('01', 't01'): t02 recebe automaticamente")
    print(f"Próximo dono: {next_owner}")
    assert next_owner == 't02', "Expected t02 to receive mutex"

    # Verifica que t02 agora é dono
    assert mm.tarefa_possui_mutex('t02', '01') == True
    print(f"Verificação: t02 agora possui o mutex 01")

    print()
    print("✅ Test PASSED - Manual scenario works correctly!\n")


def run_all_tests():
    """Executa todos os testes."""
    print("\n")
    print("*" * 60)
    print("MUTEX MANAGER - TEST SUITE")
    print("*" * 60)
    print()

    test_basic_usage()
    test_multiple_waiting_tasks()
    test_multiple_mutexes()
    test_error_release_not_owned()
    test_error_release_nonexistent()
    test_reentrant_request()
    test_manual_scenario()

    print("*" * 60)
    print("ALL TESTS PASSED! ✅")
    print("*" * 60)
    print()


if __name__ == "__main__":
    run_all_tests()

