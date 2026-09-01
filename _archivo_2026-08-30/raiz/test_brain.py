from brain.brain import Brain

brain = Brain()

print("\n===== ARUS =====\n")

while True:
    pregunta = input("Tú: ")

    if pregunta.lower() in ("salir", "exit", "quit"):
        break

    respuesta = brain.think(pregunta)

    print("\nARUS:", respuesta)
    print()
