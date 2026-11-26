"""Mostrar texto con formato y recoger respuestas del alumno.

Todo lo que el cuaderno enseña pasa por aquí, para que las ecuaciones y las
tablas se vean como tales y no como texto plano con símbolos raros.

- `mostrar(texto)`: pinta markdown (con LaTeX) en el cuaderno; fuera de un
  cuaderno lo imprime tal cual.
- `titulo(texto)`: un encabezado de sección.
- `elegir(cantidad, al_responder)`: botones de opción (o casillas, si se piden
  varias) con los números 1..cantidad. Devuelve `False` si no hay cuaderno y el
  llamador tiene que preguntar de otra forma.

Este archivo no califica nada: solo presenta y recoge.
"""

from __future__ import annotations

__all__ = ["hay_cuaderno", "mostrar", "titulo", "elegir"]


def hay_cuaderno() -> bool:
    """Dice si estamos dentro de un cuaderno (Jupyter o Colab).

    Returns:
        bool: `True` si hay un kernel interactivo, que es donde se pueden
        pintar widgets y markdown.
    """
    try:
        from IPython import get_ipython

        consola = get_ipython()
    except ImportError:
        return False
    return consola is not None and consola.__class__.__name__ in (
        "ZMQInteractiveShell", "Shell", "google.colab._shell.Shell"
    )


def mostrar(texto: str) -> None:
    """Pinta un texto en markdown, con sus ecuaciones y tablas.

    Args:
        texto: markdown; admite `$...$` y `$$...$$` de LaTeX.
    """
    if hay_cuaderno():
        from IPython.display import Markdown, display

        display(Markdown(texto))
    else:
        print(texto)


def titulo(texto: str) -> None:
    """Pinta un encabezado de sección.

    Args:
        texto: el título, sin almohadillas.
    """
    mostrar(f"#### {texto}")


def elegir(cantidad: int, al_responder, varias: bool = False) -> bool:
    """Muestra botones numerados y avisa cuando el alumno responde.

    Args:
        cantidad: cuántas opciones hay (se numeran de 1 a `cantidad`).
        al_responder: función que recibe el número elegido, o la lista de
            números si `varias` es `True`.
        varias: si se pueden marcar varias opciones (casillas en vez de
            botones de opción).

    Returns:
        bool: `True` si se pintaron los controles, `False` si no hay cuaderno
        interactivo y el llamador debe preguntar de otra manera.
    """
    if not hay_cuaderno():
        return False
    try:
        import ipywidgets as widgets
        from IPython.display import clear_output, display
    except ImportError:
        return False

    numeros = [str(numero) for numero in range(1, cantidad + 1)]

    if varias:
        casillas = [
            widgets.Checkbox(value=False, description=numero, indent=False,
                             layout=widgets.Layout(width="80px"))
            for numero in numeros
        ]
        control = widgets.HBox(casillas)

        def _valor():
            return [indice for indice, casilla in enumerate(casillas, start=1) if casilla.value]

        def _bloquear():
            for casilla in casillas:
                casilla.disabled = True
    else:
        control = widgets.RadioButtons(
            options=[(numero, numero) for numero in numeros],
            value=None,
            layout=widgets.Layout(width="220px"),
        )
        control.style = {"description_width": "initial"}

        def _valor():
            return int(control.value) if control.value is not None else None

        def _bloquear():
            control.disabled = True

    boton = widgets.Button(description="Responder", button_style="primary")
    aviso = widgets.Output()

    def _al_pulsar(_boton):
        elegido = _valor()
        if not elegido:
            with aviso:
                clear_output()
                mostrar("_Elige una opción antes de responder._")
            return
        _bloquear()
        boton.disabled = True
        with aviso:
            clear_output()
            al_responder(elegido)

    boton.on_click(_al_pulsar)
    display(widgets.VBox([control, boton, aviso]))
    return True
