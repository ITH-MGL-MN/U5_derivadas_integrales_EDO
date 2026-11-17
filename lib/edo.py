"""edo — solución numérica de ecuaciones diferenciales ordinarias (Unidad 5).

Métodos de un paso (Euler, Heun/Euler mejorado, Runge-Kutta de 4.º orden) y de
pasos múltiples (Adams-Bashforth-Moulton predictor-corrector). Todos resuelven
el problema de valor inicial

.. math:: \\frac{dy}{dx} = f(x, y), \\qquad y(x_0) = y_0

y devuelven un ``dict`` con los arreglos ``x`` e ``y`` de la trayectoria
discreta, listos para graficar o comparar contra la solución analítica.

Convenciones
------------
* ``f`` recibe ``(x, y)`` y devuelve la pendiente ``dy/dx``.
* ``x0, y0`` son la condición inicial; ``xf`` el extremo; ``h`` el paso.
* La trayectoria incluye ``x0`` y el último punto ``<= xf``.
"""

from __future__ import annotations

import numpy as np


def _malla(x0, xf, h):
    """Puntos ``x0, x0+h, ...`` hasta ``xf`` (inclusive si cae exacto)."""
    n = int(round((xf - x0) / h))
    return np.linspace(x0, x0 + n * h, n + 1)


def euler(f, x0, y0, xf, h):
    """Método de Euler, ecuación (25.2): ``y_{i+1} = y_i + f(x_i, y_i) h``."""
    x = _malla(float(x0), float(xf), float(h))
    y = np.empty_like(x)
    y[0] = float(y0)
    for i in range(x.size - 1):
        y[i + 1] = y[i] + f(x[i], y[i]) * h
    return {"x": x, "y": y}


def euler_mejorado(f, x0, y0, xf, h, iteraciones=1):
    """Método de Heun (Euler mejorado), predictor-corrector (25.15)-(25.16).

    Cada paso predice con Euler y corrige promediando las pendientes en
    ``x_i`` y ``x_{i+1}``. ``iteraciones`` repite la corrección (iteración de
    Heun, ecuaciones 25.14-25.17).
    """
    x = _malla(float(x0), float(xf), float(h))
    y = np.empty_like(x)
    y[0] = float(y0)
    for i in range(x.size - 1):
        xi, yi = x[i], y[i]
        # predictor (Euler)
        y_pred = yi + f(xi, yi) * h
        # corrector iterado
        for _ in range(max(1, int(iteraciones))):
            y_pred = yi + (f(xi, yi) + f(x[i + 1], y_pred)) / 2.0 * h
        y[i + 1] = y_pred
    return {"x": x, "y": y}


def runge_kutta_4(f, x0, y0, xf, h):
    """Método clásico de Runge-Kutta de cuarto orden (25.40).

    ``k1, k2, k3, k4`` según (25.40a)-(25.40d) y
    ``y_{i+1} = y_i + (k1 + 2k2 + 2k3 + k4) h / 6``.
    """
    x = _malla(float(x0), float(xf), float(h))
    y = np.empty_like(x)
    y[0] = float(y0)
    for i in range(x.size - 1):
        xi, yi = x[i], y[i]
        k1 = f(xi, yi)
        k2 = f(xi + h / 2.0, yi + h / 2.0 * k1)
        k3 = f(xi + h / 2.0, yi + h / 2.0 * k2)
        k4 = f(xi + h, yi + h * k3)
        y[i + 1] = yi + (k1 + 2.0 * k2 + 2.0 * k3 + k4) * h / 6.0
    return {"x": x, "y": y}


def adams_bashforth_moulton(f, x0, y0, xf, h):
    """Adams de 4.º orden predictor-corrector (método de pasos múltiples).

    Arranca con Runge-Kutta 4 para los primeros tres pasos (un método de pasos
    múltiples no se autoinicia) y después alterna el predictor abierto de
    Adams-Bashforth (26.40) con el corrector cerrado de Adams-Moulton (26.45),
    una corrección por paso.
    """
    x = _malla(float(x0), float(xf), float(h))
    y = np.empty_like(x)
    y[0] = float(y0)
    n = x.size

    # Arranque con RK4 (necesario: se requieren valores previos).
    for i in range(min(3, n - 1)):
        xi, yi = x[i], y[i]
        k1 = f(xi, yi)
        k2 = f(xi + h / 2.0, yi + h / 2.0 * k1)
        k3 = f(xi + h / 2.0, yi + h / 2.0 * k2)
        k4 = f(xi + h, yi + h * k3)
        y[i + 1] = yi + (k1 + 2.0 * k2 + 2.0 * k3 + k4) * h / 6.0

    # Predictor-corrector de Adams de 4.º orden.
    for i in range(3, n - 1):
        f_i = f(x[i], y[i])
        f_im1 = f(x[i - 1], y[i - 1])
        f_im2 = f(x[i - 2], y[i - 2])
        f_im3 = f(x[i - 3], y[i - 3])
        # predictor (Adams-Bashforth, 26.40)
        y_pred = y[i] + h / 24.0 * (55.0 * f_i - 59.0 * f_im1
                                    + 37.0 * f_im2 - 9.0 * f_im3)
        # corrector (Adams-Moulton, 26.45)
        f_pred = f(x[i + 1], y_pred)
        y[i + 1] = y[i] + h / 24.0 * (9.0 * f_pred + 19.0 * f_i
                                      - 5.0 * f_im1 + f_im2)
    return {"x": x, "y": y}


__all__ = [
    "euler", "euler_mejorado", "runge_kutta_4",
    "adams_bashforth_moulton",
]
