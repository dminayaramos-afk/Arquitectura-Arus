
"""
ARUS
Fase 13
Repository Contract Test
"""

from arus.laboratory.repositories import SQLiteLaboratoryRepository
from arus.laboratory.interfaces import LaboratoryRepository
from arus.laboratory.models import Laboratory


print("="*60)
print("TEST REPOSITORY CONTRACT")
print("="*60)


repo = SQLiteLaboratoryRepository(
    "database/test_repository.db"
)


print("\n1. Interface")

assert isinstance(
    repo,
    LaboratoryRepository
)

print("OK")


print("\n2. Crear laboratorio")

lab = Laboratory(
    name="Repository Test",
    description="Contrato SQLite"
)


repo.save(lab)

print("OK")


print("\n3. Existe")

assert repo.exists(
    "Repository Test"
)

print("OK")


print("\n4. Obtener")

row = repo.get(
    "Repository Test"
)

assert row["name"] == "Repository Test"

print("OK")


print("\n5. Listar")

items = repo.list()

assert len(items) > 0

print("OK")


print("\n6. Load")

loaded = repo.load(
    "Repository Test",
    Laboratory
)

assert loaded.name == "Repository Test"

print("OK")


print("\n7. Delete")

repo.delete(
    "Repository Test"
)

assert not repo.exists(
    "Repository Test"
)

print("OK")


repo.close()


print("\n================================")
print("✓ REPOSITORY CONTRACT OK")
print("================================")
