"""Pruebas de edo contra los ejemplos publicados del libro."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from edo import euler, euler_mejorado, runge_kutta_4, adams_bashforth_moulton  # noqa: E402


def f_polinomio(x, y):
    """dy/dx = -2x³ + 12x² - 20x + 8.5 (ejemplo 25.1)."""
    return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5


def f_exponencial(x, y):
    """dy/dx = 4e^{0.8x} - 0.5y (ejemplos 25.5, 25.7b, 26.6)."""
    import numpy as np
    return 4 * np.exp(0.8 * x) - 0.5 * y


class TestEDO(unittest.TestCase):
    def test_euler(self):
        # ejemplo 25.1: y(0.5) con Euler = 5.25
        r = euler(f_polinomio, 0.0, 1.0, 0.5, h=0.5)
        self.assertAlmostEqual(r["y"][1], 5.25, places=6)

    def test_euler_mejorado_heun(self):
        # ejemplo 25.5: 1 correccion -> y(1) = 6.701082
        r = euler_mejorado(f_exponencial, 0.0, 2.0, 1.0, h=1.0, iteraciones=1)
        self.assertAlmostEqual(r["y"][1], 6.701082, places=5)

    def test_runge_kutta_4_polinomio(self):
        # ejemplo 25.7a: y(0.5) con RK4 = 3.21875 (exacto, solucion cuartica)
        r = runge_kutta_4(f_polinomio, 0.0, 1.0, 0.5, h=0.5)
        self.assertAlmostEqual(r["y"][1], 3.21875, places=6)

    def test_adams_bashforth_moulton(self):
        # Adams 4.º orden de 0 a 4 con h=1 (arranque RK4): y(4) debe acercarse
        # a la solución exacta 75.3389626 dentro de ~1% (h=1 es un paso grueso).
        import numpy as np
        exact = lambda x: (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) \
            + 2 * np.exp(-0.5 * x)
        r = adams_bashforth_moulton(f_exponencial, 0.0, 2.0, 4.0, h=1.0)
        self.assertAlmostEqual(r["y"][-1] / exact(4.0), 1.0, places=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
