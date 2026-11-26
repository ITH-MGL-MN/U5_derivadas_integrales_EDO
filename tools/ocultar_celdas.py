"""Marca como ocultas las celdas cuyo código el alumno no edita.

En Colab, una celda de código con `#@title` ya se muestra como un formulario
plegado. Lo que este archivo agrega es la marca de "celda oculta" en los
metadatos, para que las celdas de puro trámite (entorno, cuenta, calificar,
enviar) no estorben al recorrer el cuaderno.

La regla es por título (`#@title …`): se oculta la celda cuyo título empieza con
alguno de los prefijos de `OCULTAS`. Las celdas donde el alumno escribe o cambia
algo —las funciones, el número del ejercicio a mano, la ventana del filtro, el
método del caso— se quedan a la vista.

Uso:

    python tools/ocultar_celdas.py                 # todas las de notebooks/
    python tools/ocultar_celdas.py --solo 01
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nbformat

RAIZ = Path(__file__).resolve().parent.parent

# Prefijos de título que se ocultan. Son las celdas que el alumno ejecuta pero
# no modifica: si las edita, rompe el cuaderno.
OCULTAS = (
    "⚙️ 1.1 · Entorno",
    "🪪 1.2 · Cuenta",
    "📊 3.4 · Laboratorio",
    "📊 3.5 · Laboratorio",
    "🏭 5.1 · Tus datos",
    "🧮 6.1 · Calificar",
    "📤 6.2 · Enviar",
    "🔎 6.3 · Consultar",
)


def es_oculta(celda) -> bool:
    """Dice si una celda debe mostrarse plegada.

    Args:
        celda: una celda de nbformat.

    Returns:
        bool: `True` si es de código y su título está en `OCULTAS`.
    """
    if celda.cell_type != "code":
        return False
    primera = celda.source.strip().splitlines()[0] if celda.source.strip() else ""
    if not primera.startswith("#@title"):
        return False
    return primera.replace("#@title", "").strip().startswith(OCULTAS)


def marcar(cuaderno) -> int:
    """Pone o quita la marca de celda oculta según la regla.

    Args:
        cuaderno: un notebook de nbformat (se modifica en el lugar).

    Returns:
        int: cuántas celdas quedaron ocultas.
    """
    ocultas = 0
    for celda in cuaderno.cells:
        if es_oculta(celda):
            celda.metadata.setdefault("jupyter", {})["source_hidden"] = True
            ocultas += 1
        elif celda.cell_type == "code":
            celda.metadata.pop("jupyter", None)
            celda.metadata.pop("colab", None)
    return ocultas


def main(argv: list[str] | None = None) -> int:
    """Aplica la marca a los cuadernos de `notebooks/`."""
    analizador = argparse.ArgumentParser(description="Oculta las celdas de trámite.")
    analizador.add_argument("--solo", default=None,
                            help="Solo el cuaderno cuyo nombre contiene este texto (p. ej. 01).")
    opciones = analizador.parse_args(argv)

    for ruta in sorted((RAIZ / "notebooks").glob("*.ipynb")):
        if opciones.solo and opciones.solo not in ruta.name:
            continue
        cuaderno = nbformat.read(str(ruta), as_version=4)
        total = marcar(cuaderno)
        nbformat.write(cuaderno, str(ruta))
        print(f"  ✔ {ruta.name}: {total} celdas ocultas de {len(cuaderno.cells)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
