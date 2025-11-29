"""Testes para ConfigParser atualizado com eventos."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config_parser import ConfigParser
from events import IOEvent, MutexLockEvent, MutexUnlockEvent
import tempfile
import os


def test_priopenv_format():
    """Testa parse do formato PRIOPEnv com alpha."""
    print("=" * 60)
    print("TEST: PRIOPEnv Format")
    print("=" * 60)

    content = """PRIOPEnv;5;1.5
t01;#FF0000;0;3;2;
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_file = f.name

    try:
        parser = ConfigParser()
        config, tasks = parser.parse_file(temp_file)

        print(f"Algoritmo: {config['algoritmo']}")
        print(f"Quantum: {config['quantum']}")
        print(f"Alpha: {config['alpha']}")

        assert config['algoritmo'] == 'PRIOPENV'
        assert config['quantum'] == 5
        assert config['alpha'] == 1.5

    finally:
        os.unlink(temp_file)

    print("✅ Test PASSED\n")


def test_eventos_parsing():
    """Testa parse de eventos no novo formato."""
    print("=" * 60)
    print("TEST: Eventos Parsing")
    print("=" * 60)

    content = """FIFO;1
t01;#FF0000;0;5;2;IO:2-1;ML01:1;MU01:4
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_file = f.name

    try:
        parser = ConfigParser()
        config, tasks = parser.parse_file(temp_file)

        task = tasks[0]
        eventos = task.eventos

        print(f"Total eventos: {len(eventos)}")

        # IO Event
        io_event = eventos[0]
        print(f"Evento 1: {type(io_event).__name__} - tempo={io_event.tempo_relativo}, duracao={io_event.duracao}")
        assert isinstance(io_event, IOEvent)
        assert io_event.tempo_relativo == 2
        assert io_event.duracao == 1
        assert io_event.task_id == 't01'

        # Mutex Lock Event
        ml_event = eventos[1]
        print(f"Evento 2: {type(ml_event).__name__} - tempo={ml_event.tempo_relativo}, mutex_id={ml_event.mutex_id}")
        assert isinstance(ml_event, MutexLockEvent)
        assert ml_event.tempo_relativo == 1
        assert ml_event.mutex_id == '01'
        assert ml_event.task_id == 't01'

        # Mutex Unlock Event
        mu_event = eventos[2]
        print(f"Evento 3: {type(mu_event).__name__} - tempo={mu_event.tempo_relativo}, mutex_id={mu_event.mutex_id}")
        assert isinstance(mu_event, MutexUnlockEvent)
        assert mu_event.tempo_relativo == 4
        assert mu_event.mutex_id == '01'
        assert mu_event.task_id == 't01'

    finally:
        os.unlink(temp_file)

    print("✅ Test PASSED\n")


def test_invalid_eventos():
    """Testa tratamento de eventos inválidos."""
    print("=" * 60)
    print("TEST: Invalid Eventos")
    print("=" * 60)

    content = """FIFO;1
t01;#FF0000;0;3;1;IO:2;ML:1;INVALID:3
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_file = f.name

    try:
        parser = ConfigParser()
        config, tasks = parser.parse_file(temp_file)

        avisos = parser.obter_avisos()
        print(f"Avisos gerados: {len(avisos)}")
        for aviso in avisos:
            print(f"  - {aviso}")

        # Deve ter avisos para eventos malformados
        assert len(avisos) > 0

        # Mas ainda deve ter criado a tarefa
        assert len(tasks) == 1

    finally:
        os.unlink(temp_file)

    print("✅ Test PASSED\n")


def test_example_file():
    """Testa arquivo de exemplo criado."""
    print("=" * 60)
    print("TEST: Example File")
    print("=" * 60)

    example_file = Path(__file__).parent.parent / "examples" / "config_priopenv.txt"

    parser = ConfigParser()
    config, tasks = parser.parse_file(str(example_file))

    print(f"Config: {config}")
    print(f"Total tarefas: {len(tasks)}")

    assert config['algoritmo'] == 'PRIOPENV'
    assert config['quantum'] == 2
    assert config['alpha'] == 1
    assert len(tasks) == 3

    # Verifica primeira tarefa
    t01 = tasks[0]
    assert t01.id == 't01'
    assert len(t01.eventos) == 3

    print("✅ Test PASSED\n")


def test_resumo_with_alpha():
    """Testa resumo incluindo alpha."""
    print("=" * 60)
    print("TEST: Resumo with Alpha")
    print("=" * 60)

    content = """PRIOPEnv;3;0.5
t01;#FF0000;0;2;1;
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_file = f.name

    try:
        parser = ConfigParser()
        config, tasks = parser.parse_file(temp_file)
        resumo = parser.obter_resumo()

        print(f"Resumo: {resumo}")

        assert resumo['alpha'] == 0.5
        assert resumo['algoritmo'] == 'PRIOPENV'
        assert resumo['quantum'] == 3

    finally:
        os.unlink(temp_file)

    print("✅ Test PASSED\n")


def run_all_tests():
    """Executa todos os testes."""
    print("\n")
    print("*" * 60)
    print("CONFIG PARSER - EVENTOS - TEST SUITE")
    print("*" * 60)
    print()

    test_priopenv_format()
    test_eventos_parsing()
    test_invalid_eventos()
    test_example_file()
    test_resumo_with_alpha()

    print("*" * 60)
    print("ALL TESTS PASSED! ✅")
    print("*" * 60)
    print()


if __name__ == "__main__":
    run_all_tests()
