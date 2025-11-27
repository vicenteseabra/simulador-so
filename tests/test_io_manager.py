"""Testes para a classe IOManager."""

import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from io_manager import IOManager


def test_basic_usage():
    """Testa fluxo básico de iniciar I/O e verificar conclusões."""
    print("=" * 60)
    print("TEST: Basic Usage")
    print("=" * 60)

    io = IOManager()

    # Teste 1: Iniciar I/O
    tempo_conclusao = io.iniciar_io('t01', duracao=3, tempo_atual=5)
    print(f"io.iniciar_io('t01', duracao=3, tempo_atual=5)")
    print(f"Tempo de conclusão: {tempo_conclusao}")
    assert tempo_conclusao == 8, "Expected tempo_conclusao = 8"
    print(f"Estado: {io}")
    print()

    # Teste 2: Verificar conclusões antes do tempo
    conclusoes = io.verificar_conclusoes(tempo_atual=7)
    print(f"io.verificar_conclusoes(tempo_atual=7)")
    print(f"Conclusões: {conclusoes}")
    assert conclusoes == [], "Expected empty list"
    print()

    # Teste 3: Verificar conclusões no tempo exato
    conclusoes = io.verificar_conclusoes(tempo_atual=8)
    print(f"io.verificar_conclusoes(tempo_atual=8)")
    print(f"Conclusões: {conclusoes}")
    assert conclusoes == ['t01'], "Expected ['t01']"
    print(f"Estado: {io}")
    print()

    # Teste 4: Verificar que operação foi removida
    ativas = io.operacoes_ativas()
    print(f"Operações ativas: {ativas}")
    assert ativas == [], "Expected empty list"
    print()

    print("✅ Test PASSED\n")


def test_multiple_operations():
    """Testa múltiplas operações de I/O simultâneas."""
    print("=" * 60)
    print("TEST: Multiple Operations")
    print("=" * 60)

    io = IOManager()

    # Adiciona múltiplas operações
    io.iniciar_io('t01', duracao=3, tempo_atual=5)  # conclusão: 8
    io.iniciar_io('t02', duracao=5, tempo_atual=5)  # conclusão: 10
    io.iniciar_io('t03', duracao=2, tempo_atual=5)  # conclusão: 7

    print("Operações iniciadas:")
    print("  t01: conclusão no tempo 8")
    print("  t02: conclusão no tempo 10")
    print("  t03: conclusão no tempo 7")
    print(f"\nEstado: {io}")
    print()

    # Verifica ordenação
    ativas = io.operacoes_ativas()
    print(f"Operações ativas (ordenadas): {ativas}")
    assert ativas == [('t03', 7), ('t01', 8), ('t02', 10)], "Expected ordered list"
    print()

    # Verifica conclusão no tempo 7
    conclusoes = io.verificar_conclusoes(tempo_atual=7)
    print(f"Conclusões no tempo 7: {conclusoes}")
    assert conclusoes == ['t03'], "Expected ['t03']"
    print()

    # Verifica conclusão no tempo 8
    conclusoes = io.verificar_conclusoes(tempo_atual=8)
    print(f"Conclusões no tempo 8: {conclusoes}")
    assert conclusoes == ['t01'], "Expected ['t01']"
    print()

    # Verifica conclusão no tempo 10
    conclusoes = io.verificar_conclusoes(tempo_atual=10)
    print(f"Conclusões no tempo 10: {conclusoes}")
    assert conclusoes == ['t02'], "Expected ['t02']"
    print()

    # Verifica que todas foram removidas
    ativas = io.operacoes_ativas()
    print(f"Operações ativas finais: {ativas}")
    assert ativas == [], "Expected empty list"
    print()

    print("✅ Test PASSED\n")


def test_same_completion_time():
    """Testa múltiplas operações completando no mesmo tempo."""
    print("=" * 60)
    print("TEST: Same Completion Time")
    print("=" * 60)

    io = IOManager()

    # Adiciona operações que completam no mesmo tempo
    io.iniciar_io('t01', duracao=3, tempo_atual=5)  # conclusão: 8
    io.iniciar_io('t02', duracao=3, tempo_atual=5)  # conclusão: 8
    io.iniciar_io('t03', duracao=3, tempo_atual=5)  # conclusão: 8

    print("Todas as operações completam no tempo 8")
    print(f"Estado: {io}")
    print()

    # Verifica conclusão no tempo 8 (todas de uma vez)
    conclusoes = io.verificar_conclusoes(tempo_atual=8)
    print(f"Conclusões no tempo 8: {conclusoes}")
    assert len(conclusoes) == 3, "Expected 3 completions"
    assert set(conclusoes) == {'t01', 't02', 't03'}, "Expected all tasks"
    print()

    print("✅ Test PASSED\n")


def test_cancelar_io():
    """Testa cancelamento de operação de I/O."""
    print("=" * 60)
    print("TEST: Cancel I/O")
    print("=" * 60)

    io = IOManager()

    # Inicia operações
    io.iniciar_io('t01', duracao=3, tempo_atual=5)
    io.iniciar_io('t02', duracao=5, tempo_atual=5)

    print("Operações iniciadas: t01 e t02")
    print(f"Estado: {io}")
    print()

    # Cancela t01
    cancelado = io.cancelar_io('t01')
    print(f"io.cancelar_io('t01'): {cancelado}")
    assert cancelado == True, "Expected True"
    print(f"Estado: {io}")
    print()

    # Verifica que t01 foi removido
    ativas = io.operacoes_ativas()
    print(f"Operações ativas: {ativas}")
    assert ativas == [('t02', 10)], "Expected only t02"
    print()

    # Tenta cancelar t01 novamente
    cancelado = io.cancelar_io('t01')
    print(f"io.cancelar_io('t01') novamente: {cancelado}")
    assert cancelado == False, "Expected False"
    print()

    # Cancela operação inexistente
    cancelado = io.cancelar_io('t99')
    print(f"io.cancelar_io('t99'): {cancelado}")
    assert cancelado == False, "Expected False"
    print()

    print("✅ Test PASSED\n")


def test_replace_io():
    """Testa substituição de operação de I/O da mesma tarefa."""
    print("=" * 60)
    print("TEST: Replace I/O")
    print("=" * 60)

    io = IOManager()

    # Primeira operação
    tempo1 = io.iniciar_io('t01', duracao=3, tempo_atual=5)
    print(f"Primeira operação: t01, conclusão no tempo {tempo1}")
    print(f"Estado: {io}")
    print()

    # Segunda operação da mesma tarefa (substitui a primeira)
    tempo2 = io.iniciar_io('t01', duracao=5, tempo_atual=6)
    print(f"Segunda operação: t01, conclusão no tempo {tempo2}")
    print(f"Estado: {io}")
    print()

    # Verifica que há apenas uma operação para t01
    ativas = io.operacoes_ativas()
    print(f"Operações ativas: {ativas}")
    assert len(ativas) == 1, "Expected only one operation"
    assert ativas[0] == ('t01', 11), "Expected ('t01', 11)"
    print()

    # Verifica que não completa no tempo 8 (tempo da primeira operação)
    conclusoes = io.verificar_conclusoes(tempo_atual=8)
    print(f"Conclusões no tempo 8: {conclusoes}")
    assert conclusoes == [], "Expected empty list"
    print()

    # Verifica que completa no tempo 11 (tempo da segunda operação)
    conclusoes = io.verificar_conclusoes(tempo_atual=11)
    print(f"Conclusões no tempo 11: {conclusoes}")
    assert conclusoes == ['t01'], "Expected ['t01']"
    print()

    print("✅ Test PASSED\n")


def test_helper_methods():
    """Testa métodos auxiliares (tem_io_ativo, obter_tempo_conclusao)."""
    print("=" * 60)
    print("TEST: Helper Methods")
    print("=" * 60)

    io = IOManager()

    # Verifica tarefa sem I/O ativo
    tem_io = io.tem_io_ativo('t01')
    print(f"io.tem_io_ativo('t01'): {tem_io}")
    assert tem_io == False, "Expected False"
    print()

    # Obtém tempo de conclusão de tarefa sem I/O
    tempo = io.obter_tempo_conclusao('t01')
    print(f"io.obter_tempo_conclusao('t01'): {tempo}")
    assert tempo is None, "Expected None"
    print()

    # Inicia I/O
    io.iniciar_io('t01', duracao=3, tempo_atual=5)
    print("I/O iniciado para t01")
    print()

    # Verifica tarefa com I/O ativo
    tem_io = io.tem_io_ativo('t01')
    print(f"io.tem_io_ativo('t01'): {tem_io}")
    assert tem_io == True, "Expected True"
    print()

    # Obtém tempo de conclusão
    tempo = io.obter_tempo_conclusao('t01')
    print(f"io.obter_tempo_conclusao('t01'): {tempo}")
    assert tempo == 8, "Expected 8"
    print()

    # Verifica __len__
    tamanho = len(io)
    print(f"len(io): {tamanho}")
    assert tamanho == 1, "Expected 1"
    print()

    print("✅ Test PASSED\n")


def test_manual_scenario():
    """Executa o teste manual exato da descrição da task."""
    print("=" * 60)
    print("TEST: Manual Scenario from Task")
    print("=" * 60)

    io = IOManager()

    # io.iniciar_io('t01', duracao=3, tempo_atual=5)  # conclusão: 8
    tempo_conclusao = io.iniciar_io('t01', duracao=3, tempo_atual=5)
    print(f"io.iniciar_io('t01', duracao=3, tempo_atual=5)")
    print(f"Tempo de conclusão: {tempo_conclusao}")
    assert tempo_conclusao == 8, "Expected 8"
    print()

    # conclusoes = io.verificar_conclusoes(tempo_atual=8)  # ['t01']
    conclusoes = io.verificar_conclusoes(tempo_atual=8)
    print(f"io.verificar_conclusoes(tempo_atual=8)")
    print(f"Conclusões: {conclusoes}")
    assert conclusoes == ['t01'], "Expected ['t01']"
    print()

    print("✅ Test PASSED - Manual scenario works correctly!\n")


def test_verificar_conclusoes_future():
    """Testa verificar_conclusoes com tempo futuro (pega tudo)."""
    print("=" * 60)
    print("TEST: Verificar Conclusoes - Future Time")
    print("=" * 60)

    io = IOManager()

    # Adiciona várias operações
    io.iniciar_io('t01', duracao=3, tempo_atual=5)   # conclusão: 8
    io.iniciar_io('t02', duracao=5, tempo_atual=5)   # conclusão: 10
    io.iniciar_io('t03', duracao=10, tempo_atual=5)  # conclusão: 15

    print("Operações com conclusões em: 8, 10, 15")
    print(f"Estado: {io}")
    print()

    # Verifica conclusões em tempo muito futuro (pega todas)
    conclusoes = io.verificar_conclusoes(tempo_atual=100)
    print(f"io.verificar_conclusoes(tempo_atual=100)")
    print(f"Conclusões: {conclusoes}")
    assert len(conclusoes) == 3, "Expected 3 completions"
    assert set(conclusoes) == {'t01', 't02', 't03'}, "Expected all tasks"
    print()

    # Verifica que todas foram removidas
    ativas = io.operacoes_ativas()
    print(f"Operações ativas: {ativas}")
    assert ativas == [], "Expected empty list"
    print()

    print("✅ Test PASSED\n")


def run_all_tests():
    """Executa todos os testes."""
    print("\n")
    print("*" * 60)
    print("IO MANAGER - TEST SUITE")
    print("*" * 60)
    print()

    test_basic_usage()
    test_multiple_operations()
    test_same_completion_time()
    test_cancelar_io()
    test_replace_io()
    test_helper_methods()
    test_manual_scenario()
    test_verificar_conclusoes_future()

    print("*" * 60)
    print("ALL TESTS PASSED! ✅")
    print("*" * 60)
    print()


if __name__ == "__main__":
    run_all_tests()

