# 🎓 Proyecto final — Métodos Numéricos

> Entrega individual. Demuestra que sabes **usar** los métodos numéricos vistos
> en toda la materia para resolver un problema real de ingeniería, y que puedes
> **explicar** el algoritmo que hay detrás de cada función.

## 📋 Qué entregar

Un solo documento (Markdown o PDF) con las secciones de abajo. El código que
usaste va pegado en bloques, y la explicación del algoritmo en tus propias
palabras (no copies la documentación).

## 1. Título y contexto

- Nombre del proyecto y una frase que diga **qué problema de ingeniería
  resuelve** (ej.: "Cálculo del esfuerzo en una viga", "Seguimiento de la
  temperatura de un motor", "Dimensionamiento de un circuito RC").
- Por qué es un problema que necesita métodos numéricos (¿no tiene solución
  analítica?, ¿son datos experimentales?, ¿es una EDO no lineal?).

## 2. Métodos que usaste

| Método | Unidad | Qué hiciste con él |
|---|---|---|
| (ej.) Bisección / Newton-Raphson | U2 | encontrar la raíz de … |
| (ej.) Eliminación de Gauss | U3 | resolver el sistema de … |
| (ej.) Regresión por mínimos cuadrados | U4 | ajustar la curva de … |
| (ej.) `solve_ivp` (Runge-Kutta) | U5 | simular la dinámica de … |
| (ej.) `np.trapezoid` / `simpson` | U5 | integrar … |

> Mínimo **dos** métodos de unidades distintas. Explica por qué elegiste cada
> uno y no otro (criterio: costo, precisión, tipo de dato, rigidez…).

## 3. Algoritmo (lo importante)

Para **cada** método, en una sección corta:

1. **Qué hace** el método, con la ecuación principal (en `$...$`).
2. **Cómo funciona por dentro** (los pasos: iteración, actualización, criterio
   de paro). Aquí puedes apoyarte en las implementaciones de referencia de
   `lib/` de la materia.
3. **Qué función nativa usaste** (numpy/scipy/matlab), con su llamada exacta y
   qué significa **cada argumento** y **cada salida**.
4. **Qué obtuviste** (número, tabla o gráfica) y cómo sabes que es correcto
   (comparación con solución analítica, convergencia al refinar, etc.).

## 4. Resultados y figuras

- Una tabla con los valores clave y, si aplica, una o dos gráficas (método vs.
  solución exacta, convergencia del error, etc.).

## 5. Conclusión

- ¿El método cumplió? ¿Qué limitaciones encontraste (rigidez, paso pequeño,
  error de redondeo, datos ruidosos)? ¿Qué harías distinto?

## ✅ Criterios de evaluación

| Rubro | Puntos |
|---|---|
| Contexto del problema y justificación | 20 |
| Métodos bien elegidos (≥2 de unidades distintas) | 20 |
| Explicación correcta del algoritmo y de entradas/salidas | 30 |
| Resultados reproducibles (código + números + figuras) | 20 |
| Conclusión y análisis crítico | 10 |
