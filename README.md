# 🧮 Unidad 5: Derivadas, integrales y ecuaciones diferenciales

Segunda versión del repositorio de la Unidad 5 (Métodos Numéricos, ITH 2026).

> ⚠️ **En construcción.** La arquitectura está cerrada en
> [plan U5_derivadas_integrales_EDO_V2.md](plan%20U5_derivadas_integrales_EDO_V2.md);
> los cuadernos y el motor se están escribiendo.

---

## 🎯 Qué se aprende

**Elegir el método**, no transcribir el algoritmo. Cada cuaderno explica los
métodos del libro, enseña **cómo se llaman en Python y en MATLAB**, y termina
con un caso de ingeniería personalizado. Solo se programa a mano lo sencillo:
lo que de verdad se escribe en un microcontrolador a alta velocidad.

| Cuaderno | Tipo | Qué se programa |
|---|---|---|
| **01 Derivación** | diferencias hacia atrás y centrada | `derivada_atras`, `derivada_centrada` |
| **02 Integración** | reglas del rectángulo | `integral_izquierda`, `integral_derecha`, `integral_punto_medio` |
| **03 EDO de un paso** | Euler | `euler_paso` |
| **04 Multipaso y rigidez** | catálogo | *nada*: se decide qué solver usar |
| **05 Proyecto integrador** | motor de CD | se combinan las funciones anteriores |

Cinco funciones en toda la unidad. Todo lo demás —trapecio, Simpson, Heun,
RK4, Adams–Bashforth–Moulton, BDF, LSODA— se ve en su forma teórica, con su
equivalente en `numpy`/`scipy` y en MATLAB, y con **cuándo usarlo y cuándo no**.

---

## 🧭 Cómo se recorre un cuaderno

Siempre la misma secuencia, para que la navegación no cueste:

1. **1.1 Entorno** — Drive y librerías (Colab) o archivos locales.
2. **1.2 Cuenta** — tu correo y tu número de control siembran tus datos.
3. **2.1 · 2.2** — introducción al tema, diferencias entre métodos y primera
   pregunta teórica.
4. **3.1–3.5 «hazlo»** — teoría con figura explicada → procedimiento a mano con
   *tus* datos → programas la función en el cuaderno → laboratorio → pregunta.
5. **4.1–4.4 «decídelo»** — el resto de los métodos: ecuación, cómo se llaman
   en Python y MATLAB, celda para configurarlos y pregunta.
6. **n-1 Caso de ingeniería** — tus parámetros, el método lo eliges tú.
7. **n Calificar · Enviar · Consultar.**

---

## 📁 Mapa del repositorio

```text
U5_derivadas_integrales_EDO_V2/
├── notebooks/      # los cinco cuadernos (autocontenidos)
├── lib/            # robomat.py (base del curso) y graficos.py (laboratorios)
├── grader/         # un blob por cuaderno, lo que carga Colab
├── docs/           # catálogo de métodos, teoría, casos y figuras
├── config/         # parámetros públicos (sin credenciales)
├── tools/          # verificar, figuras, sitio, simulación de Colab
├── tests/          # referencias contra los ejemplos del libro
└── site/           # plantilla del sitio en GitHub Pages
```

Cada pregunta del motor son dos archivos con el mismo nombre: el `.md` con el
enunciado y el `.py` con la respuesta. Viven en la rama `test`.

---

## 🚀 Cómo se usa

**En VS Code (local).** Abre el cuaderno y ejecuta la celda 1.1: detecta los
archivos del repositorio y no pide nada.

**En Google Colab.** Abre el cuaderno desde tu fork público; la celda 1.1 monta
tu Drive una vez, guarda el enlace de tu fork y refresca el material del curso
en cada ejecución. No hay que editar archivos ni hacer commits: todo se escribe
dentro del cuaderno.

---

## 🌿 Ramas

- **`main`** — material del alumno: cuadernos, `lib/`, `docs/`, `grader/`.
- **`test`** — el motor (`privado/`), el banco de preguntas, las referencias y
  las credenciales. Nada de esto se publica.

---

## 📖 Fuente

Libro *Métodos numéricos para ingenieros*, 7ª edición: capítulo 6
(diferenciación e integración numérica, temas 21–24) y capítulo 7 (ecuaciones
diferenciales ordinarias, temas 25–28). Las ecuaciones y figuras conservan la
numeración del libro; las extensiones (tiempo real, sensores, motores) van
marcadas como tales.
