"""Pruebas de derivada_integral contra los ejemplos publicados del libro."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from derivada_integral import (  # noqa: E402
    trapecio, trapecio_datos, simpson_1_3, simpson_3_8,
    integracion_desigual, derivada_adelante, derivada_atras,
    derivada_centrada,
)


def f_polinomio(x):
    """f(x) = 0.2 + 25x - 200x² + 675x³ - 900x⁴ + 400x⁵ (ejemplos 21.1-21.6)."""
    return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5


VERDADERO = 1.640533  # integral exacta de f_polinomio en [0, 0.8]


class TestIntegracion(unittest.TestCase):
    def test_trapecio_simple(self):
        # ejemplo 21.1: n=1 -> I = 0.1728 (publicado)
        self.assertAlmostEqual(trapecio(f_polinomio, 0.0, 0.8, n=1), 0.1728, places=4)

    def test_trapecio_multiple(self):
        # ejemplo 21.2: n=2 -> I = 1.0688
        self.assertAlmostEqual(trapecio(f_polinomio, 0.0, 0.8, n=2), 1.0688, places=4)

    def test_simpson_1_3(self):
        # ejemplo 21.5: n=4 -> I = 1.623467
        self.assertAlmostEqual(simpson_1_3(f_polinomio, 0.0, 0.8, n=4), 1.623467, places=6)

    def test_simpson_3_8(self):
        # ejemplo 21.6a: n=3 -> I = 1.519170
        self.assertAlmostEqual(simpson_3_8(f_polinomio, 0.0, 0.8, n=3), 1.519170, places=6)

    def test_trapecio_datos_desiguales(self):
        # ejemplo 21.7 (tabla 21.3) -> I = 1.594801
        x = [0.0, 0.12, 0.22, 0.32, 0.36, 0.40, 0.44, 0.54, 0.64, 0.70, 0.80]
        y = [0.200000, 1.309729, 1.305241, 1.743393, 2.074903, 2.456000,
             2.842985, 3.507297, 3.181929, 2.363000, 0.232000]
        self.assertAlmostEqual(trapecio_datos(x, y), 1.594801, places=6)
        self.assertAlmostEqual(integracion_desigual(x, y), 1.594801, places=6)


class TestDerivacion(unittest.TestCase):
    def test_derivada_centrada_primera(self):
        # f(x)=x^2 -> f'(1)=2 (exacta con centrada)
        self.assertAlmostEqual(derivada_centrada(lambda x: x ** 2, 1.0, h=0.01), 2.0, places=6)

    def test_derivada_centrada_segunda(self):
        # f(x)=x^3 -> f''(1)=6 (exacta con centrada)
        self.assertAlmostEqual(derivada_centrada(lambda x: x ** 3, 1.0, h=0.01, orden=2), 6.0, places=4)

    def test_derivada_adelante_atras(self):
        # f(x)=x^2 -> f'(1)=2 aprox (adelante O(h), atras O(h))
        self.assertAlmostEqual(derivada_adelante(lambda x: x ** 2, 1.0, h=1e-5), 2.0, places=3)
        self.assertAlmostEqual(derivada_atras(lambda x: x ** 2, 1.0, h=1e-5), 2.0, places=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
