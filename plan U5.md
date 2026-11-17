# 🗺️ Plan — U5: Derivadas, integrales y EDO

> Combina la Parte 6 (diferenciación e integración numéricas) y la Parte 7
> (ecuaciones diferenciales ordinarias) del libro. El alumno **no programa**:
> aprende a usar las funciones nativas de numpy/scipy (y su equivalente en
> MATLAB), entiende sus entradas/salidas y decide cuándo usar cada una.

## Decisiones base

- **Ubicación:** carpeta `U5 derivadas integrales y EDO/` (directo, sin `Repo`).
- **Cuadernos:** 4 (derivación, integración, EDO un paso, EDO multipaso).
- **Enfoque:** teoría (ecuaciones + figuras del libro) → lab con funciones
  nativas → entradas/salidas y diferencias → preguntas teóricas → casos de
  ingeniería comparando métodos → envío/calificación por Apps Script.
- **`lib/derivada_integral.py` y `lib/edo.py`** son implementaciones de
  **referencia** (se muestran para explicar el algoritmo por dentro, no para
  que el alumno las complete). Se verifican contra los ejemplos del libro.
- **Proyecto final:** `proyecto_final.md` (el alumno expone su proyecto y el
  algoritmo de los métodos que usó de toda la materia).

## Alcance temático (programa)

| Tema | Cuaderno | Fuente (libro) |
|---|---|---|
| 5.1 Derivación numérica | 01 | Cap. 23 (diferencias finitas) |
| 5.2 Integración: trapecio, Simpson 1/3 y 3/8 | 02 | Cap. 21 |
| 5.3 Integración con intervalos desiguales | 02 | Cap. 21 (sec. 21.3) |
| 6.1 Fundamentos de EDO | 03 | Parte 7 (intro) |
| 6.2 Métodos de un paso: Euler, Euler mejorado, RK | 03 | Cap. 25 |
| 6.3 Métodos de pasos múltiples | 04 | Cap. 26 |

## Mapeo de funciones nativas

| Tema | numpy/scipy | MATLAB |
|---|---|---|
| Derivación | `np.gradient(y, x)`, `np.diff(y)/np.diff(x)` | `gradient`, `diff` |
| Trapecio | `np.trapezoid(y, x)` | `trapz` |
| Simpson | `scipy.integrate.simpson(y, x)` | `integral` |
| Desiguales | `np.trapezoid(y, x)` / `simpson(y, x)` con `x` irregular | `trapz(x, y)` |
| EDO un paso | `solve_ivp(f, t_span, y0, method='RK45'|'RK23'|'DOP853')` | `ode45`, `ode23` |
| EDO multipaso/rígidas | `solve_ivp(method='LSODA'|'BDF')`, `odeint` | `ode15s`, `ode113` |

## Fases

### Fase 0 — Estructura ✅
- [x] Carpeta + `config/config.yaml`, `.gitignore`, `pyrightconfig.json`,
      `requirements.txt`, `.devcontainer`.
- [x] `lib/robomat.py` (copiado de U4, sin cambios de API).

### Fase 1 — Contenido del libro ✅
- [x] Extracción de P6-21, P6-23, P7-Intro, P7-25, P7-26 →
      `docs/_extraccion_p6.json` y `docs/_extraccion_p7.json`.

### Fase 2 — Biblioteca de referencia y pruebas ✅
- [x] `lib/derivada_integral.py` (trapecio, Simpson 1/3 y 3/8, desiguales,
      derivadas).
- [x] `lib/edo.py` (Euler, Heun/Euler mejorado, RK4, Adams-Bashforth-Moulton).
- [x] `tests/` contra los ejemplos publicados del libro (12 pruebas en verde).

### Fase 3 — Cuadernos (pendiente)
- [ ] `U5_01_Derivacion_Numerica.ipynb` (5.1)
- [ ] `U5_02_Integracion_Numerica.ipynb` (5.2 + 5.3)
- [ ] `U5_03_EDO_Un_Paso.ipynb` (6.1 + 6.2)
- [ ] `U5_04_EDO_Multipaso.ipynb` (6.3 + casos)

### Fase 4 — Motor, preguntas y blobs (pendiente)
- [ ] `lib/mn_motor/` + `preguntas/` (teóricas por cuaderno).
- [ ] `tools/build_grader.py` + blobs en `grader/`.

### Fase 5 — Proyecto final (pendiente)
- [ ] `proyecto_final.md` (plantilla).

## Ramas

- **`test`** — trabajo (motor + preguntas).
- **`main`** — material público + blob ofuscado.
