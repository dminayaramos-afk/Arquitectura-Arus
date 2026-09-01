"""
ARUS
Test carga desde SQLite
"""

from arus.laboratory.managers import LaboratoryManager

print("=" * 60)
print("TEST LOAD SQLITE")
print("=" * 60)

manager = LaboratoryManager()

# Limpiar si existe
if manager.repository.exists("Laboratorio IA"):
    manager.repository.delete("Laboratorio IA")

print("\n1. Crear laboratorio")
lab = manager.create(
    "Laboratorio IA",
    "Persistencia SQLite"
)
print("OK")

print("\n2. Nuevo manager")
manager2 = LaboratoryManager()

print("\n3. Cargando desde SQLite")
lab2 = manager2.load("Laboratorio IA")

if lab2 is None:
    print("ERROR")
else:
    print("OK")
    print(lab2.info())

print("\n4. Limpiando")
manager2.delete("Laboratorio IA")

print("FIN")
