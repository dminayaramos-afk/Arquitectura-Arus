"""
ARUS — Fase 5
Tests de memoria especializada.
"""

from memory.memory_manager import MemoryManager


def test_semantic_memory():

    memory = MemoryManager()

    memory.remember_semantic(
        "color_favorito_test",
        "azul",
    )

    assert (
        memory.recall_semantic(
            "color_favorito_test"
        )
        == "azul"
    )


def test_semantic_memory_complex_value():

    memory = MemoryManager()

    value = {
        "language": "Python",
        "version": 3,
        "tags": ["ai", "arus"],
    }

    memory.remember_semantic(
        "project_test",
        value,
    )

    assert (
        memory.recall_semantic(
            "project_test"
        )
        == value
    )


def test_user_preferences():

    memory = MemoryManager()

    memory.set_preference(
        "theme_test",
        "dark",
    )

    assert (
        memory.get_preference(
            "theme_test"
        )
        == "dark"
    )


def test_user_preferences_default():

    memory = MemoryManager()

    assert (
        memory.get_preference(
            "does_not_exist_test",
            "default",
        )
        == "default"
    )


def test_task_memory():

    memory = MemoryManager()

    task = memory.add_task(
        "test_task",
        {"value": 42},
    )

    assert task.name == "test_task"
    assert task.status == "pending"
    assert task.arguments["value"] == 42

    assert task in memory.tasks.pending()


def test_task_completion():

    memory = MemoryManager()

    task = memory.add_task(
        "completion_test",
    )

    memory.tasks.complete(
        task,
        "OK",
    )

    assert task.status == "done"
    assert task.result == "OK"
    assert task in memory.tasks.completed()
