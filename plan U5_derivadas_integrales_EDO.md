# Plan · U5_derivadas_integrales_EDO

Arquitectura y alcance de la segunda versión de la Unidad 5. Toma la forma de
`U4_Repo` (cuadernos + `docs/` + `lib/` + `grader/` + rama `test`) y corrige
tres problemas de la v1:

| # | Problema en v1 | Cómo lo resuelve la v2 |
|---|---|---|
| 1 | El alumno **no programa** nada | Programa **5 funciones cortas** dentro del cuaderno y las compara con la referencia |
| 2 | `lib/mn_motor/` (9 módulos, `_fabrica.py`, `_instalar()`, `sys.modules` sintéticos): F12 no lleva a ningún lado | Paquete plano `privado/` (7 módulos), API de 10 funciones, profundidad máxima 3 llamadas, una pregunta = dos archivos |
| 3 | Lo secreto y lo público mezclados en `main` | `main` = material del alumno; `test` = motor, preguntas, respuestas y credenciales |

---

## 0. Objetivos (el faro: si una decisión no sirve a uno de estos, no se toma)

**Del alumno**

1. **Elegir el método.** Es el objetivo principal de la unidad, sobre todo en
   ecuaciones diferenciales. Los cuadernos no forman programadores: forman
   gente que sabe qué configuración usar y por qué.
2. **Saber cómo se llama cada método en Python y en MATLAB**, para poder
   configurarlo después aunque hoy no lo implemente.
3. **Programar solo lo sencillo**, lo que de verdad se escribe a mano en un
   microcontrolador: diferencias hacia atrás/centrada, reglas del rectángulo y
   un paso de Euler. **Seis funciones** en toda la unidad.
4. **Hacer a mano** esos mismos métodos con sus datos personales, porque el
   orden de error y el compromiso `h`-ruido se entienden con lápiz.
5. **Cerrar con un caso de ingeniería personalizado** por cuaderno y con un
   proyecto integrador propio.

**Del profesor**

6. **Navegar el repo como humano**: un archivo por cosa, nombre que dice qué
   es, sin saltos de cuatro niveles para depurar.
7. **Calificar sin backend frágil**: todo se verifica en el cuaderno; el envío
   es opcional y degrada con elegancia.
8. **Un solo lugar para lo privado** (rama `test`): preguntas, respuestas,
   referencias, tolerancias finas y credenciales.

---

## 1. Principios de diseño

1. **Plano antes que DRY.** Si abstraer obliga a saltar cuatro archivos para
   entender una llamada, se duplica.
2. **Profundidad máxima: 3.** `celda → privado/api.py → un módulo`. Sin
   despacho por diccionarios de callables, sin fábricas, sin metaclases, sin
   módulos creados al vuelo.
3. **Una pregunta = un `.md` + un `.py` con el mismo nombre.** El `.md` es el
   examen; el `.py` es la respuesta, el peso y la retroalimentación.
4. **Todo se resuelve en el cuaderno.** El alumno no edita archivos, no hace
   commits, no usa Codespaces. `lib/` es de solo lectura.
5. **Masticado, pero no resuelto.** Todo lo que no sea de la materia viene
   dado; el método y el algoritmo no (§12).

---

## 2. Mapa del repositorio — rama `main` (público)

```text
U5_derivadas_integrales_EDO/
├── README.md
├── plan U5_derivadas_integrales_EDO.md   # este archivo
├── requirements.txt                # numpy, matplotlib, scipy
├── pyrightconfig.json
├── .devcontainer/devcontainer.json
├── .github/workflows/pages.yml
│
├── notebooks/                      # LOS CINCO CUADERNOS
│   ├── U5_01_Derivacion_Numerica.ipynb
│   ├── U5_02_Integracion_Numerica.ipynb
│   ├── U5_03_EDO_Un_Paso.ipynb
│   ├── U5_04_EDO_Multipaso.ipynb
│   └── U5_05_Proyecto_Integrador.ipynb
│
├── lib/                            # material de consulta, solo lectura
│   ├── robomat.py                  # base del curso (API intacta, copiada de U4)
│   └── graficos.py                 # laboratorio(): una función por subtema
│
├── grader/                         # lo que el cuaderno carga en Colab
│   ├── u5_01_derivacion.txt        # blob base64+zlib (§11)
│   ├── u5_02_integracion.txt
│   ├── u5_03_edo_un_paso.txt
│   ├── u5_04_edo_multipaso.txt
│   └── u5_05_integrador.txt
│
├── docs/
│   ├── guias/catalogo_metodos.md   # LA tabla maestra (§6)
│   ├── guias/guia_integrador.md
│   ├── metodos/                    # teoría de apoyo, 01…05 .md
│   ├── aplicaciones/               # fichas de ingeniería
│   ├── casos_estudio/              # problema → método → código → comparación
│   └── figuras/libro/              # figuras del libro + manifest.csv
│
├── config/config.yaml              # parámetros públicos; credenciales vacías
├── site/                           # plantilla HTML/CSS del sitio
├── tools/                          # verificar.py, generar_figuras.py,
│                                   # build_site.py, simular_colab.py,
│                                   # revisar_cuadernos.py
└── tests/test_privado.py           # pruebas del motor (rama test)
```

`.gitignore` de `main`:

```text
__pycache__/  *.pyc  .ipynb_checkpoints/  .venv/
privado/                       # el motor vive en la rama test
config/privado.yaml            # credenciales
tests/test_privado.py
tools/build_grader.py
tools/revisar_preguntas.py
notebooklm/  _tmp_*  *.tmp  _site/
```

> `grader/*.txt` **sí** se publica: es el motor ofuscado, igual que en U4. Lo
> que no se publica es el código legible ni las respuestas en claro.

---

## 3. Ramas: en `test` se trabaja, en `main` se publica

**`test` es la rama de trabajo y contiene todo**: lo público y lo privado. Aquí
se desarrolla y se depura en local, **sin** construir el paquete de `grader/`.

**`main` es la rama publicada y contiene solo lo público.** No se edita a mano:
se actualiza copiando rutas desde `test`. Nunca con `git merge test`, porque el
merge arrastraría `privado/` y las respuestas — `.gitignore` no detiene a un
archivo que ya está rastreado en la otra rama.

Receta de publicación (solo cuando toque probar de verdad en Colab):

```powershell
git switch main
git checkout test -- notebooks lib docs site tools config/config.yaml `
                     README.md "plan U5_derivadas_integrales_EDO.md" grader
git commit -m "Publica U5 v2" -- notebooks lib docs site tools config/config.yaml `
                                README.md "plan U5_derivadas_integrales_EDO.md" grader
git switch test
```

`grader/` entra en esa lista **después** de correr `tools/build_grader.py`
(fase F8). Durante el desarrollo no se empaqueta nada: como `privado/` existe en
el árbol, la celda 1.1 del cuaderno arranca en modo local, que es el modo en el
que se depura con F12 y `pdb`.

| Rama | Contiene | Cuándo se toca |
|---|---|---|
| `test` | todo: público + `privado/` + preguntas | todos los días, commit por cambio |
| `main` | solo lo público + `grader/*.txt` | al publicar, copiando rutas |

Regla de oro: **si revela una respuesta o una credencial, solo vive en `test`.**

---

## 4. El contrato del motor — `privado/api.py`

Once funciones (diez renglones), todas de menos de 15 líneas, todas
documentadas.

| Función | Devuelve | Qué hace | Numeral |
|---|---|---|---|
| `identificacion(email=None, nombre=None)` | `dict` | Identidad, número de control, semilla | 1.2 |
| `mano_enunciado(clave)` | `dict` | Datos sembrados + texto del ejercicio a mano | 3.2 |
| `mano_comprueba(clave, valor)` | `bool` | Compara con tolerancia, sin revelar la respuesta | 3.2 |
| `practica(funcion)` | `bool` | Corre la función del alumno contra la referencia | 3.3 |
| `pregunta(n)` | `bool` | Muestra el `.md` de la pregunta `n` y la revisa | 2.2, 3.5, k.4 |
| `caso()` | `dict` | Enunciado del caso personalizado + métodos admitidos | n-1.1 |
| `caso_revisar(metodo, resultados)` | `dict` | Rúbrica: método + resultados | n-1.1 |
| `ver_preguntas()` | `None` | Lista preguntas, pesos y estado | — |
| `calificar()` | `tuple[int, int]` | Puntaje y máximo (100) | n.1 |
| `enviar(email)` / `consultar_calificacion(email=None)` | `dict` | Backend | n.2 / n.3 |

- **`practica(funcion)` recibe la función, no un nombre.** Nada de `user_ns`
  ni `globals()`: `practica(derivada_atras)`; el identificador sale de
  `funcion.__name__`. Si no está en el registro, el error lista los válidos.
- **Un solo identificador por método en `snake_case`**, el mismo en
  `ESPECIFICACIONES`, en la clave del a mano y en el `def` del cuaderno.
- `ESPECIFICACIONES` en `referencia.py` es la fuente única de aridad,
  tolerancia y referencia:
  ```python
  ESPECIFICACIONES = {
      "derivada_atras": {
          "firma": "derivada_atras(t, y, i)",
          "referencia": _ref_derivada_atras,
          "casos": [...],
          "tol": 1e-9,
      },
      ...
  }
  ```

---

## 5. Tipos de subtema: "hazlo" y "decídelo"

No todos los subtemas se programan. Hay **dos plantillas**, y el cuaderno
siempre empieza con la misma secuencia de arranque.

### Arranque (igual en los cinco cuadernos)

| Numeral | Celda | Tipo | Qué tiene |
|---|---|---|---|
| **1.1** | 1 | código | **Entorno**: monta el Drive del alumno y deja ahí el material del curso (`lib/` y el paquete del motor), sin pedir nada por teclado ni hablar de repositorios; importa `robomat`, deja la API lista (§11) |
| **1.2** | 2 | código | **Cuenta**: `identificacion()` — email, nombre, número de control, semilla |
| **2.1** | 3 | markdown | **Introducción general del tema** y diferencias entre métodos, con figuras explicadas |
| **2.2** | 4 | código | **Pregunta teórica 1** (personalizada) |

### Subtema tipo A · "hazlo" (uno por cuaderno, dos en el 01 y 02)

Lo que de verdad se escribe a mano en un microcontrolador.

| Numeral | Celda | Tipo | Qué tiene |
|---|---|---|---|
| **3.1** | md | MD | Introducción matemática: ecuación numerada, figura **con lectura** |
| **3.2** | 2 celdas | código | `mano_enunciado("clave")` → `mano_comprueba("clave", valor)` |
| **3.3** | md + 2 celdas | MD/código | Contrato y pistas · `def` con docstring y `NotImplementedError` ← **el alumno escribe el cuerpo** · `practica(funcion)` |
| **3.4** | código + md | Código | `laboratorio("clave")`: el método contra la librería en 2–3 casos, y **qué observar** |
| **3.5** | código | código | **Pregunta teórica 2** (personalizada) |

### Subtema tipo B · "decídelo" (los demás métodos del libro)

El método no se programa: se entiende, se sabe llamar y se sabe cuándo usar.

| Numeral | Celda | Tipo | Qué tiene |
|---|---|---|---|
| **k.1** | md | MD | Ecuación, figura con lectura, orden de error y costo |
| **k.2** | md | MD | **Cómo se llama en Python y en MATLAB** (tabla) + cuándo usarlo y cuándo no |
| **k.3** | 1 celda | código | **Configúralo**: llamada a la librería con los parámetros del método, comentada y ejecutable. El alumno cambia parámetros, no escribe el algoritmo |
| **k.4** | código | código | **Pregunta teórica** (personalizada) |

### Cierre (igual en los cinco)

| Numeral | Qué |
|---|---|
| **n-1.1** | `caso()` → trabajo del alumno → `caso_revisar(metodo, resultados)` |
| **n-1.2** | Preguntas del caso (personalizadas) |
| **n.1 · n.2 · n.3** | `calificar()` · `enviar(email)` · `consultar_calificacion(email)` |

Reparto de preguntas: **3 por cuaderno** (una en 2.2, una en el subtema tipo A,
una en el cierre del caso). 12 de contenido + 3 del integrador = **15**.

---

## 6. Contenido por cuaderno

### U5_01 · Derivación numérica y diferenciación en tiempo real

| Numeral | Tipo | Contenido | Programar |
|---|---|---|---|
| 2.1 | MD | Diferencias finitas: adelante, atrás, centrada; amplificación de ruido | — |
| **3** | **A** | Diferencias simples | `derivada_atras(t, y, i)`, `derivada_centrada(t, y, i)` |
| 3.4 | — | Lab: las dos contra `np.diff` y `np.gradient` | — |
| **4** | **B** | Derivadas de orden superior, ruido, filtrado y `np.gradient` | — |
| n-1.1 | caso | Brazo robótico con encoder ruidoso: estimar velocidad y aceleración | — |

Catálogo del subtema 4: `np.diff` · `np.gradient` · `np.convolve` (media móvil)
· `scipy.signal.savgol_filter` ‖ MATLAB: `diff` · `gradient` · `filter` ·
`sgolayfilt`.

### U5_02 · Integración numérica e integradores en tiempo real

| Numeral | Tipo | Contenido | Programar |
|---|---|---|---|
| 2.1 | MD | Newton–Cotes: del rectángulo a Simpson; qué gana cada orden | — |
| **3** | **A** | Reglas del rectángulo | `integral_izquierda(t, y)`, `integral_derecha(t, y)`, `integral_punto_medio(t, y)` |
| 3.4 | — | Lab: las tres contra `np.trapezoid` en la misma señal | — |
| **4** | **B** | Trapecio, Simpson 1/3 y 3/8, intervalos desiguales | — |
| n-1.1 | caso | Coulomb counting de SoC en batería Li-Ion con `dt` irregular | — |

Catálogo del subtema 4: `np.trapezoid` · `scipy.integrate.simpson` ·
`scipy.integrate.cumulative_trapezoid` · `scipy.integrate.quad` ‖ MATLAB:
`trapz` · `cumtrapz` · `integral`. (Simpson no tiene función estándar en
MATLAB: se compone con `trapz` sobre refinamiento.)

### U5_03 · EDO de un paso

| Numeral | Tipo | Contenido | Programar |
|---|---|---|---|
| 2.1 | MD | PVI de primer orden; Euler, Heun, RK4: qué gana cada orden | — |
| **3** | **A** | Un paso de Euler dentro de un lazo de control | `euler_paso(f, t, y, h)` |
| 3.4 | — | Lab: un paso de Euler vs `solve_ivp(RK45)` vs solución exacta | — |
| **4** | **B** | Heun, punto medio, RK4 y el mapa de solvers | — |
| n-1.1 | caso | Masa-resorte-amortiguador: reducir 2º orden a sistema | — |

Catálogo del subtema 4: `scipy.integrate.solve_ivp` (`RK45`, `RK23`, `DOP853`)
· `scipy.integrate.odeint` ‖ MATLAB: `ode45` · `ode23` · `ode113`.

### U5_04 · EDO multipaso y rigidez — **sin subtema tipo A**

| Numeral | Tipo | Contenido |
|---|---|---|
| 2.1 | MD | Por qué existen los multipaso: menos evaluaciones de `f` |
| **4** | **B** | Adams–Bashforth, Adams–Moulton, predictor-corrector y el problema del arranque |
| **5** | **B** | Rigidez: qué es, cómo se diagnostica (`nfev`), qué solver usar |
| n-1.1 | caso | Motor de CD con inercia y transitorio inductivo |

Catálogo: `solve_ivp` (`BDF`, `Radau`, `LSODA`) ‖ MATLAB: `ode15s` · `ode23s` ·
`ode113` (Adams–Bashforth–Moulton de orden variable). Aquí no se programa nada:
es el cuaderno donde **decidir** es todo el ejercicio.

### U5_05 · Proyecto integrador

Solo el proyecto. Sin teoría nueva. §8.

### Guías por cuaderno — `docs/guias/`

Una guía por cuaderno, más un índice con la tabla de decisión rápida:

```text
docs/guias/
├── README.md                     # índice + decisión rápida + errores típicos
├── catalogo_01_derivacion.md
├── catalogo_02_integracion.md
├── catalogo_03_edo_un_paso.md
└── catalogo_04_edo_multipaso.md
```

Cada guía trae las ecuaciones, una tabla `Método · En Python · En MATLAB ·
Cuándo sí · Cuándo no`, y **las figuras del libro que le tocan, incluidas en el
documento y con su lectura**. Cada subtema tipo B cita la suya; el cuaderno 05
usa el índice como chuleta. Es el artefacto que responde "qué usar en cada
caso" sin abrir cinco cuadernos.

Reglas de estas guías:

1. **Sin enlaces a rutas locales**: los cuadernos se leen en Colab y en GitHub,
   así que todo enlace es una URL absoluta.
2. **Sin notas de autor**: nada de explicar cómo se escribe el markdown ni cómo
   se comporta Colab. Eso vive en este plan, no en el material del alumno.
3. **Ninguna figura anunciada sin incluirla.** Si se menciona una figura, va la
   imagen y su lectura; si no hay imagen disponible, se escribe la fórmula y se
   cita el libro, sin prometer figuras.

---

## 7. Figuras y explicación de métodos

- Toda figura del libro se extrae de `Contenido/Markdown/Ed7/<cap>_images/
  page_XXXX/N.jpg` (179 imágenes disponibles; §10).
- **Ninguna figura entra sin lectura**: 2–4 líneas con *qué muestra*, *qué
  concluye* y *qué limitación tiene el método*. Una figura sin esas tres cosas
  se borra.
- La imagen va en su propio markdown, **fuera de las tablas** (ver §13).
- Numeración de ecuaciones y figuras: la del libro. Las extensiones (tiempo
  real, sensores, motores) van marcadas como tales.

---

## 8. Cuaderno 05 · Proyecto integrador

**Enunciado.** Motor de CD con carga inercial; $R$, $L$, $K_t$, $J$, $b$ solo
existen en la semilla del alumno.

- **Parte A · lazo causal (25).** Bucle a $\Delta t = 1$ ms con el `euler_paso`
  que ya programó en el cuaderno 03.
- **Parte B · indicadores (15).** Derivar la aceleración angular e integrar la
  corriente con las funciones de los cuadernos 01 y 02.
- **Parte C · solver (30).** Repetir con `solve_ivp` eligiendo método
  (`RK45`, `RK23`, `BDF`, `LSODA`); reportar `nfev` y `status`.
- **Parte D · conclusión (30).** Justificar el método: pregunta de opción
  múltiple con sus números.

Grado de masticado: ecuación completa, esqueleto con `TODO` y variables ya
nombradas, 3–4 pistas por parte (§12), celda de verificación por parte y tabla
síntomas → causa → qué cambiar. Nada de optimización, estadística ni control.

`docs/guias/guia_integrador.md` repite el enunciado en versión larga, para
imprimir.

---

## 9. Banco de preguntas con variables por semilla

1. El `.md` declara huecos con doble llave:
   ```markdown
   El encoder entrega $N = {{N}}$ pulsos por vuelta y el lazo corre a
   $T = {{T}}\ \mathrm{ms}$. ¿Qué pasa si reduces $h$ a la mitad?
   ```
2. El `.py` de la misma pregunta define `variables(semilla) -> dict[str, str]`
   con `random.Random(semilla)`.
3. `banco.py` sustituye. Si falta un hueco o sobra, **falla ruidosamente** con
   el nombre del archivo.

`tools/revisar_preguntas.py` verifica: existe el `.md`; exactamente una `[x]`;
su índice coincide con `CORRECTA`; `revisar(CORRECTA)` da `True`;
`variables(semilla)` cubre todos los huecos en 50 semillas y produce al menos
3 combinaciones distintas. Las preguntas fijas usan `variables` que devuelve
`{}`, para que haya un solo camino.

---

## 10. ¿Se puede calificar según el método elegido? Sí, y así

1. **Método declarado.** El `.py` del caso declara:
   ```python
   METODOS = {
       "BDF":   {"puntos": 30, "tol": 1e-6, "nota": "óptimo para este caso"},
       "RK45":  {"puntos": 30, "tol": 1e-6, "nota": "aceptable; más caro"},
       "LSODA": {"puntos": 25, "tol": 1e-6, "nota": "aceptable"},
       "Euler": {"puntos": 8,  "tol": 1e-2, "nota": "no apto: paso fijo"},
   }
   ```
   Los resultados se comparan **contra la referencia de ese mismo método**, cada
   uno con su tolerancia: no hay una única verdad.
2. **Justificación.** Pregunta de opción múltiple con los números de su semilla.
3. **Detección por firma (solo aviso).** Si el método declarado no coincide con
   el que produjo sus números (`nfev`, orden del error), `caso_revisar` lo
   reporta sin castigar: sirve para detectar copias y para retroalimentar.

Nunca se evalúa a ojo: tolerancia relativa contra la referencia recalculada con
la semilla.

---

## 11. Figuras del libro: disponibilidad y mecanismo

| Capítulo | Carpeta en `Ed7/` | Imágenes |
|---|---|---|
| 6 · Introducción | `P6_Introduccion_images` | 25 |
| 21 · Newton–Cotes | `P6_21_…_newton_cotes_images` | 23 |
| 22 · Integración de ecuaciones | `P6_22_Integracion_de_ecuaciones_images` | 8 |
| 23 · Diferenciación numérica | `P6_23_Diferenciacion_numerica_images` | 8 |
| 24 · Casos de integración y diferenciación | `P6_24_…_images` | 15 |
| 7 · Introducción EDO | `P7_Introduccion_images` | 7 |
| 25 · Runge–Kutta | `P7_25_Metodos_de_runge_kutta_images` | 19 |
| 26 · Rígidos y multipaso | `P7_26_…_images` | 17 |
| 27 · Frontera y valores propios | `P7_27_…_images` | 20 |
| 28 · Casos de EDO | `P7_28_…_images` | 37 |

1. `docs/figuras/libro/manifest.csv` — una fila por figura:
   `archivo_destino, capitulo, pagina, indice, numero_libro, pie, cuaderno`.
2. `tools/generar_figuras.py` lee el manifiesto y copia
   `Ed7/<cap>_images/<pagina>/<indice>.jpg` → `docs/figuras/libro/<destino>`.
3. El cuaderno referencia la imagen por nombre; la celda 1.1 la descarga de
   `raw.githubusercontent.com`.

Ya verificadas y en uso en la v1 (se conservan): `fig21_4_trapecio.png`,
`fig21_12_simpson_combinado.png`, `fig23_4_temperatura.png`,
`fig25_9_heun.png`, `fig25_15_rk4.png`, `fig26_6_multipaso.png`.

---

## 12. Política de pistas (masticado sin regalar la respuesta)

Cada pista va en su propio `<details>` para que no estorbe a quien no la
necesita. Tres niveles, en este orden:

| Nivel | Contiene | Ejemplo |
|---|---|---|
| **1 · Dónde** | qué ecuación o capítulo releer | "Revisa la ec. (23.9) del capítulo 23" |
| **2 · Qué forma** | qué entra, qué sale y en qué unidades | "Tu función recibe tres argumentos y devuelve un float en A/s" |
| **3 · Qué propiedad** | qué propiedad del problema o qué función de librería mirar | "`np.gradient` ya está pensado para ejes no uniformes" |

**Prohibido en una pista:** el pseudocódigo, el algoritmo paso a paso, el número
u opción correcta, o el nombre del método cuando justamente eso es lo que se
evalúa. Si una pista se puede copiar y pegar para resolver, sobra.

Los casos y el integrador sí traen **todo lo demás** masticado: física, datos,
unidades, esqueleto con variables nombradas, celda de verificación y tabla
síntomas → causa → qué cambiar.

---

## 13. Reglas de estilo y documentación

- **Ecuaciones largas: siempre `$$ … $$` en línea propia.** Nunca un bloque
  `$$` ni `\tag{}` dentro de una celda de tabla: **Google Colab corta la
  ecuación** cuando la tabla la envuelve. Dentro de una tabla solo se permite
  matemática corta y en línea (`$O(h^2)$`, `$1/h$`); si la ecuación lleva
  fracciones, raíces o varias líneas, va fuera y la tabla la cita como
  "ec. (21.4)".
- Toda figura lleva su lectura de 2–4 líneas (§7).
- **Docstring obligatorio** en toda función pública:
  ```
  <una línea: qué hace>

  Libro: ecuación (X.Y).

  Args:
      <param>: <qué es y unidades>
  Returns:
      <tipo>: <qué significa>
  Raises:
      ValueError: <cuándo>
  Ejemplo:
      >>> derivada_atras([0, .1, .2], [0, .1, .4], 1)
      1.0000000000000002
  ```
- Los módulos empiezan con un docstring que dice **para qué sirve el archivo y
  qué NO hace**.
- `snake_case`, español, sin abreviaturas inventadas.
- Prohibido: `**kwargs` en la API del cuaderno, decoradores que oculten la
  firma, `functools.partial`, imports dentro de funciones, `eval`/`exec` fuera
  de la celda 1.1.
- `lib/graficos.py`: una función `lab_<clave>()` completa por subtema (puede
  repetir el armado de la figura) y un despachador `laboratorio(clave)` de
  cinco líneas. `lib/robomat.py` no se toca.
- Español de México, decimales con punto, unidades explícitas.

---

## 14. Calificación y envío

| Concepto | Puntos | Cómo |
|---|---|---|
| Preguntas teóricas (3 por cuaderno) | 60 (20 c/u) | `revisar()` de cada `.py` |
| Caso de ingeniería | 40 | `caso_revisar()`: método 20 + resultados 20 |
| Actividades a mano | 0 | Solo evidencia; no restan |
| **Cuaderno** | **100** | |

Cuaderno 05: A 25 · B 15 · C 30 · D 30.

- `max_intentos` y tolerancias públicas en `config/config.yaml`; las tolerancias
  finas viven en `ESPECIFICACIONES` (privado).
- **El correo debe ser institucional y traer el número de control**
  (`evaluacion.dominio_correo` en `config/config.yaml`). Si la cuenta de Google
  del alumno no es la institucional, la celda 1.2 lo dice y pide el correo
  correcto: sin número de control no hay identidad verificable, y con una cuenta
  ajena sería fácil entregar por otro.
- Credenciales en orden: entorno → `config/privado.yaml` (rama `test`) → blob.
- `envio.py` es la única función que toca la red. Sin credenciales, `enviar()`
  avisa «modo local: no se envió» y devuelve `{"estado": "local"}`.

---

## 15. Modo local y modo blob

La celda 1.1 hace **una sola decisión**, con dos caminos explícitos:

```python
# ¿Hay código legible? (tú, en local, con la rama test) -> úsalo: F12 y pdb sirven.
# ¿No hay? (alumno en Colab) -> descomprime el paquete de grader/ y sigue igual.
if os.path.isdir(os.path.join(RAIZ, "privado")):
    sys.path.insert(0, RAIZ)
    MODO = "local"
else:
    _dir = pathlib.Path(tempfile.mkdtemp(prefix="u5motor_"))
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(open(BLOB, "rb").read()))) as _zip:
        _zip.extractall(_dir)
    sys.path.insert(0, str(_dir))
    MODO = "blob"

from privado.api import *          # noqa: F403  — igual en los dos modos
```

En Colab, `RAIZ` es la carpeta `CursoMN/material` del **Drive del alumno**: la
celda monta el Drive y deja ahí los tres archivos que hacen falta. El origen de
esos archivos vive en una constante de la celda y **no se muestra en pantalla**:
el alumno no necesita saber de dónde salen, solo que el material está listo.

En ambos modos quedan en el espacio de nombres las mismas once funciones y el
paquete es **código normal**: `import privado.banco` funciona, los `.md` de las
preguntas están en su carpeta y se pueden abrir. La celda imprime la ruta del
temporal, para poder abrir los archivos a mano cuando algo falle.

**Armado del paquete** (`tools/build_grader.py`, rama `test`):

1. Empaqueta en un zip `privado/**/*.py`, `privado/preguntas/**/*.md`,
   `config/config.yaml` y `config/privado.yaml`, más un `LEEME.txt` que explica
   qué es el paquete.
2. Escribe `base64(zip)` en una línea de `grader/<cuaderno>.txt`.
3. Verifica antes de escribir: todo compila; `identificacion()` funciona; un
   alumno perfecto saca 100; el zip trae los archivos esperados.

> **Compromiso consciente:** el paquete lleva `config/privado.yaml`, así que un
> alumno decidido puede leer el token. Es el mismo trato que hace U4, y el Apps
> Script solo permite escribir en la hoja, no leerla. Si algún día molesta, se
> quita del zip y `enviar()` queda en modo local.

> **Por qué zip y no un texto plano concatenado:** con texto plano, `banco.py`
> no podría importar las preguntas (no habría módulos), y habría que inventar
> nombres `_q_...` para no chocar con las funciones del alumno. El zip conserva
> módulos reales y elimina toda esa maquinaria.

---

## 16. Fases

- [x] **F0 · Esqueleto.** Carpetas, `.gitignore`, `requirements.txt`,
      `pyrightconfig.json`, `README.md`, ramas `main` y `test`.
- [x] **F1 · Contrato.** `privado/referencia.py` + `ESPECIFICACIONES` de las 6
      funciones; 23 pruebas contra los ejemplos 21.1, 23.1, 25.1 y 25.5.
- [x] **F2 · Motor.** `privado/api.py`, `banco.py`, `califica.py`, `casos.py`
      (cuaderno 01), `identidad.py`, `envio.py`, `ajustes.py`; 40 pruebas.
      Pendiente de F2: los casos de los cuadernos 02–05.
- [x] **F3 · Guías.** `docs/guias/`: índice con la tabla de decisión rápida y
      una guía por cuaderno, con sus figuras incluidas.
- [ ] **F4 · Preguntas.** 15 preguntas (3 por cuaderno), `.md` + `.py`;
      `revisar_preguntas.py` en verde.
- [x] **F5 · Figuras.** `manifest.csv` + `generar_figuras.py`; extraídas 23.4 y
      23.5 (dos mitades). Faltan las de los cuadernos 02–05 conforme se escriban.
- [x] **F6 · Cuaderno 01.** Generado con `tools/crear_cuadernos.py`; 27 celdas,
      recorrido completo verificado por prueba automática (100/100).
- [ ] **F6 · Cuadernos 02–04.** Con las plantillas de §5 y el contenido de §6.
- [ ] **F7 · Cuaderno 05.** Integrador + `guia_integrador.md`.
- [ ] **F8 · Empaquetado.** 5 blobs; `simular_colab.py` desde fuera del repo.
- [ ] **F9 · Publicación.** `docs/`, sitio, `README`, push de ambas ramas.

---

## 17. Supuestos que tomé

1. **01 programa dos funciones** (atrás y centrada) porque son las dos que se
   usan en un lazo causal; **02 programa tres** (izquierda, derecha, punto
   medio) porque pediste justamente sus variaciones.
2. **04 no programa nada**: es el cuaderno de decidir. Esto revierte la celda
   3.3 que había propuesto antes para `adams_bashforth_moulton`.
3. **`proyecto_final.md` no entra al repo.** El proyecto abierto vive en Google
   Classroom; el repo solo tiene el integrador del cuaderno 05.
4. Pesos 20 por pregunta y 40 por caso (§14).
