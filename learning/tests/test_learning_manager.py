from learning.domain.knowledge import KnowledgeItem
from learning.manager.learning_manager import LearningManager
from learning.repositories.memory_repository import InMemoryKnowledgeRepository


def test_learn():
    repo = InMemoryKnowledgeRepository()
    manager = LearningManager(repo)

    item = KnowledgeItem(
        title="Python",
        content="Python es un lenguaje."
    )

    manager.learn(item)

    assert repo.exists(item.id)


def test_remember():
    repo = InMemoryKnowledgeRepository()
    manager = LearningManager(repo)

    item = KnowledgeItem(
        title="FastAPI",
        content="Framework web."
    )

    manager.learn(item)

    result = manager.remember(item.id)

    assert result.title == "FastAPI"


def test_reinforce():
    repo = InMemoryKnowledgeRepository()
    manager = LearningManager(repo)

    item = KnowledgeItem(
        title="Docker",
        content="Contenedores"
    )

    manager.learn(item)

    before = item.confidence

    manager.reinforce(item.id)

    after = manager.remember(item.id).confidence

    assert after > before


def test_forget():
    repo = InMemoryKnowledgeRepository()
    manager = LearningManager(repo)

    item = KnowledgeItem(
        title="Eliminar",
        content="Prueba"
    )

    manager.learn(item)

    assert manager.forget(item.id) is True

    assert repo.exists(item.id) is False


def test_search():
    repo = InMemoryKnowledgeRepository()
    manager = LearningManager(repo)

    manager.learn(
        KnowledgeItem(
            title="Python",
            content="Lenguaje"
        )
    )

    manager.learn(
        KnowledgeItem(
            title="FastAPI",
            content="Framework Python"
        )
    )

    results = manager.search("python")

    assert len(results) == 2
