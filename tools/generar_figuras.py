"""Extrae las figuras del libro al repositorio, siguiendo el manifiesto.

Las imágenes del libro **no** se versionan en el repositorio del curso: se
copian aquí una vez, se revisan y luego se publican en `docs/figuras/libro/`
con su atribución. Este script es la única forma de producirlas, para que el
nombre de cada archivo siempre diga qué figura es.

Uso:

    python tools/generar_figuras.py --fuente "C:/ruta/a/Contenido/Markdown/Ed7"
    python tools/generar_figuras.py --fuente ... --forzar     # rehace las que ya existen

El manifiesto `docs/figuras/libro/manifest.csv` tiene una fila por figura:

    archivo_destino, capitulo, pagina, indice, numero_libro, pie, cuaderno

donde `pagina` es la carpeta `page_XXXX` del capítulo e `indice` es el número
del archivo dentro de ella. La ruta de origen queda como

    <fuente>/P6_23_Diferenciacion_numerica_images/page_0006/0.jpg

y el destino como `docs/figuras/libro/<archivo_destino>`, siempre en PNG
(aunque el original sea JPEG, para que el visor de GitHub no adivine el tipo).
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
MANIFIESTO = RAIZ / "docs" / "figuras" / "libro" / "manifest.csv"
DESTINO = RAIZ / "docs" / "figuras" / "libro"


def _carpeta_de_capitulo(capitulo: str) -> str:
    """Nombre de la carpeta de imágenes de un capítulo.

    Args:
        capitulo: número del tema del libro, por ejemplo `"23"`.

    Returns:
        str: el prefijo que hay que buscar, por ejemplo `"P6_23_"`.
    """
    parte = "P6" if int(capitulo) < 25 else "P7"
    return f"{parte}_{capitulo}_"


def localizar(fuente: Path, capitulo: str, pagina: str, indice: str) -> Path:
    """Encuentra el archivo de origen de una figura.

    Args:
        fuente: carpeta `Ed7` del libro convertido.
        capitulo: número del tema, por ejemplo `"23"`.
        pagina: carpeta de página, por ejemplo `"page_0006"`.
        indice: nombre del archivo sin extensión, por ejemplo `"0"`.

    Returns:
        Path: el archivo de origen.

    Raises:
        FileNotFoundError: si no hay carpeta del capítulo o archivo que
            coincida con esa página e índice.
    """
    prefijo = _carpeta_de_capitulo(capitulo)
    candidatas = [ruta for ruta in fuente.glob(prefijo + "*_images") if ruta.is_dir()]
    if not candidatas:
        raise FileNotFoundError(f"No encuentro la carpeta de imágenes del capítulo {capitulo} en {fuente}.")
    for carpeta in candidatas:
        for extension in (".jpg", ".jpeg", ".png"):
            archivo = carpeta / pagina / (indice + extension)
            if archivo.exists():
                return archivo
    raise FileNotFoundError(
        f"No encuentro {pagina}/{indice} en {candidatas[0].name}; "
        "revisa la columna pagina del manifiesto."
    )


def convertir(origen: Path, destino: Path) -> None:
    """Copia una figura a PNG, sin recortes ni realces.

    Args:
        origen: archivo del libro (JPEG o PNG).
        destino: archivo de salida en PNG.
    """
    with Image.open(origen) as imagen:
        imagen.convert("RGB").save(destino, "PNG", optimize=True)


def main(argv: list[str] | None = None) -> int:
    """Recorre el manifiesto y produce las figuras que falten."""
    analizador = argparse.ArgumentParser(description="Extrae las figuras del libro.")
    analizador.add_argument("--fuente", required=True, type=Path,
                            help="Carpeta Ed7 con los .md y las carpetas *_images.")
    analizador.add_argument("--forzar", action="store_true",
                            help="Vuelve a generar las figuras que ya existen.")
    opciones = analizador.parse_args(argv)

    if not MANIFIESTO.exists():
        print(f"Falta el manifiesto: {MANIFIESTO}")
        return 1

    with open(MANIFIESTO, encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))

    hechas, saltadas, falladas = 0, 0, 0
    for fila in filas:
        destino = DESTINO / fila["archivo_destino"].strip()
        if destino.exists() and not opciones.forzar:
            saltadas += 1
            continue
        try:
            origen = localizar(opciones.fuente, fila["capitulo"].strip(),
                               fila["pagina"].strip(), fila["indice"].strip())
            convertir(origen, destino)
            print(f"  ✔ {destino.name}  (de {origen.parent.name}/{origen.name})")
            hechas += 1
        except FileNotFoundError as exc:
            print(f"  ✘ {destino.name}: {exc}")
            falladas += 1

    print(f"\n{hechas} generadas, {saltadas} ya existían, {falladas} con problema.")
    return 1 if falladas else 0


if __name__ == "__main__":
    sys.exit(main())
