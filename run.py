import sys
import os

# Añadimos la raíz absoluta del proyecto al principio del path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    from arus.main import main
    main()
