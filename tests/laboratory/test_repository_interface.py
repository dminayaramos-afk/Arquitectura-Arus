"""
ARUS
Test Repository Interface
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))


from arus.laboratory.repositories import (
    SQLiteLaboratoryRepository
)

from arus.laboratory.interfaces import (
    LaboratoryRepository
)


print("="*60)
print("TEST REPOSITORY INTERFACE")
print("="*60)


repo = SQLiteLaboratoryRepository()


assert isinstance(
    repo,
    LaboratoryRepository
)


print("✓ SQLite cumple interfaz")

repo.close()

print("FIN")
