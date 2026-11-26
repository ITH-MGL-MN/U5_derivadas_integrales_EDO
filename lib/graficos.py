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
        ejemplo: diccionario con los datos del caso. Para los métodos de
            diferencias se usan `f`, `df`, `a`, `b`, `n`, `x0` y `nombre`; para
            `"filtrado"` se usan `ventana` (muestras de la media móvil) y
            `ruido` (desviación estándar del sensor). Si se omite, se usa el
            ejemplo 23.1 del libro.

    Returns:
        dict: según el laboratorio; los de diferencias devuelven
        `{"error_refinado": ..., "pendiente": ...}` con el error máximo en la
        malla más fina y la pendiente ajustada de la gráfica log-log (1.0 para
        un método de primer orden, 2.0 para uno de segundo).

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

    figura, (eje1, eje2, eje3) = plt.subplots(3, 1, figsize=(6.5, 11))

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

    figura, (eje1, eje2, eje3) = plt.subplots(3, 1, figsize=(6.5, 11))

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


def _lab_filtrado(datos: dict) -> dict:
    """Laboratorio del filtrado antes de derivar (subtema 4.x del cuaderno 01).

    Tres paneles apilados para leer en el teléfono:

    1. la señal medida (con ruido) y la misma señal después de la media móvil;
    2. la derivada sin filtrar, la derivada de la señal filtrada y la derivada
       exacta del seno, que es lo que se quiere recuperar;
    3. el error de la derivada contra el ancho de la ventana, donde se ve que
       filtrar de más también arruina la estimación.

    Args:
        datos: además de las claves comunes, `ventana` (muestras de la media
            móvil; 7 por omisión) y `ruido` (desviación estándar; 0.02 por
            omisión). La señal es un seno de 1 Hz con su tercer armónico, medida
            a 200 muestras por segundo, como un lazo de control.

    Returns:
        dict: `{"ventana", "error", "ventana_optima"}` con el error medio de la
        derivada en la ventana elegida y la ventana que lo minimiza.
    """
    ventana = int(datos.get("ventana", 7))
    ruido = float(datos.get("ruido", 0.02))
    frecuencia = 1.0
    muestreo = 200.0
    armonico = 0.3

    t = np.arange(0.0, 2.0, 1.0 / muestreo)
    limpia = (np.sin(2.0 * np.pi * frecuencia * t)
              + armonico * np.sin(2.0 * np.pi * 3.0 * frecuencia * t))
    generador = np.random.default_rng(7)
    medida = limpia + generador.normal(0.0, ruido, t.size)

    exacta = (2.0 * np.pi * frecuencia * np.cos(2.0 * np.pi * frecuencia * t)
              + armonico * 6.0 * np.pi * frecuencia * np.cos(2.0 * np.pi * 3.0 * frecuencia * t))
    suave = np.convolve(medida, np.ones(ventana) / ventana, mode="same")
    derivada_cruda = np.gradient(medida, t)
    derivada_suave = np.gradient(suave, t)

    figura, (eje1, eje2, eje3) = plt.subplots(3, 1, figsize=(6.5, 11))

    eje1.plot(t, medida, color="0.7", lw=0.9, label="señal medida (con ruido)")
    eje1.plot(t, suave, "b-", lw=2, label=f"media móvil de {ventana} muestras")
    eje1.plot(t, limpia, "k--", lw=1, label="señal real")
    _estilo(eje1, f"1) La señal y su suavizado (ruido σ = {ruido})", "tiempo (s)", "posición")
    eje1.legend(fontsize=8, loc="upper right")

    tope = 2.5 * float(np.max(np.abs(exacta)))
    eje2.plot(t, derivada_cruda, color="0.75", lw=0.8, label="derivada sin filtrar")
    eje2.plot(t, derivada_suave, "b-", lw=2, label="derivada de la señal filtrada")
    eje2.plot(t, exacta, "k--", lw=1.5, label="derivada exacta")
    eje2.set_ylim(-tope, tope)
    _estilo(eje2, "2) La derivada: el ruido se multiplica", "tiempo (s)", "velocidad")
    eje2.legend(fontsize=8, loc="upper right")

    ventanas = np.arange(1, 62, 2)
    errores = []
    for ancho in ventanas:
        filtrada = np.convolve(medida, np.ones(ancho) / ancho, mode="same")
        aproximada = np.gradient(filtrada, t)
        interior = slice(ancho, -ancho)
        errores.append(float(np.mean(np.abs(aproximada[interior] - exacta[interior]))))
    errores = np.array(errores)
    optima = int(ventanas[int(np.argmin(errores))])

    eje3.semilogy(ventanas, errores, "o-", color="tab:green", ms=3)
    eje3.axvline(ventana, color="tab:blue", ls="--", lw=1.2,
                 label=f"tu ventana: {ventana}")
    eje3.axvline(optima, color="tab:red", ls=":", lw=1.2,
                 label=f"la mejor: {optima}")
    _estilo(eje3, "3) Error de la derivada según el ancho de la ventana",
            "muestras de la media móvil", "error medio")
    eje3.legend(fontsize=8)

    figura.tight_layout()
    plt.show()

    error_elegida = errores[int(np.argmin(np.abs(ventanas - ventana)))]
    mostrar(
        f"**Ventana elegida:** {ventana} muestras · "
        f"error medio de la derivada `{error_elegida:.4f}`\n\n"
        f"**Sin filtrar** (ventana de 1 muestra) el error medio es "
        f"`{errores[0]:.4f}`: la derivada sigue al ruido, no a la señal. "
        f"**La mejor ventana de este caso es {optima}**, con `{errores.min():.4f}`.\n\n"
        "| Ventana | Error medio |\n|---|---|\n"
        + "\n".join(f"| {ancho} | {valor:.4f} |"
                    for ancho, valor in zip(ventanas[::5], errores[::5]))
        + "\n\n*Mira el panel 3: a la izquierda manda el ruido, a la derecha el "
        "filtro se come la señal. El mínimo es lo que hay que buscar, y no está "
        "en los extremos.*"
    )
    return {"ventana": ventana, "error": error_elegida, "ventana_optima": optima}


# ---------------------------------------------------------------------------
# Cuaderno 02 · Integración numérica
# ---------------------------------------------------------------------------


def _integral_exacta(a: float, b: float) -> float:
    """Integral de la función de prueba entre a y b.

    La función es f(t) = 2 + 1.5t - 0.4t² + e^(-t) y su primitiva
    S(t) = 2t + 0.75t² - 0.4t³/3 - e^(-t). Se eligió con un término
    exponencial a propósito: así Simpson **no** es exacto y su orden se puede
    medir en la gráfica (con un polinomio de grado dos daría error de máquina).

    Args:
        a: extremo inferior.
        b: extremo superior.

    Returns:
        float: el valor exacto de la integral.
    """
    def primitiva(x):
        return 2.0 * x + 0.75 * x**2 - 0.4 * x**3 / 3.0 - np.exp(-x)

    return float(primitiva(b) - primitiva(a))


def _senal_de_prueba(t: np.ndarray) -> np.ndarray:
    """Valores de la función de prueba en los instantes dados."""
    return 2.0 + 1.5 * t - 0.4 * t**2 + np.exp(-t)


def _lab_rectangulos(datos: dict) -> dict:
    """Laboratorio de las tres reglas del rectángulo sobre datos muestreados.

    Tres paneles apilados:

    1. la señal con los rectángulos de cada regla en una malla gruesa, para ver
       dónde toma la altura cada una;
    2. la integral acumulada de las tres contra la exacta: la de la derecha se
       despega, la de la izquierda también, y la del punto medio se pega;
    3. el error total contra el número de intervalos en escala logarítmica, con
       la pendiente de cada regla.

    Args:
        datos: `a`, `b` y `n` (intervalos de la malla gruesa; 8 por omisión).

    Returns:
        dict: `{"error_izquierda", "error_derecha", "error_punto_medio"}` en la
        malla fina.
    """
    a = float(datos.get("a", 0.0))
    b = float(datos.get("b", 2.0))
    n = int(datos.get("n", 8))

    t = np.linspace(a, b, n + 1)
    y = _senal_de_prueba(t)
    h = t[1] - t[0]

    figura, (eje1, eje2, eje3) = plt.subplots(3, 1, figsize=(6.5, 11))

    eje1.plot(t, y, "ko-", ms=4, lw=1, label="muestras", zorder=5)
    for indice in range(n):
        eje1.add_patch(plt.Rectangle((t[indice], 0), h, y[indice],
                                     facecolor="tab:blue", alpha=0.18, edgecolor="none"))
        eje1.plot([t[indice + 1], t[indice + 1]], [0, y[indice]], color="tab:red",
                  lw=0.8, alpha=0.5)
    eje1.axhline(0, color="k", lw=0.6)
    _estilo(eje1, f"1) Altura de cada rectángulo: izquierda (azul) y derecha (rojo), n = {n}",
            "t", "f(t)")
    eje1.legend(fontsize=8, loc="upper right")

    malla = np.linspace(a, b, 401)
    exacta_acumulada = np.array([_integral_exacta(a, x) for x in malla])
    izquierda_acumulada = np.concatenate(([0.0], np.cumsum(y[:-1] * h)))
    derecha_acumulada = np.concatenate(([0.0], np.cumsum(y[1:] * h)))
    medio_acumulada = np.concatenate(([0.0], np.cumsum(0.5 * (y[:-1] + y[1:]) * h)))

    eje2.plot(malla, exacta_acumulada, "k-", lw=2, label="exacta")
    eje2.plot(t, izquierda_acumulada, "b--o", ms=3, label="izquierda")
    eje2.plot(t, derecha_acumulada, "r--s", ms=3, label="derecha")
    eje2.plot(t, medio_acumulada, "g-.^", ms=3, label="punto medio")
    _estilo(eje2, "2) Integral acumulada: cada regla se despega a su manera",
            "t", "integral de a hasta t")
    eje2.legend(fontsize=8, loc="upper left")

    mallas = (4, 8, 16, 32, 64, 128, 256)
    errores = {"izquierda": [], "derecha": [], "punto medio": []}
    for pasos in mallas:
        ts = np.linspace(a, b, pasos + 1)
        ys = _senal_de_prueba(ts)
        ancho = ts[1] - ts[0]
        exacto = _integral_exacta(a, b)
        errores["izquierda"].append(abs(float(np.sum(ys[:-1] * ancho)) - exacto))
        errores["derecha"].append(abs(float(np.sum(ys[1:] * ancho)) - exacto))
        errores["punto medio"].append(abs(float(np.sum(0.5 * (ys[:-1] + ys[1:]) * ancho)) - exacto))

    for nombre, color, marca in (("izquierda", "tab:blue", "o"),
                                 ("derecha", "tab:red", "s"),
                                 ("punto medio", "tab:green", "^")):
        pendiente = _pendiente(np.array(mallas, dtype=float), np.array(errores[nombre]))
        eje3.loglog(mallas, errores[nombre], marca + "-", color=color, ms=3,
                    label=f"{nombre} (pendiente ≈ {pendiente:.2f})")
    eje3.loglog(mallas, np.array(errores["izquierda"])[0] * (np.array(mallas, dtype=float) ** -1),
                "k:", lw=1, label="referencia O(h)")
    _estilo(eje3, "3) Error total al refinar", "número de intervalos", "error absoluto")
    eje3.legend(fontsize=8, loc="lower left")

    figura.tight_layout()
    plt.show()

    mostrar(
        f"**Integral exacta** entre {a:g} y {b:g}: `{_integral_exacta(a, b):.6f}`\n\n"
        "| Regla | Integral | Error |\n|---|---|---|\n"
        f"| izquierda | {float(np.sum(y[:-1] * h)):.6f} | {errores['izquierda'][-1]:.3e} |\n"
        f"| derecha | {float(np.sum(y[1:] * h)):.6f} | {errores['derecha'][-1]:.3e} |\n"
        f"| punto medio | {float(np.sum(0.5 * (y[:-1] + y[1:]) * h)):.6f} | {errores['punto medio'][-1]:.3e} |\n\n"
        "*Con datos muestreados, el punto medio necesita el valor en el centro del "
        "intervalo, que no existe: por eso se promedia los extremos y el resultado "
        "coincide con el trapecio. Con la función a mano sí se evalúa el centro.*"
    )
    return {"error_izquierda": errores["izquierda"][-1],
            "error_derecha": errores["derecha"][-1],
            "error_punto_medio": errores["punto medio"][-1]}


def _lab_trapecio_simpson(datos: dict) -> dict:
    """Laboratorio del trapecio y de Simpson sobre una función conocida.

    Tres paneles apilados:

    1. el área que sombrea el trapecio con pocos intervalos y la curva real;
    2. el área que sombrea Simpson 1/3 con los mismos intervalos;
    3. el error de los dos contra el número de intervalos, con la pendiente de
       cada método (2 para el trapecio, 4 para Simpson).

    Args:
        datos: `a`, `b` y `n` (intervalos; debe ser par para Simpson, 8 por
            omisión).

    Returns:
        dict: `{"error_trapecio", "error_simpson"}` en la malla más fina.
    """
    a = float(datos.get("a", 0.0))
    b = float(datos.get("b", 2.0))
    n = int(datos.get("n", 8))
    if n % 2:
        n += 1

    t = np.linspace(a, b, n + 1)
    y = _senal_de_prueba(t)
    fina = np.linspace(a, b, 400)

    figura, (eje1, eje2, eje3) = plt.subplots(3, 1, figsize=(6.5, 11))

    eje1.plot(fina, _senal_de_prueba(fina), "k-", lw=2, label="f(t)")
    eje1.plot(t, y, "o", color="tab:blue", ms=4, label="nodos")
    for indice in range(n):
        eje1.add_patch(plt.Polygon([[t[indice], 0], [t[indice], y[indice]],
                                    [t[indice + 1], y[indice + 1]], [t[indice + 1], 0]],
                                   closed=True, facecolor="tab:blue", alpha=0.25,
                                   edgecolor="none"))
    eje1.axhline(0, color="k", lw=0.6)
    _estilo(eje1, f"1) Trapecio con n = {n}: une los nodos con rectas", "t", "f(t)")
    eje1.legend(fontsize=8, loc="upper right")

    eje2.plot(fina, _senal_de_prueba(fina), "k-", lw=2, label="f(t)")
    eje2.plot(t, y, "o", color="tab:green", ms=4, label="nodos")
    for inicio in range(0, n, 2):
        xs = t[inicio:inicio + 3]
        if xs.size < 3:
            break
        coeficientes = np.polyfit(xs, _senal_de_prueba(xs), 2)
        tramo = np.linspace(xs[0], xs[-1], 40)
        eje2.fill_between(tramo, 0, np.polyval(coeficientes, tramo),
                          color="tab:green", alpha=0.25)
        eje2.plot(tramo, np.polyval(coeficientes, tramo), color="tab:green", lw=1.5)
    eje2.axhline(0, color="k", lw=0.6)
    _estilo(eje2, f"2) Simpson 1/3 con los mismos nodos: une de tres en tres con parábolas",
            "t", "f(t)")
    eje2.legend(fontsize=8, loc="upper right")

    mallas = (2, 4, 8, 16, 32, 64, 128)
    errores_trapecio, errores_simpson = [], []
    exacto = _integral_exacta(a, b)
    from scipy.integrate import simpson

    for pasos in mallas:
        ts = np.linspace(a, b, pasos + 1)
        ys = _senal_de_prueba(ts)
        errores_trapecio.append(abs(float(np.trapezoid(ys, ts)) - exacto))
        errores_simpson.append(abs(float(simpson(ys, x=ts)) - exacto))

    integral_trapecio = float(np.trapezoid(y, t))
    integral_simpson = float(simpson(y, x=t))

    pendiente_t = _pendiente(np.array(mallas, dtype=float), np.array(errores_trapecio))
    pendiente_s = _pendiente(np.array(mallas, dtype=float), np.array(errores_simpson))
    eje3.loglog(mallas, errores_trapecio, "bo-", ms=3,
                label=f"trapecio (pendiente ≈ {pendiente_t:.2f})")
    eje3.loglog(mallas, errores_simpson, "g^-", ms=3,
                label=f"Simpson (pendiente ≈ {pendiente_s:.2f})")
    _estilo(eje3, "3) Error al refinar: la diferencia entre los dos órdenes",
            "número de intervalos", "error absoluto")
    eje3.legend(fontsize=8, loc="lower left")

    figura.tight_layout()
    plt.show()

    mostrar(
        f"**Integral exacta** entre {a:g} y {b:g}: `{exacto:.6f}`\n\n"
        "| Método | Integral | Error |\n|---|---|---|\n"
        f"| trapecio | {integral_trapecio:.6f} | {errores_trapecio[-1]:.3e} |\n"
        f"| Simpson 1/3 | {integral_simpson:.6f} | {errores_simpson[-1]:.3e} |\n\n"
        "Al duplicar los intervalos, el trapecio divide su error entre 4 y Simpson "
        "entre 16: ese es el efecto de ganar dos órdenes."
    )
    return {"error_trapecio": errores_trapecio[-1], "error_simpson": errores_simpson[-1]}


def _lab_ruido(datos: dict) -> dict:
    """Laboratorio de por qué derivar amplifica el ruido e integrar lo atenúa.

    Es el contraste que cierra el tema. Con la **misma** señal medida, tres
    paneles apilados:

    1. la señal medida y la real;
    2. su derivada numérica contra la derivada exacta: el ruido aparece
       multiplicado y tapa la curva;
    3. su integral acumulada contra la integral exacta: las dos se pegan, y el
       error se queda pequeño.

    Args:
        datos: `a`, `b` y `ruido` (desviación estándar del sensor). La señal es
            f(t) = 2 + 1.5t - 0.4t² + e^(-t), muestreada a 200 Hz.

    Returns:
        dict: `{"ruido", "error_derivada", "error_integral"}` con las raíces
        del error cuadrático medio de cada operación.
    """
    a = float(datos.get("a", 0.0))
    b = float(datos.get("b", 2.0))
    ruido = float(datos.get("ruido", 0.05))
    muestreo = 200.0

    t = np.arange(a, b, 1.0 / muestreo)
    real = _senal_de_prueba(t)
    generador = np.random.default_rng(5)
    medida = real + generador.normal(0.0, ruido, t.size)

    exacta_derivada = 1.5 - 0.8 * t - np.exp(-t)
    derivada = np.gradient(medida, t)

    anchos = np.diff(t)
    integral = np.concatenate(([0.0], np.cumsum(0.5 * (medida[:-1] + medida[1:]) * anchos)))
    exacta_integral = np.array([_integral_exacta(a, x) for x in t])

    error_derivada = float(np.sqrt(np.mean((derivada - exacta_derivada) ** 2)))
    error_integral = float(np.sqrt(np.mean((integral - exacta_integral) ** 2)))
    ruido_medido = float(np.std(medida - real))

    figura, (eje1, eje2, eje3) = plt.subplots(3, 1, figsize=(6.5, 11))

    eje1.plot(t, medida, color="0.65", lw=0.8, label="señal medida")
    eje1.plot(t, real, "k--", lw=1.6, label="señal real")
    _estilo(eje1, f"1) La señal y su ruido (σ = {ruido})", "tiempo (s)", "f(t)")
    eje1.legend(fontsize=8, loc="upper right")

    eje2.plot(t, derivada, color="tab:red", lw=0.8, label="derivada de la señal medida")
    eje2.plot(t, exacta_derivada, "k--", lw=1.6, label="derivada exacta")
    _estilo(eje2, "2) Derivar: el ruido se multiplica y tapa la curva", "tiempo (s)", "f'(t)")
    eje2.legend(fontsize=8, loc="upper right")

    eje3.plot(t, integral, "b-", lw=2, label="integral de la señal medida")
    eje3.plot(t, exacta_integral, "k--", lw=1.6, label="integral exacta")
    _estilo(eje3, "3) Integrar: las dos curvas se pegan", "tiempo (s)", "integral acumulada")
    eje3.legend(fontsize=8, loc="upper left")

    figura.tight_layout()
    plt.show()

    mostrar(
        f"**Ruido en la señal:** `{ruido_medido:.4f}` (desviación estándar de lo "
        "que el sensor agrega a la curva real).\n\n"
        "| Operación | Error medio (RMS) | Respecto al ruido |\n|---|---|---|\n"
        f"| derivar | {error_derivada:.4f} | × {error_derivada / ruido_medido:.0f} |\n"
        f"| integrar | {error_integral:.4f} | × {error_integral / ruido_medido:.2f} |\n\n"
        f"Al final del intervalo, la integral medida se aparta de la exacta apenas "
        f"`{abs(integral[-1] - exacta_integral[-1]):.4f}` sobre un total de "
        f"`{exacta_integral[-1]:.4f}`.\n\n"
        "*Derivar resta dos muestras vecinas y divide entre un paso pequeño: el "
        "ruido entra completo y multiplicado. Integrar suma muchos valores y las "
        "fluctuaciones de signo opuesto se compensan: el ruido crece como la raíz "
        "del número de muestras, mientras la señal crece con el número de muestras, "
        "así que el error relativo baja.*"
    )
    return {"ruido": ruido_medido, "error_derivada": error_derivada,
            "error_integral": error_integral}
