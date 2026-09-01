class LearningError(Exception):
    """Excepción base del sistema de aprendizaje."""


class KnowledgeNotFoundError(LearningError):
    """El conocimiento solicitado no existe."""


class DuplicateKnowledgeError(LearningError):
    """El conocimiento ya existe."""


class InvalidKnowledgeError(LearningError):
    """El conocimiento no es válido."""


class RepositoryError(LearningError):
    """Error producido por un repositorio."""


class MemoryError(LearningError):
    """Error relacionado con la memoria."""


class RelationError(LearningError):
    """Error relacionado con las relaciones de conocimiento."""
