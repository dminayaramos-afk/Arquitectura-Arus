from learning.domain.knowledge import KnowledgeItem
from learning.repositories.memory_repository import InMemoryKnowledgeRepository


def test_save_and_get():
    repo = InMemoryKnowledgeRepository()

    item = KnowledgeItem(
        title="ARUS",
        content="Artificial Reasoning Unified"
    )

    repo.save(item)

    recovered = repo.get(item.id)

    assert recovered is not None
    assert recovered.id == item.id
    assert recovered.title == "ARUS"


def test_exists():
    repo = InMemoryKnowledgeRepository()

    item = KnowledgeItem(
        title="Python",
        content="Lenguaje"
    )

    repo.save(item)

    assert repo.exists(item.id)


def test_update():
    repo = InMemoryKnowledgeRepository()

    item = KnowledgeItem(
        title="Docker",
        content="Contenedores"
    )

    repo.save(item)

    item.title = "Docker Engine"

    repo.update(item)

    assert repo.get(item.id).title == "Docker Engine"


def test_delete():
    repo = InMemoryKnowledgeRepository()

    item = KnowledgeItem(
        title="Eliminar",
        content="Test"
    )

    repo.save(item)

    assert repo.delete(item.id)

    assert not repo.exists(item.id)


def test_clear():
    repo = InMemoryKnowledgeRepository()

    repo.save(KnowledgeItem(title="A"))
    repo.save(KnowledgeItem(title="B"))

    assert len(repo.list()) == 2

    repo.clear()

    assert len(repo.list()) == 0
