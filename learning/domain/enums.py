from enum import Enum


class KnowledgeType(str, Enum):
    WORKING = "working"
    LONG_MEMORY = "long_memory"
    KNOWLEDGE_BASE = "knowledge_base"
    LEARNED = "learned"
    USER = "user"
    EXPERIENCE = "experience"


class KnowledgeSource(str, Enum):
    USER = "user"
    DOCUMENT = "document"
    PROJECT = "project"
    ERROR = "error"
    TOOL = "tool"
    AGENT = "agent"
    SYSTEM = "system"
    IMPORT = "import"


class RelationType(str, Enum):
    RELATED_TO = "related_to"
    USES = "uses"
    REQUIRES = "requires"
    DEPENDS_ON = "depends_on"
    CONTAINS = "contains"
    FIXES = "fixes"
    LEARNED_FROM = "learned_from"
    GENERATED_FROM = "generated_from"
