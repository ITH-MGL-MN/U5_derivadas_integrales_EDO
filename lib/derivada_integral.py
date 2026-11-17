"""derivada_integral — diferenciación e integración numéricas (Unidad 5).

Funciones puras (sin estado, sin gráficas) para que sirvan igual en un
cuaderno, en un script o en las pruebas. Reciben funciones ``f(x)`` o pares de
arreglos ``x``, ``y`` y devuelven ``float``/``ndarray``/``dict`` explícitos.

Convenciones
------------
* ``f`` es una función escalar ``f(x) -> float`` (o vectorizable).
* Los métodos de cuadratura ``f(a, b, n)`` reciben el integrando y devuelven
  la integral aproximada; ``n`` es el número de **segmentos**.
* ``derivada_*`` recibe la función, el punto ``x`` y el paso ``h``; ``orden``
  es 1 (primera derivada) o 2 (segunda derivada).
* Las versiones ``_datos`` trabajan con datos tabulados (espaciado irregular).
"""

from __future__ import annotations

import numpy as np


# ----------------------------------------------------------------------
# Integración: regla del trapecio
# ----------------------------------------------------------------------
def trapecio(f, a, b, n=1):
    """Regla del trapecio, simple (``n=1``) o de aplicación múltiple.

    Ecuación (21.3) para un segmento y (21.9) para ``n`` segmentos:
    ``I = (h/2)[f(x0) + 2 Σ f(xi) + f(xn)]``.
    """
    a, b = float(a), float(b)
    n = int(n)
    if n < 1:
        raise ValueError("n debe ser >= 1")
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = np.asarray([f(xi) for xi in x], dtype=float)
    return float(h * (0.5 * y[0] + np.sum(y[1:-1]) + 0.5 * y[-1]))


def trapecio_datos(x, y):
    """Regla del trapecio sobre datos tabulados (espaciado irregular).

    Ecuación (21.22): suma de ``h_i * (f(x_{i-1}) + f(x_i))/2`` por segmento.
    Es la base de la integración con intervalos desiguales.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or x.size != y.size or x.size < 2:
        raise ValueError("x y y deben ser arreglos 1-D del mismo tamaño (>= 2)")
    h = np.diff(x)
    return float(np.sum(h * (y[:-1] + y[1:]) / 2.0))


# ----------------------------------------------------------------------
# Reglas de Simpson
# ----------------------------------------------------------------------
def simpson_1_3(f, a, b, n):
    """Regla de Simpson 1/3, simple (``n=2``) o de aplicación múltiple.

    Ecuaciones (21.14) y (21.18). ``n`` debe ser **par**.
    """
    a, b = float(a), float(b)
    n = int(n)
    if n < 2 or n % 2 != 0:
        raise ValueError("n debe ser par y >= 2")
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = np.asarray([f(xi) for xi in x], dtype=float)
    return float(h / 3.0 * (y[0] + 4.0 * np.sum(y[1:-1:2])
                            + 2.0 * np.sum(y[2:-2:2]) + y[-1]))


def simpson_3_8(f, a, b, n=3):
    """Regla de Simpson 3/8, simple (``n=3``) o de aplicación múltiple.

    Ecuación (21.20). ``n`` debe ser **múltiplo de 3**.
    """
    a, b = float(a), float(b)
    n = int(n)
    if n < 3 or n % 3 != 0:
        raise ValueError("n debe ser múltiplo de 3 y >= 3")
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = np.asarray([f(xi) for xi in x], dtype=float)
    total = y[0] + y[-1]
    for i in range(1, n):
        total += 3.0 * y[i] if i % 3 != 0 else 2.0 * y[i]
    return float(3.0 * h / 8.0 * total)


def integracion_desigual(x, y):
    """Integración con intervalos desiguales sobre datos tabulados.

    Alias de ``trapecio_datos``: aplica la regla del trapecio segmento a
    segmento con el ``h_i`` real de cada intervalo (ecuación 21.22).
    """
    return trapecio_datos(x, y)


# ----------------------------------------------------------------------
# Diferenciación numérica (diferencias finitas)
# ----------------------------------------------------------------------
def _puntos(f, x, h, n):
    """Evalúa ``f`` en ``x + k*h`` para ``k = 0..n-1`` (hacia adelante)."""
    return np.asarray([f(x + k * h) for k in range(n)], dtype=float)


def derivada_adelante(f, x, h=0.1, orden=1):
    """Primera o segunda derivada con diferencias hacia adelante.

    ``orden=1`` usa la fórmula ``O(h)`` ``(f(x+h) - f(x))/h`` y
    ``orden=2`` usa ``(f(x+h) - 2f(x) + f(x-h))/h²``. Son las fórmulas de la
    figura 23.1 del libro.
    """
    x, h = float(x), float(h)
    if orden == 1:
        return float((f(x + h) - f(x)) / h)
    if orden == 2:
        return float((f(x + 2 * h) - 2 * f(x + h) + f(x)) / h ** 2)
    raise ValueError("orden debe ser 1 o 2")


def derivada_atras(f, x, h=0.1, orden=1):
    """Primera o segunda derivada con diferencias hacia atrás (figura 23.2)."""
    x, h = float(x), float(h)
    if orden == 1:
        return float((f(x) - f(x - h)) / h)
    if orden == 2:
        return float((f(x) - 2 * f(x - h) + f(x - 2 * h)) / h ** 2)
    raise ValueError("orden debe ser 1 o 2")


def derivada_centrada(f, x, h=0.1, orden=1):
    """Primera o segunda derivada con diferencias centradas (figura 23.3).

    ``orden=1``: ``(f(x+h) - f(x-h)) / (2h)`` (``O(h²)``).
    ``orden=2``: ``(f(x+h) - 2f(x) + f(x-h)) / h²`` (``O(h²)``).
    """
    x, h = float(x), float(h)
    if orden == 1:
        return float((f(x + h) - f(x - h)) / (2.0 * h))
    if orden == 2:
        return float((f(x + h) - 2.0 * f(x) + f(x - h)) / h ** 2)
    raise ValueError("orden debe ser 1 o 2")


def derivada_datos(x, y):
    """Primera derivada de datos tabulados (espaciado irregular).

    Usa diferencias centradas en los puntos interiores y hacia adelante/atrás
    en los extremos, con el ``h`` real de cada intervalo.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or x.size != y.size or x.size < 3:
        raise ValueError("se requieren al menos 3 puntos (x, y)")
    dy = np.empty_like(x)
    dy[0] = (y[1] - y[0]) / (x[1] - x[0])            # hacia adelante
    dy[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])       # hacia atrás
    for i in range(1, x.size - 1):
        dy[i] = (y[i + 1] - y[i - 1]) / (x[i + 1] - x[i - 1])  # centrada
    return dy


__all__ = [
    "trapecio", "trapecio_datos", "simpson_1_3", "simpson_3_8",
    "integracion_desigual", "derivada_adelante", "derivada_atras",
    "derivada_centrada", "derivada_datos",
]
