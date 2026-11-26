"""Genera los cuadernos de la Unidad 5 con nbformat.

Un cuaderno se arma con la plantilla del plan (§5):

    1.1 entorno · 1.2 cuenta · 2.1 introducción · 2.2 pregunta
    3.1–3.5 subtema "hazlo" (teoría, a mano, programar, laboratorio, pregunta)
    4.1–4.4 subtema "decídelo" (teoría, Python/MATLAB, configurar, pregunta)
    5.1 caso de ingeniería · 6.1–6.3 calificar, enviar, consultar

Se genera en vez de editarse a mano para que los cinco cuadernos se muevan
juntos: si cambia la celda de entorno o el cierre, cambia en todos.

Uso:

    python tools/crear_cuadernos.py            # todos los que estén definidos
    python tools/crear_cuadernos.py --solo 01  # solo uno
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "notebooks"
REPO = "ITH-MGL-MN/U5_derivadas_integrales_EDO"
FIGURAS = "https://raw.githubusercontent.com/" + REPO + "/main/docs/figuras/libro/"
DOCS = "https://github.com/" + REPO + "/blob/main/docs/"


# ---------------------------------------------------------------------------
# Utilidades de armado
# ---------------------------------------------------------------------------


def _md(texto: str):
    """Celda de markdown, sin espacios sobrantes al inicio ni al final."""
    return nbf.v4.new_markdown_cell(texto.strip() + "\n")


def _py(texto: str):
    """Celda de código, sin espacios sobrantes al inicio ni al final."""
    return nbf.v4.new_code_cell(texto.strip() + "\n")


def _rellena(texto: str) -> str:
    """Cambia los marcadores de ruta por las URLs publicadas.

    Los cuadernos se leen en Colab, así que los enlaces a las figuras y a las
    guías tienen que ser absolutos: un enlace relativo no lleva a ningún lado
    fuera de GitHub.
    """
    return texto.replace("@FIGURAS@", FIGURAS).replace("@DOCS@", DOCS)


def _nuevo(titulo_curso: str):
    """Cuaderno vacío con la metadata que necesitan Jupyter y Colab."""
    cuaderno = nbf.v4.new_notebook()
    cuaderno.metadata.update({
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
        "colab": {"provenance": [], "toc_visible": True},
    })
    return cuaderno


# ---------------------------------------------------------------------------
# Piezas comunes a los cinco cuadernos
# ---------------------------------------------------------------------------

ENTORNO = '''
#@title ⚙️ 1.1 · Entorno — ejecuta esta celda primero
# ---------------------------------------------------------------------------
# No hay nada que editar aquí: la celda prepara el material del curso en tu
# Drive y deja todo listo para trabajar. En Google Colab te va a pedir permiso
# para acceder a tu Drive (es el único permiso que pide esta celda).
# ---------------------------------------------------------------------------
import base64
import io
import os
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

CUADERNO = "@CUADERNO@"
CARPETA_MATERIAL = "CursoMN/material"
ORIGEN = "https://raw.githubusercontent.com/@REPO@/main"


try:
    import google.colab  # noqa: F401
    EN_COLAB = True
except ImportError:
    EN_COLAB = False


def _raiz_local():
    """Sube desde la carpeta del cuaderno hasta encontrar lib/robomat.py."""
    candidatas = []
    nb = globals().get("__vsc_ipynb_file__")
    if nb:
        candidatas.append(os.path.dirname(os.path.abspath(nb)))
    candidatas.append(os.getcwd())
    for base in candidatas:
        carpeta = Path(base)
        for _ in range(7):
            if (carpeta / "lib" / "robomat.py").exists():
                return carpeta
            carpeta = carpeta.parent
    return None


def _carpeta_material():
    """Deja el material del curso en el Drive del alumno y devuelve su ruta.

    Monta el Drive, actualiza los archivos que el cuaderno necesita y no
    pide nada por teclado.

    Returns:
        Path: carpeta con `lib/` y `grader/`.

    Raises:
        RuntimeError: si falta algún archivo del material (por ejemplo, porque
            todavía no se publicó el paquete del motor).
    """
    from google.colab import drive

    drive.mount("/content/drive")
    base = Path("/content/drive/MyDrive") / CARPETA_MATERIAL
    for relativa in ("lib/robomat.py", "lib/graficos.py", "lib/pantalla.py",
                     "grader/" + CUADERNO + ".txt"):
        destino = base / relativa
        destino.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(f"{ORIGEN}/{relativa}", timeout=60) as respuesta:
                destino.write_bytes(respuesta.read())
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"Falta {relativa} del material del curso (HTTP {exc.code}). "
                "Avisa al profesor."
            ) from exc
    return base


if EN_COLAB:
    RAIZ = _carpeta_material()
else:
    RAIZ = _raiz_local()

if RAIZ is None:
    raise RuntimeError("No encuentro el material del curso: abre el cuaderno desde la carpeta notebooks/.")


def _prepara_motor(raiz, cuaderno):
    """Deja el motor importable y dice en qué modo quedó.

    Con la rama test se usa el código legible (F12 y pdb funcionan). Sin él, se
    descomprime el paquete de `grader/`, que es lo que recibe el alumno.
    """
    if (raiz / "privado").is_dir():
        sys.path.insert(0, str(raiz))
        return "local"
    carpeta = Path(tempfile.mkdtemp(prefix="u5motor_"))
    archivo = raiz / "grader" / (cuaderno + ".txt")
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(archivo.read_bytes()))) as paquete:
        paquete.extractall(carpeta)
    sys.path.insert(0, str(carpeta))
    return "blob"


MODO = _prepara_motor(RAIZ, CUADERNO)
sys.path.insert(0, str(RAIZ / "lib"))

from privado.api import *          # noqa: F403,E402
from graficos import laboratorio   # noqa: E402

# El cuaderno le dice al motor cuál es su cuaderno. En el paquete de Colab ya
# viene fijo; en local hay que declararlo.
import privado.ajustes as _ajustes  # noqa: E402

_ajustes.CUADERNO = CUADERNO
try:
    _ajustes.TAREA_ID = _ajustes.leer_config().get("cuadernos", {}).get(CUADERNO, "")
except FileNotFoundError:
    _ajustes.TAREA_ID = ""

exec((RAIZ / "lib" / "robomat.py").read_text(encoding="utf-8"))   # noqa: S102

print(f"✅ Cuaderno {CUADERNO} listo. Continúa con la celda 1.2.")
'''

CUENTA = '''
#@title 🪪 1.2 · Cuenta — tus datos
# Tu cuenta fija el número de control y, con él, todos los datos de la unidad:
# el ejercicio a mano, el caso y la versión de cada pregunta.
# Usa tu correo INSTITUCIONAL (el que trae tu número de control): con otra
# cuenta no se puede registrar la calificación.
# En Google Colab se te va a pedir autorizar tu cuenta de Google: es un permiso
# aparte del que pediste para el Drive. En local no se pide nada.
MI_CUENTA = identificacion()
'''

CIERRE = '''
#@title 🧮 6.1 · Calificar
NOTA, TOPE = calificar()
'''

CIERRE_ENVIO = '''
#@title 📤 6.2 · Enviar
ENVIO = enviar()
'''

CIERRE_CONSULTA = '''
#@title 🔎 6.3 · Consultar la calificación guardada
GUARDADO = consultar_calificacion()
'''


def _entorno(cuaderno: str) -> str:
    """Arma la celda 1.1 para un cuaderno concreto."""
    return (ENTORNO.replace("@CUADERNO@", cuaderno)
                   .replace("@REPO@", REPO))


def _preguntas_del_cierre():
    """Las tres celdas de cierre, idénticas en todos los cuadernos."""
    return [_py(CIERRE), _py(CIERRE_ENVIO), _py(CIERRE_CONSULTA)]


# ---------------------------------------------------------------------------
# Cuaderno 01 · Derivación numérica
# ---------------------------------------------------------------------------

TITULO_01 = """
# 📉 Cuaderno 01 · Derivación numérica y diferenciación en tiempo real

Un encoder, una cámara, un termopar: todos entregan **muestras**, no funciones
matemáticas derivables analíticamente. En este cuaderno vas a estimar
$\\frac{\\mathrm{d}y}{\\mathrm{d}t}$ a partir de datos y a decidir **qué
diferencia usar** según el ruido, el lazo de control y dónde está la muestra.

> Las preguntas valen 20 puntos cada una y el caso vale 40. Las actividades a
> mano no restan: son evidencia de que seguiste el procedimiento.
"""

INTRO_01 = """
## 2.1 · Qué es derivar numéricamente y por qué duele

La derivada es un límite; con datos nunca llegamos al límite, solo a un
cociente de diferencias. La pregunta del tema no es "cuál es la fórmula" sino
**de qué lado del punto tomo la muestra** y **cuánto separo una muestra de otra**.

Las tres respuestas clásicas son las de las figuras 23.1 a 23.3 del libro:
hacia adelante, hacia atrás y centrada. Cambian dos cosas: el **orden del
error** y la **causalidad** (si para calcular la derivada de hoy necesito una
muestra de mañana, no puedo usarla en un lazo de control).

### Figura 23.4 · el caso que sí existe en la práctica

![Figura 23.4](@FIGURAS@fig23_4_temperatura.png)

Un termómetro se usa para medir la temperatura del suelo a 0, 1.25 y 3.75 cm de
profundidad y obtiene 13.5, 12 y 10 °C. Para estimar
$\\frac{\\mathrm{d}T}{\\mathrm{d}z}$ hay que dividir diferencias de temperatura
entre diferencias de profundidad **que no son iguales**. Ese es el caso normal:
los instrumentos no muestrean parejo.

*Qué muestra*: tres pares (profundidad, temperatura) sobre un eje vertical que
crece hacia abajo.

*Qué concluye*: la temperatura baja al profundizar, y con tres puntos desiguales
la diferencia centrada se generaliza dividiendo entre el intervalo total.

*Qué limitación tiene*: con tres puntos no hay forma de estimar el error sin
suponer algo sobre la curvatura.
"""

RUIDO_01 = """
### Figura 23.5 · por qué el ruido es el enemigo

Las dos imágenes siguientes son las dos mitades de la figura 23.5 del libro. En
la primera, los datos son limpios y la derivada sale suave; en la segunda, a los
mismos datos se les cambió un valor **muy poco** y la derivada se volvió un
zigzag.

![Figura 23.5, paneles a y c](@FIGURAS@fig23_5_ruido_1.png)

![Figura 23.5, paneles b y d](@FIGURAS@fig23_5_ruido_2.png)

*Qué muestra*: arriba los datos, abajo su derivada, en los dos casos.

*Qué concluye*: un error pequeño en $y$ se convierte en un error grande en
$\\frac{\\mathrm{d}y}{\\mathrm{d}x}$.

*Qué limitación tiene*: el método de diferencias no distingue entre una
variación real y un error de medición; por eso antes de derivar hay que decidir
si se filtra.

| Si necesitas… | Usa | Porque |
|---|---|---|
| Derivar dentro de un controlador | diferencia hacia atrás | Es la única que solo usa el pasado |
| Derivar con la mejor precisión y sin prisa | diferencia centrada | Su error es $O(h^2)$ y cuesta lo mismo |
| Derivar una señal ruidosa | filtrar y después centrada | El ruido se amplifica como $1/h$ |

Todo el catálogo (con los nombres exactos en Python y en MATLAB, y las figuras
del libro) está en la [guía de derivación numérica](@DOCS@guias/catalogo_01_derivacion.md).
"""

TEORIA_01 = """
## 3.1 · Diferencias finitas: las tres fórmulas y su error

Con una malla de paso $h$, el libro escribe las tres primeras derivadas así:

$$
f'(x_i) \\approx \\frac{f(x_{i+1}) - f(x_i)}{h}
$$

*Adelante, con error $O(h)$.*

$$
f'(x_i) \\approx \\frac{f(x_i) - f(x_{i-1})}{h}
$$

*Atrás, con error $O(h)$.*

$$
f'(x_i) \\approx \\frac{f(x_{i+1}) - f(x_{i-1})}{2h}
$$

*Centrada, con error $O(h^2)$.*

La centrada gana un orden **gratis**: usa los mismos dos valores, solo que uno a
cada lado. El precio es que hay que esperar la muestra siguiente, y que en el
primer y el último punto de la señal no se puede aplicar.

### La diferencia hacia atrás, que es la que corre en un microcontrolador

Es la única **causal**: para estimar la derivada en la muestra $i$ usa $i$ e
$i-1$, es decir, solo lo que ya ocurrió. Cuesta una resta y una división, y por
eso es la que aparece en un lazo de control a alta velocidad.

Su forma con espaciado desigual —que es la que necesitas cuando el
microcontrolador no muestrea parejo— es la misma división entre el intervalo
real:

$$
f'(x_i) \\approx \\frac{y_i - y_{i-1}}{t_i - t_{i-1}}
$$

**Lo que se te pide**: escribir dos funciones, la de atrás y la centrada. Reciben
la tabla completa y el índice, y devuelven un número.
"""

CONTRATO_01 = """
### 3.3 · Programa tus dos diferencias

Completa las funciones de la celda siguiente **sin cambiar sus nombres ni sus
parámetros**. Después ejecútalas con `practica(...)`, que las compara con la
referencia en tres casos cada una: el ejemplo 23.1 del libro, un caso con
espaciado desigual y tu propio caso sembrado con tu número de control.

- **Entra**: `t` (tiempos), `y` (valores) e `i` (índice de la muestra).
- **Sale**: un `float`, la derivada estimada.
- **Casos raros**: si `i` no tiene la muestra que hace falta, la función debe
  avisar con `ValueError` en vez de devolver un número inventado.

<details><summary>Pista 1 · dónde están en el libro</summary>

Son las fórmulas de las figuras 23.2 y 23.3: "diferencias divididas hacia atrás"
y "centradas".

</details>

<details><summary>Pista 2 · qué forma tienen las respuestas</summary>

Las dos son dos restas y una división. En la de atrás restas los valores de
`i` e `i-1`; en la centrada, los de `i+1` e `i-1`. El denominador no es `h`:
es la diferencia de tiempos, que funciona igual con espaciado uniforme o no.

</details>

<details><summary>Pista 3 · qué propiedad del problema mirar</summary>

Fíjate en el signo: si la señal sube, la derivada debe salir positiva. Y fíjate
en el rango de `i` que cada una puede aceptar.

</details>
"""

OBSERVA_01 = """
### 3.4 · Qué observar en el laboratorio

El laboratorio dibuja tres cosas. Míralas en este orden:

1. **La secante.** Es la derivada: la pendiente de la recta que une dos
   muestras. Si la señal es curva, la secante de un lado se queda corta o se
   pasa; la centrada promedia dos errores de signo contrario.
2. **La estimación contra la exacta.** Con la malla gruesa del ejemplo (h = 0.1)
   la diferencia hacia atrás se separa de la curva exacta sobre todo donde la
   curvatura es grande. La centrada casi se pega.
3. **El error al refinar.** Es la gráfica que decide el tema. En escala
   logarítmica, una recta de pendiente 1 significa error $O(h)$ y una de
   pendiente 2 significa $O(h^2)$. Al duplicar los intervalos, la primera baja a
   la mitad y la segunda a la cuarta parte.

> **Ojo con `np.gradient`.** Hace lo mismo que la centrada, pero además resuelve
> los extremos con diferencias de un solo lado. Por eso en el laboratorio los
> dos arreglos coinciden en el interior y solo difieren en los bordes.
"""

CATALOGO_01 = """
## 4.1 · Lo que no se programa, pero sí se elige

Ya tienes la diferencia hacia atrás. Los demás casos del capítulo 23 no se
escriben a mano: se configuran. Lo que hay que saber es **cuál pedir**.

- **Segunda derivada.** Se obtiene derivando dos veces, y ahí el ruido se vuelve
  el problema principal: si al derivar una vez el error crece como $1/h$, al
  derivar dos veces crece como $1/h^2$. Nunca se deriva dos veces una señal
  ruidosa sin filtrar.
- **Espaciado desigual.** La diferencia centrada se generaliza dividiendo entre
  el intervalo total entre las dos muestras que rodean al punto. Es la ecuación
  (23.9) del libro aplicada al caso lineal.
- **Extrapolación de Richardson.** Combina dos estimaciones con pasos distintos
  para cancelar el término de error dominante (ecuación 23.8). Gana orden, pero
  amplifica el ruido: solo con datos limpios.
- **Filtrado.** Una media móvil de $N$ muestras baja el ruido y también suaviza
  la señal real. Existe un $N$ que equilibra las dos cosas, y no es el mismo
  para todas las señales.

## 4.2 · Cómo se llaman en Python y en MATLAB

| Necesitas | Python | MATLAB |
|---|---|---|
| Diferencias simples | `np.diff(y)` | `diff(y)` |
| Derivada centrada, con ejes | `np.gradient(y, t)` | `gradient(y, t)` |
| Media móvil | `np.convolve(y, np.ones(N)/N, "same")` | `filter(ones(1,N)/N, 1, y)` |
| Suavizado que respeta la forma | `scipy.signal.savgol_filter` | `sgolayfilt` |
| Segunda derivada | `np.gradient(np.gradient(y, t), t)` | `gradient(gradient(y, t), t)` |

**Cuándo sí y cuándo no.** `np.gradient` es la opción por defecto cuando ya
tienes toda la señal en memoria: resuelve los bordes y acepta tiempos
irregulares. `np.diff` **no** divide entre `dt` ni resuelve bordes: sirve para
ver la diferencia bruta, no para reportar una velocidad. La media móvil es
barata y predecible, pero retrasa la señal media ventana; `savgol_filter`
conserva mejor los picos y cuesta más.
"""

CONFIGURA_01 = '''
#@title 🔧 4.3 · Configúralo tú (no lo programes)
# Cambia VENTANA y el RUÍDO del sensor y vuelve a ejecutar. El laboratorio
# dibuja la señal, su derivada y el error según el ancho de la ventana.
VENTANA = 7          # muestras que promedia la media móvil
RUIDO = 0.01         # desviación estándar del sensor, en unidades de la señal

FILTRO = laboratorio("filtrado", {"ventana": VENTANA, "ruido": RUIDO})
'''

OBSERVA_FILTRO_01 = """
### 4.4 · Qué observar en el laboratorio del filtro

Los tres paneles cuentan la misma historia en tres pasos:

1. **La señal.** La línea gris es lo que entrega el sensor: la curva real más
   ruido. La azul es la misma señal después de promediar `VENTANA` muestras. A
   simple vista se parecen; la diferencia está en la derivada.
2. **La derivada.** Al derivar la señal sin filtrar (gris), el ruido se
   multiplica y tapa la curva real. La derivada de la señal filtrada (azul) sí
   sigue a la exacta (negro a rayas). Ese es el motivo de filtrar antes de
   derivar.
3. **El ancho de la ventana.** El error no baja siempre: con ventanas pequeñas
   manda el ruido y con ventanas grandes el filtro se come la señal y la
   derivada se aplana. Hay un mínimo, y está marcado. Si eliges a ojo, casi
   siempre eliges de más: promediar 30 muestras se ve muy limpio y es un error
   grande.

Cambia `VENTANA` y vuelve a ejecutar la celda: la línea azul del panel 3 se
mueve. Con `VENTANA = 1` no hay filtro y el resultado es el de la señal cruda.
"""

CASO_01 = """
## 5.1 · Caso de ingeniería: aceleración de un brazo robótico

Un brazo gira con un movimiento suave, pero el encoder que mide el ángulo
entrega ruido. Con esas muestras hay que reportar **la velocidad angular
máxima**, y para eso hay que decidir tres cosas: cada cuánto se muestrea, si se
filtra, y qué diferencia se usa.

Ejecuta la celda siguiente: te va a dar **tus** datos (amplitud, frecuencia,
nivel de ruido y el arreglo de muestras) y la lista de métodos admitidos con lo
que vale cada uno. Elige tú.

<details><summary>Pista 1 · por dónde empezar</summary>

Con ruido, derivar directo es lo peor que puedes hacer: la figura 23.5 lo
muestra con datos de juguete, y tus datos son iguales. Antes de derivar, suaviza.

</details>

<details><summary>Pista 2 · qué forma tiene la respuesta</summary>

Un solo número, en rad/s, dentro de un diccionario con la clave
`"velocidad_max"`. Los extremos de la señal no se usan: la centrada no se puede
aplicar ahí.

</details>

<details><summary>Pista 3 · qué propiedad mirar</summary>

`np.convolve(..., mode="same")` mantiene el mismo tamaño que la señal, así que
el índice de la muestra i sigue significando lo mismo antes y después de
filtrar. La velocidad máxima es el máximo del **valor absoluto**: el brazo gira
en los dos sentidos.

</details>
"""

ESQUELETO_01 = """
### 5.1.1 · Tu solución

Completa los tres huecos. Nada de esto es de otra materia: la media móvil, el
máximo y el valor absoluto ya están resueltos; lo que falta es **tu** decisión.
"""

CODIGO_CASO_01 = '''
#@title 🛠️ 5.1.1 · Solución del caso
import numpy as np

VENTANA = 7                      # muestras de la media móvil
DATOS = CASO["datos"]
t = DATOS["t"]
theta = DATOS["theta"]

# Paso 1: quita el ruido sin cambiar el tamaño de la señal.
suave = ____

# Paso 2: estima la velocidad angular con tu función del numeral 3.3.
#         Recorre las muestras interiores (la centrada no se puede en los bordes).
velocidad = [____ for i in range(1, len(t) - 1)]

# Paso 3: el brazo gira en los dos sentidos, así que interesa el valor absoluto.
velocidad_max = ____

print(f"Velocidad angular máxima: {velocidad_max:.4f} rad/s")
'''

REVISA_01 = '''
#@title ✅ 5.1.2 · Revisar el caso
# Declara el método que usaste y entrega tu número.
VEREDICTO = caso_revisar(metodo="derivada_centrada", resultados={"velocidad_max": velocidad_max})
'''

CIERRE_MD_01 = """
## 6 · Cierre

`calificar()` suma tus tres preguntas y el caso, y normaliza a 100. El resultado
queda en `NOTA` y `TOPE`, por si quieres consultarlo después.

`enviar()` manda el resultado al backend del curso y `consultar_calificacion()`
te dice lo que quedó guardado. Sin conexión, `enviar()` avisa y no falla.

Si te quedó duda de algún método que no programaste, la
[guía de métodos](@DOCS@guias/README.md) tiene la tabla de decisión rápida y los
nombres en Python y en MATLAB.
"""


def cuaderno_01():
    """Arma el cuaderno U5_01 completo."""
    cuaderno = _nuevo("Derivación numérica")
    celdas = [
        _md(_rellena(TITULO_01)),
        _py(_entorno("u5_01_derivacion")),
        _py(CUENTA),
        _md(_rellena(INTRO_01)),
        _md(_rellena(RUIDO_01)),
        _py("""
#@title 🧪 2.2 · Pregunta 1
pregunta(1)
"""),
        _md(TEORIA_01),
        _py("""
#@title ✍️ 3.2 · Tu ejercicio a mano
MANO = mano_enunciado("derivada_atras")
"""),
        _py("""
#@title ✍️ 3.2 · Comprueba tu resultado
# Escribe aquí el número que calculaste (con 4 decimales).
ACIERTO = mano_comprueba("derivada_atras", 0.0)
"""),
        _md(CONTRATO_01),
        _py('''
#@title 💻 3.3 · Programa las dos funciones
def derivada_atras(t, y, i):
    """Derivada en la muestra i por diferencia hacia atrás.

    Args:
        t: tiempos de las muestras, crecientes.
        y: valores muestreados, misma longitud que t.
        i: índice de la muestra donde se estima la derivada (1 o mayor).

    Returns:
        float: la derivada estimada.

    Raises:
        ValueError: si i no tiene muestra anterior.
    """
    raise NotImplementedError("Escribe aquí tu diferencia hacia atrás")


def derivada_centrada(t, y, i):
    """Derivada en la muestra i por diferencia centrada.

    Args:
        t: tiempos de las muestras, crecientes.
        y: valores muestreados, misma longitud que t.
        i: índice de la muestra donde se estima la derivada.

    Returns:
        float: la derivada estimada.

    Raises:
        ValueError: si i no tiene una muestra a cada lado.
    """
    raise NotImplementedError("Escribe aquí tu diferencia centrada")
'''),
        _py("""
#@title ▶️ 3.3 · Compáralas con la referencia
APROBADA_ATRAS = practica(derivada_atras)
"""),
        _py("""
#@title ▶️ 3.3 · La centrada, contra la referencia
APROBADA_CENTRADA = practica(derivada_centrada)
"""),
        _py("""
#@title 📊 3.4 · Laboratorio
laboratorio("derivada_atras")
"""),
        _md(OBSERVA_01),
        _py("""
#@title 🧪 3.5 · Pregunta 2
pregunta(2)
"""),
        _md(CATALOGO_01),
        _py(CONFIGURA_01),
        _md(OBSERVA_FILTRO_01),
        _md(CASO_01),
        _py("""
#@title 🏭 5.1 · Tus datos y los métodos admitidos
CASO = caso()
"""),
        _md(ESQUELETO_01),
        _py(CODIGO_CASO_01),
        _py(REVISA_01),
        _py("""
#@title 🧪 5.1.3 · Pregunta 3
pregunta(3)
"""),
        _md(_rellena(CIERRE_MD_01)),
    ]
    celdas.extend(_preguntas_del_cierre())
    cuaderno["cells"] = celdas
    return cuaderno


# ---------------------------------------------------------------------------
# Cuaderno 02 · Integración numérica
# ---------------------------------------------------------------------------

TITULO_02 = """
# 📈 Cuaderno 02 · Integración numérica e integradores en tiempo real

Un sensor de corriente, un caudalímetro, un encoder: todos entregan muestras de
una **tasa**. Integrarlas da el total que sí interesa: carga consumida, agua
servida, distancia recorrida. En este cuaderno vas a integrar datos y a decidir
**qué regla usar** según el paso, el ruido y si estás dentro de un lazo.

> Las preguntas valen 20 puntos cada una y el caso vale 40. Las actividades a
> mano no restan: son evidencia de que seguiste el procedimiento.
"""

INTRO_02 = """
## 2.1 · De sumar rectángulos a Newton–Cotes

Integrar con datos es sumar áreas. La diferencia entre un método y otro está en
**cómo se rellena el hueco entre dos muestras**: con un rectángulo, con un
trapecio o con una parábola. Todo el capítulo 21 del libro es esa idea, y cada
relleno distinto compra un orden de error.

### Figura 21.4 · el trapecio

![Figura 21.4](@FIGURAS@fig21_4_trapecio.png)

La curva se cambia por la recta que une sus dos extremos: el área sombreada es
el trapecio que se usa como estimación. La franja entre la recta y la curva es
exactamente el error que se comete.

*Qué muestra*: la función, sus dos extremos y el trapecio que los une.

*Qué concluye*: si la curva es cóncava, el trapecio queda por encima y
sobreestima; si es convexa, subestima. El error depende de la curvatura, no del
valor.

*Qué limitación tiene*: con un solo trapecio el error es enorme; su gracia
aparece al repetirlo en muchos intervalos.

### Las tres formas de tomar la altura

Antes del trapecio está la regla del rectángulo, que es la que de verdad se
programa en un microcontrolador. Su altura puede ser el valor de la izquierda,
el de la derecha o el del centro del intervalo. Las tres son de primer orden,
pero no cometen el mismo error: una se queda corta, otra se pasa y la tercera
reparte el error a partes iguales.
"""

TEORIA_02 = """
## 3.1 · Las reglas del rectángulo

Con muestras $(t_0, y_0), (t_1, y_1), \\dots$ y anchos $h_k = t_{k+1} - t_k$:

$$
I_{\\text{izq}} = \\sum_{k} y_k\\, h_k
$$

$$
I_{\\text{der}} = \\sum_{k} y_{k+1}\\, h_k
$$

$$
I_{\\text{med}} = \\sum_{k} \\frac{y_k + y_{k+1}}{2}\\, h_k
$$

Las tres son de primer orden, pero se equivocan hacia lados distintos:

- **izquierda** subestima si la señal crece y sobreestima si decrece;
- **derecha** hace lo contrario: es la **causal**, porque en el instante $k+1$
  solo se conoce $y_{k+1}$, y por eso es la que corre en un lazo;
- **punto medio** promedia los extremos. Con la función a mano se evalúa el
  centro del intervalo y se gana un orden; con muestras no hay centro que
  evaluar, así que promediar es lo único posible.

En un microcontrolador se escribe como un acumulador, una línea por muestra:

```python
carga += corriente[k] * dt      # regla de la izquierda, dentro del lazo
```

### Por qué el trapecio es distinto

El trapecio es exactamente el promedio de las reglas de izquierda y derecha:

$$
I_{\\text{trap}} = \\sum_k \\frac{y_k + y_{k+1}}{2}\\, h_k
$$

Con datos muestreados coincide con la regla del punto medio, y esa coincidencia
es la que te va a aparecer en el laboratorio. Con la función disponible, en
cambio, el punto medio evalúa $f$ en el centro y es mejor.
"""

CONTRATO_02 = """
### 3.3 · Programa las tres reglas

Completa las tres funciones de la celda siguiente **sin cambiar sus nombres ni
sus parámetros**. Después ejecútalas con `practica(...)`: cada una se compara
con la referencia en dos casos del ejemplo 21.1 del libro y en tu caso sembrado
con tu número de control.

- **Entra**: `t` (instantes) e `y` (muestras), del mismo tamaño.
- **Sale**: un `float` con la integral.
- **Ojo**: los intervalos **no** son iguales. No uses un `h` único: usa el ancho
  de cada intervalo.

<details><summary>Pista 1 · dónde están en el libro</summary>

No tienen número de ecuación: son las reglas que se usan en un lazo de tiempo
real. El trapecio del libro es la ecuación (21.9) y es, literalmente, el
promedio de las dos primeras.

</details>

<details><summary>Pista 2 · qué forma tienen las respuestas</summary>

Un acumulador que recorre los intervalos. En cada uno, multiplica una altura por
su ancho: `y[k]` para la izquierda, `y[k+1]` para la derecha y el promedio de
los dos para el punto medio.

</details>

<details><summary>Pista 3 · qué propiedad del problema mirar</summary>

Si la señal es constante, las tres deben dar exactamente lo mismo: el valor por
el tiempo total. Si alguna falla ese caso, el error está en los índices.

</details>
"""

OBSERVA_02 = """
### 3.4 · Qué observar en el laboratorio

Los tres paneles responden tres preguntas distintas:

1. **¿Dónde toma la altura cada regla?** Los rectángulos azules usan el valor de
   la izquierda; la línea roja marca la altura que usaría la derecha. Con pocos
   intervalos, el hueco entre la recta y la curva es el error.
2. **¿Cómo se acumula el error?** La integral acumulada de la derecha se separa
   de la exacta y ya no vuelve: el sesgo se suma en cada intervalo. La del punto
   medio se mantiene pegada.
3. **¿Cuánto mejora al refinar?** En escala logarítmica, la pendiente del error
   es 1 para las tres: todas son de primer orden. Que la pendiente sea la misma
   no significa que cometan el mismo error, sino que **mejoran al mismo ritmo**.

> **Lo importante del panel 2.** La regla de la derecha no es "un poco peor":
> su error tiene el mismo signo en todos los intervalos y se acumula. En una
> batería eso es carga que se pierde de la cuenta, no ruido.
"""

CATALOGO_02 = """
## 4.1 · Lo que no se programa, pero sí se elige

Ya tienes las tres reglas. Los métodos de Newton–Cotes del capítulo 21 no se
escriben a mano en este curso: se configuran. Lo que hay que saber es cuál pedir.

- **Trapecio múltiple** (ecuación 21.9). Repite el trapecio en cada intervalo:
  error de segundo orden y funciona con paso irregular, porque cada intervalo
  usa su propio ancho (ecuación 21.22). Es la opción por defecto con datos.
- **Simpson 1/3** (ecuación 21.14). Cambia cada dos intervalos por una parábola:
  sube a cuarto orden **sin evaluar nada nuevo**, pero exige número par de
  intervalos y separación uniforme.
- **Simpson 3/8** (ecuación 21.20). Usa tres intervalos por parábola cúbica. Su
  razón de existir es cubrir un tramo final cuando el número de intervalos no es
  múltiplo de dos.
- **Cuadratura adaptativa.** Cuando tienes la **función** y no las muestras, el
  integrador elige los puntos y controla el error. Es otro problema: aquí no hay
  muestras que respetar.

### Figura 21.12 · combinar 1/3 con 3/8

![Figura 21.12](@FIGURAS@fig21_12_simpson_combinado.png)

La curva es unimodal y asimétrica. El tramo de la izquierda se integra con
Simpson 1/3 y el de la derecha con Simpson 3/8.

*Qué muestra*: dos reglas distintas cubriendo tramos contiguos del mismo
intervalo.

*Qué concluye*: cuando el número de intervalos no es par, no hay que tirar un
segmento ni bajar a trapecio: se cubre el final con la regla de tres octavos y
todo el intervalo queda con el mismo orden de error.

*Qué limitación tiene*: hay que llevar la cuenta de dónde empieza cada regla, y
por eso en la práctica se prefiere ajustar la malla para que sea par.

## 4.2 · Cómo se llaman en Python y en MATLAB

| Necesitas | Python | MATLAB |
|---|---|---|
| Trapecio | `np.trapezoid(y, t)` | `trapz(t, y)` |
| Trapecio acumulado | `scipy.integrate.cumulative_trapezoid` | `cumtrapz` |
| Simpson | `scipy.integrate.simpson(y, x=t)` | se compone con `trapz` o `integral` |
| Cuadratura adaptativa | `scipy.integrate.quad(f, a, b)` | `integral(@f, a, b)` |

**Cuándo sí y cuándo no.** `np.trapezoid` acepta `t` irregular y nunca falla:
es la apuesta segura con datos. `simpson` exige paso uniforme; si le pasas un
`t` irregular interpola por dentro y te devuelve un número que **parece** bueno.
`quad` necesita la función, así que no sirve para registros de un sensor.
`cumulative_trapezoid` es el que quieres cuando te interesa el valor en cada
instante y no solo el total.
"""

CONFIGURA_02 = '''
#@title 🔧 4.3 · Configúralo tú (no lo programes)
# Cambia N y vuelve a ejecutar. El laboratorio compara trapecio y Simpson sobre
# la misma función y muestra cómo cae el error de cada uno al refinar.
N = 8                # intervalos (Simpson necesita un número par)
COMPARACION = laboratorio("trapecio_simpson", {"n": N})
'''

OBSERVA_SIMPSON_02 = """
### 4.4 · Qué observar en el laboratorio de trapecio y Simpson

1. **El panel 1** une los nodos con rectas: eso es el trapecio. Con ocho
   intervalos la diferencia con la curva todavía se nota.
2. **El panel 2** une los nodos de tres en tres con parábolas: eso es Simpson.
   Con los **mismos** nodos, el área se pega mucho mejor a la curva.
3. **El panel 3** es la prueba del orden. El trapecio baja con pendiente 2 y
   Simpson con pendiente 4: al duplicar los intervalos, el primero divide su
   error entre 4 y el segundo entre 16.

Esa es la razón por la que Simpson, cuando el paso es uniforme, es la mejor
compra: cuesta lo mismo que el trapecio y gana dos órdenes. El precio es la
condición: **número par de intervalos e igual separación entre nodos**.
"""

CASO_02 = """
## 5.1 · Caso de ingeniería: estado de carga de una batería

Un paquete de baterías alimenta un robot. El bus CAN informa la corriente cada
cierto tiempo, **sin periodicidad**: hay ráfagas de datos rápidos y huecos
largos. Con esa corriente hay que estimar cuánta carga se consumió y en qué
estado de carga quedó la batería.

Ejecuta la celda siguiente: te da **tus** datos (capacidad, estado inicial,
muestras y picos de corriente) y la lista de métodos admitidos con lo que vale
cada uno. Elige tú.

<details><summary>Pista 1 · por dónde empezar</summary>

La carga es la integral de la corriente: cada amperio durante un segundo es un
coulomb. Para pasar a amperios-hora hay que dividir entre 3600.

</details>

<details><summary>Pista 2 · qué forma tiene la respuesta</summary>

Un solo número, el estado de carga final en porcentaje, dentro de un
diccionario con la clave `"soc_final"`.

</details>

<details><summary>Pista 3 · qué propiedad del problema mirar</summary>

Mira la separación entre muestras antes de elegir la regla. Si no es constante,
hay reglas de Newton–Cotes que dejan de ser válidas tal como están escritas.

</details>
"""

ESQUELETO_02 = """
### 5.1.1 · Tu solución

Completa los dos huecos. El ancho de cada intervalo y las muestras ya están
listos; lo que falta es **tu** elección de regla.
"""

CODIGO_CASO_02 = '''
#@title 🛠️ 5.1.1 · Solución del caso
import numpy as np

DATOS = CASO["datos"]
t = DATOS["t"]
corriente = DATOS["corriente"]

ANCHOS = np.diff(t)          # ancho de cada intervalo, en segundos

# Paso 1: carga consumida, en amperios-hora. Un amperio durante un segundo
#         es un coulomb, y 3600 coulombs son un amperio-hora.
carga_Ah = ____

# Paso 2: estado de carga final, en porcentaje.
soc_final = ____

print(f"Carga consumida: {carga_Ah:.4f} Ah")
print(f"Estado de carga final: {soc_final:.4f} %")
'''

REVISA_02 = '''
#@title ✅ 5.1.2 · Revisar el caso
# Declara el método que usaste y entrega tu número.
VEREDICTO = caso_revisar(metodo="trapecio_irregular", resultados={"soc_final": soc_final})
'''

CIERRE_MD_02 = """
## 6 · Cierre

`calificar()` suma tus tres preguntas y el caso, y normaliza a 100. El resultado
queda en `NOTA` y `TOPE`, por si quieres consultarlo después.

`enviar()` manda el resultado al backend del curso y `consultar_calificacion()`
te dice lo que quedó guardado. Sin conexión, `enviar()` avisa y no falla.

Si te quedó duda de algún método que no programaste, la
[guía de integración](@DOCS@guias/catalogo_02_integracion.md) tiene la tabla de
decisión y los nombres en Python y en MATLAB.
"""


def cuaderno_02():
    """Arma el cuaderno U5_02 completo."""
    cuaderno = _nuevo("Integración numérica")
    celdas = [
        _md(_rellena(TITULO_02)),
        _py(_entorno("u5_02_integracion")),
        _py(CUENTA),
        _md(_rellena(INTRO_02)),
        _py("""
#@title 🧪 2.2 · Pregunta 1
pregunta(1)
"""),
        _md(TEORIA_02),
        _py("""
#@title ✍️ 3.2 · Tu ejercicio a mano
MANO = mano_enunciado("integral_derecha")
"""),
        _py("""
#@title ✍️ 3.2 · Comprueba tu resultado
# Escribe aquí el número que calculaste (con 4 decimales).
ACIERTO = mano_comprueba("integral_derecha", 0.0)
"""),
        _md(CONTRATO_02),
        _py('''
#@title 💻 3.3 · Programa las tres reglas
def integral_izquierda(t, y):
    """Integral por la regla del rectángulo con el valor de la izquierda.

    Args:
        t: instantes de las muestras, crecientes.
        y: muestras, misma longitud que t.

    Returns:
        float: la integral aproximada.
    """
    raise NotImplementedError("Escribe aquí tu regla de la izquierda")


def integral_derecha(t, y):
    """Integral por la regla del rectángulo con el valor de la derecha.

    Args:
        t: instantes de las muestras, crecientes.
        y: muestras, misma longitud que t.

    Returns:
        float: la integral aproximada.
    """
    raise NotImplementedError("Escribe aquí tu regla de la derecha")


def integral_punto_medio(t, y):
    """Integral por la regla del punto medio sobre datos muestreados.

    Args:
        t: instantes de las muestras, crecientes.
        y: muestras, misma longitud que t.

    Returns:
        float: la integral aproximada.
    """
    raise NotImplementedError("Escribe aquí tu regla del punto medio")
'''),
        _py("""
#@title ▶️ 3.3 · Compáralas con la referencia
APROBADA_IZQUIERDA = practica(integral_izquierda)
APROBADA_DERECHA = practica(integral_derecha)
APROBADA_MEDIO = practica(integral_punto_medio)
"""),
        _py("""
#@title 📊 3.4 · Laboratorio
laboratorio("rectangulos")
"""),
        _md(OBSERVA_02),
        _py("""
#@title 🧪 3.5 · Pregunta 2
pregunta(2)
"""),
        _md(_rellena(CATALOGO_02)),
        _py(CONFIGURA_02),
        _md(OBSERVA_SIMPSON_02),
        _md(CASO_02),
        _py("""
#@title 🏭 5.1 · Tus datos y los métodos admitidos
CASO = caso()
"""),
        _md(ESQUELETO_02),
        _py(CODIGO_CASO_02),
        _py(REVISA_02),
        _py("""
#@title 🧪 5.1.3 · Pregunta 3
pregunta(3)
"""),
        _md(_rellena(CIERRE_MD_02)),
    ]
    celdas.extend(_preguntas_del_cierre())
    cuaderno["cells"] = celdas
    return cuaderno


CUADERNOS = {
    "01": ("U5_01_Derivacion_Numerica.ipynb", cuaderno_01),
    "02": ("U5_02_Integracion_Numerica.ipynb", cuaderno_02),
}


def main(argv: list[str] | None = None) -> int:
    """Escribe los cuadernos en `notebooks/`."""
    analizador = argparse.ArgumentParser(description="Genera los cuadernos de la Unidad 5.")
    analizador.add_argument("--solo", choices=sorted(CUADERNOS), default=None,
                            help="Genera solo el cuaderno indicado.")
    opciones = analizador.parse_args(argv)

    DESTINO.mkdir(parents=True, exist_ok=True)
    for clave, (nombre, constructor) in sorted(CUADERNOS.items()):
        if opciones.solo and opciones.solo != clave:
            continue
        ruta = DESTINO / nombre
        nbf.write(constructor(), ruta)
        print(f"  ✔ {ruta.relative_to(RAIZ)}  ({len(nbf.read(ruta, as_version=4)['cells'])} celdas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
