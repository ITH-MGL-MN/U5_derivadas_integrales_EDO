"""Corre las pruebas del repositorio desde cualquier carpeta.

    python tools/verificar.py

Sale con código 1 si alguna prueba falla, así que sirve en un script o en un
workflow.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main() -> int:
    """Descubre y ejecuta las pruebas de `tests/`."""
    sys.path.insert(0, str(RAIZ))
    descubiertas = unittest.defaultTestLoader.discover(str(RAIZ / "tests"))
    resultado = unittest.TextTestRunner(verbosity=2).run(descubiertas)
    if resultado.wasSuccessful():
        print("\nTodo en orden.")
        return 0
    print("\nHay pruebas fallando.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
