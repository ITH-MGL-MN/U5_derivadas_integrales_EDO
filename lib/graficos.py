"""Laboratorios gráficos de la Unidad 5.

Un laboratorio dibuja un método, lo compara con el resultado exacto y con la
función equivalente de NumPy, y muestra **cómo cambia el error al refinar**.
Esa última gráfica es la que responde "¿qué método uso?" mejor que cualquier
párrafo.

Este archivo no califica ni conoce al alumno: es material de consulta. Cada
laboratorio está escrito completo, aunque repita el armado de la figura, para
que se pueda leer de arriba abajo sin saltar a otra función.

Uso desde el cuaderno:

    from graficos import laboratorio
    laboratorio("derivada_centrada")

    # o con otro ejemplo:
    laboratorio("derivada_centrada", {"f": ..., "df": ..., "a": 0.0, "b": 2.0})
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

try:
    from pantalla import mostrar
except ImportError:                     # fuera del repositorio, sin lib/ en la ruta
    def mostrar(texto: str) -> None:
        """Respaldo: imprime el texto tal cual."""
        print(texto)

__all__ = ["laboratorio"]

# Ejemplo del libro (23.1). Se usa cuando el cuaderno no pasa otro.
_EJEMPLO_LIBRO = {
    "nombre": "f(x) = -0.1x⁴ - 0.15x³ - 0.5x² - 0.25x + 1.2",
    "f": lambda x: -0.1 * x**4 - 0.15 * x**3 - 0.5 * x**2 - 0.25 * x + 1.2,
    "df": lambda x: -0.4 * x**3 - 0.45 * x**2 - 1.0 * x - 0.25,
    "a": 0.2,
    "b": 1.2,
    "n": 11,
    "x0": 0.5,
}

_MALLAS = (4, 8, 16, 32, 64, 128)


def laboratorio(clave: str, ejemplo: dict | None = None) -> dict:
    """Dibuja el laboratorio de un método de la unidad.

    Args:
        clave: nombre del método; debe existir la función `_lab_<clave>`.
        ejemplo: diccionario con `f`, `df`, `a`, `b`, `n` y, si se quiere,
            `x0` y `nombre`. Si se omite, se usa el ejemplo 23.1 del libro.

    Returns:
        dict: `{"error_refinado": ..., "pendiente": ...}` con el error máximo
        en la malla más fina y la pendiente ajustada de la gráfica log-log
        (1.0 para un método de primer orden, 2.0 para uno de segundo).

    Raises:
        KeyError: si `clave` no tiene laboratorio.
    """
    disponible = {nombre: valor for nombre, valor in globals().items() if nombre.startswith("_lab_")}
    funcion = disponible.get("_lab_" + clave)
    if funcion is None:
        raise KeyError(
            f"No hay laboratorio para {clave!r}. Los disponibles son: "
            + ", ".join(sorted(nombre[5:] for nombre in disponible))
        )
    datos = dict(_EJEMPLO_LIBRO)
    datos.update(ejemplo or {})
    return funcion(datos)


def _malla(datos: dict, n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Construye la malla de muestras y los valores exactos.

    Args:
        datos: el ejemplo en uso.
        n: número de intervalos.

    Returns:
        tuple: `(x, y, df_exacta)`, todos del mismo tamaño (`n + 1`).
    """
    x = np.linspace(datos["a"], datos["b"], n + 1)
    return x, datos["f"](x), datos["df"](x)


def _pendiente(nj: np.ndarray, errores: np.ndarray) -> float:
    """Pendiente de la recta que mejor ajusta `log(error)` contra `log(h)`.

    Args:
        nj: número de intervalos de cada corrida.
        errores: error máximo de cada corrida.

    Returns:
        float: la pendiente; 1.0 significa error O(h), 2.0 significa O(h²).
    """
    return float(np.polyfit(np.log(1.0 / nj), np.log(errores), 1)[0])


def _estilo(eje, titulo: str, xlabel: str, ylabel: str) -> None:
    """Deja un eje presentable sin repetir la configuración en cada panel."""
    eje.set_title(titulo, fontsize=10)
    eje.set_xlabel(xlabel)
    eje.set_ylabel(ylabel)
    eje.grid(alpha=0.3)


def _lab_derivada_atras(datos: dict) -> dict:
    """Laboratorio de la diferencia hacia atrás (figura 23.2).

    Tres paneles: la secante hacia atrás sobre la señal, la derivada estimada
    contra la exacta y la de `np.gradient`, y el error contra el tamaño de paso
    en escala logarítmica.

    Args:
        datos: el ejemplo en uso.

    Returns:
        dict: `{"error_refinado", "pendiente"}` del método.
    """
    x, y, df_exacta = _malla(datos, datos["n"])
    h = x[1] - x[0]
    x0 = datos["x0"]
    i0 = int(np.argmin(np.abs(x - x0)))

    atras = (y[i0] - y[i0 - 1]) / (x[i0] - x[i0 - 1])
    centrada = (y[i0 + 1] - y[i0 - 1]) / (x[i0 + 1] - x[i0 - 1])

    figura, (eje1, eje2, eje3) = plt.subplots(1, 3, figsize=(13, 3.6))

    eje1.plot(x, y, "o-", lw=1, ms=4, label="muestras")
    eje1.plot([x[i0 - 1], x[i0]], [y[i0 - 1], y[i0]], "r-", lw=2, label="secante hacia atrás")
    eje1.plot(x[i0], y[i0], "ks", ms=7)
    eje1.set_title(f"1) Secante hacia atrás en x = {x[i0]:.2f}", fontsize=10)
    eje1.legend(fontsize=8)
    _estilo(eje1, "La señal y la secante", "x", "f(x)")

    estimada = np.full_like(x, np.nan)
    estimada[1:] = np.diff(y) / np.diff(x)
    eje2.plot(x, df_exacta, "k-", lw=2, label="exacta")
    eje2.plot(x, estimada, "r--", lw=1.5, label="atrás")
    eje2.plot(x, np.gradient(y, x), "b:", lw=1.5, label="np.gradient")
    _estilo(eje2, "Estimación contra la derivada exacta", "x", "f'(x)")
    eje2.legend(fontsize=8)

    errores = []
    for n in _MALLAS:
        xs, ys, exacta = _malla(datos, n)
        aproximada = np.full_like(ys, np.nan)
        aproximada[1:] = np.diff(ys) / np.diff(xs)
        errores.append(float(np.nanmax(np.abs(aproximada - exacta))))
    pendiente = _pendiente(np.array(_MALLAS, dtype=float), np.array(errores))
    eje3.loglog(_MALLAS, errores, "ro-", label=f"atrás (pendiente ≈ {pendiente:.2f})")
    eje3.loglog(_MALLAS, errores[0] * (np.array(_MALLAS, dtype=float) ** -1), "k:", lw=1,
                label="referencia O(h)")
    _estilo(eje3, "Error máximo al refinar", "número de intervalos", "error máximo")
    eje3.legend(fontsize=8)

    figura.tight_layout()
    plt.show()

    mostrar(
        f"**{datos['nombre']}**\n\n"
        f"| Paso $h$ | Hacia atrás | Centrada | Exacta |\n|---|---|---|---|\n"
        f"| {h:.4f} | {atras:.6f} | {centrada:.6f} | {df_exacta[i0]:.6f} |\n\n"
        f"- Error máximo con {_MALLAS[-1]} intervalos: `{errores[-1]:.3e}`\n"
        f"- Pendiente del error: **{pendiente:.2f}** "
        f"(1.0 significa error $O(h)$, 2.0 significa $O(h^2)$)"
    )
    return {"error_refinado": errores[-1], "pendiente": pendiente}


def _lab_derivada_centrada(datos: dict) -> dict:
    """Laboratorio de la diferencia centrada (figura 23.3).

    Tres paneles: la secante centrada sobre la señal, la derivada estimada
    contra la exacta, y el error contra el tamaño de paso en escala
    logarítmica, comparado con el de la diferencia hacia atrás.

    Args:
        datos: el ejemplo en uso.

    Returns:
        dict: `{"error_refinado", "pendiente"}` del método.
    """
    x, y, df_exacta = _malla(datos, datos["n"])
    h = x[1] - x[0]
    x0 = datos["x0"]
    i0 = int(np.argmin(np.abs(x - x0)))

    atras = (y[i0] - y[i0 - 1]) / (x[i0] - x[i0 - 1])
    centrada = (y[i0 + 1] - y[i0 - 1]) / (x[i0 + 1] - x[i0 - 1])

    figura, (eje1, eje2, eje3) = plt.subplots(1, 3, figsize=(13, 3.6))

    eje1.plot(x, y, "o-", lw=1, ms=4, label="muestras")
    eje1.plot([x[i0 - 1], x[i0 + 1]], [y[i0 - 1], y[i0 + 1]], "g-", lw=2,
              label="secante centrada")
    eje1.plot(x[i0], y[i0], "ks", ms=7)
    eje1.set_title(f"1) Secante centrada en x = {x[i0]:.2f}", fontsize=10)
    eje1.legend(fontsize=8)
    _estilo(eje1, "La señal y la secante", "x", "f(x)")

    estimada = np.full_like(x, np.nan)
    estimada[1:-1] = (y[2:] - y[:-2]) / (x[2:] - x[:-2])
    eje2.plot(x, df_exacta, "k-", lw=2, label="exacta")
    eje2.plot(x, estimada, "g--", lw=1.5, label="centrada")
    eje2.plot(x, np.gradient(y, x), "b:", lw=1.5, label="np.gradient")
    _estilo(eje2, "Estimación contra la derivada exacta", "x", "f'(x)")
    eje2.legend(fontsize=8)

    errores_centrada, errores_atras = [], []
    for n in _MALLAS:
        xs, ys, exacta = _malla(datos, n)
        centrada_n = np.full_like(ys, np.nan)
        centrada_n[1:-1] = (ys[2:] - ys[:-2]) / (xs[2:] - xs[:-2])
        atras_n = np.full_like(ys, np.nan)
        atras_n[1:] = np.diff(ys) / np.diff(xs)
        errores_centrada.append(float(np.nanmax(np.abs(centrada_n - exacta))))
        errores_atras.append(float(np.nanmax(np.abs(atras_n - exacta))))
    pendiente = _pendiente(np.array(_MALLAS, dtype=float), np.array(errores_centrada))
    eje3.loglog(_MALLAS, errores_centrada, "go-", label=f"centrada (pendiente ≈ {pendiente:.2f})")
    eje3.loglog(_MALLAS, errores_atras, "r--", label="atrás, para comparar")
    _estilo(eje3, "Error máximo al refinar", "número de intervalos", "error máximo")
    eje3.legend(fontsize=8)

    figura.tight_layout()
    plt.show()

    mostrar(
        f"**{datos['nombre']}**\n\n"
        f"| Paso $h$ | Hacia atrás | Centrada | Exacta |\n|---|---|---|---|\n"
        f"| {h:.4f} | {atras:.6f} | {centrada:.6f} | {df_exacta[i0]:.6f} |\n\n"
        f"- Error máximo de la centrada con {_MALLAS[-1]} intervalos: "
        f"`{errores_centrada[-1]:.3e}`\n"
        f"- Error máximo de la de atrás, en la misma malla: `{errores_atras[-1]:.3e}`\n"
        f"- Pendiente del error: **{pendiente:.2f}** "
        f"(1.0 significa error $O(h)$, 2.0 significa $O(h^2)$)"
    )
    return {"error_refinado": errores_centrada[-1], "pendiente": pendiente}
