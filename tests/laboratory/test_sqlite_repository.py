"""
ARUS
Fase 13
Test SQLite Laboratory Repository
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from arus.laboratory.managers import LaboratoryManager

print("=" * 60)
print("TEST SQLITE LABORATORY")
print("=" * 60)

manager = LaboratoryManager()

print("\n1. Creando laboratorio...")

lab = manager.create(
    "Laboratorio IA",
    "Laboratorio de pruebas",
)

print("OK")

print("\n2. Existe en SQLite:")

print(manager.repository.exists("Laboratorio IA"))

print("\n3. Listado:")

for row in manager.repository.list():
    print(dict(row))

print("\n4. Eliminando...")

manager.delete("Laboratorio IA")

print("OK")

print("\n5. Existe después de borrar:")

print(manager.repository.exists("Laboratorio IA"))

print("\nFIN TEST")
