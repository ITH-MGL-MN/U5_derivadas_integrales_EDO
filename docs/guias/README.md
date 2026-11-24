# 🧭 Guías de la Unidad 5

Material de consulta del curso de Métodos Numéricos: qué método usar, cómo se
llama en Python y en MATLAB, y cuándo **no** conviene. Cada cuaderno tiene su
propia guía, con las figuras del libro que le corresponden.

> Los cuadernos son la clase; estas guías son la chuleta. Si tienes que decidir
> un método en un examen o en un proyecto, empieza por la tabla de decisión de
> abajo.

## Índice

| # | Guía | Cuaderno | Métodos que cubre |
|---|---|---|---|
| 1 | [Derivación numérica](catalogo_01_derivacion.md) | `U5_01` | diferencias finitas, orden superior, filtrado |
| 2 | [Integración numérica](catalogo_02_integracion.md) | `U5_02` | rectángulo, trapecio, Simpson, cuadratura adaptativa |
| 3 | [EDO de un paso](catalogo_03_edo_un_paso.md) | `U5_03` | Euler, Heun, punto medio, RK4 y los solvers |
| 4 | [EDO multipaso y rigidez](catalogo_04_edo_multipaso.md) | `U5_04` | Adams–Bashforth–Moulton, BDF, Radau, LSODA |
| 5 | Proyecto integrador | `U5_05` | guía en preparación |

Cada guía incluye las figuras del libro que le tocan, con su lectura. Las
imágenes están en [`../figuras/libro/`](../figuras/libro/) y su procedencia
—capítulo, página e índice— queda anotada en el
[manifiesto](../figuras/libro/manifest.csv).

---

## Tabla de decisión rápida

| Si el problema es… | Usa | Porque |
|---|---|---|
| Derivar una señal con ruido | media móvil o `savgol_filter`, **después** centrada | El ruido se amplifica como $1/h$ |
| Derivar dentro de un microcontrolador | diferencia hacia atrás | Es la única causal y cuesta una resta |
| Integrar muestras con paso irregular | trapecio con el ancho de cada intervalo | Newton–Cotes necesita paso uniforme |
| Integrar muestras uniformes y quieres precisión | Simpson 1/3 | Sube de $O(h^2)$ a $O(h^4)$ sin evaluar nada nuevo |
| Integrar una función conocida | `quad` / `integral` | Control de error adaptativo |
| Simular un lazo de control a paso fijo | Euler | Es lo que corre en el microcontrolador |
| Resolver una EDO no rígida | `RK45` / `ode45` | Buen equilibrio entre orden y costo |
| Evaluar la derivada es carísimo | multipaso (`ode113`) | Reutiliza pendientes ya calculadas |
| El número de evaluaciones explota | `BDF` / `ode15s` / `LSODA` | Implícitos: no los limita la estabilidad |
| No sé si el sistema es rígido | `LSODA` | Cambia solo entre explícito e implícito |
| Necesito la solución en instantes exactos | `t_eval=` / `odeset('Refine')` | Evita interpolar a mano |

## Errores que cuestan puntos

1. **Refinar el paso sin mirar el ruido.** El error total tiene un mínimo;
   pasarse de fino empeora la estimación.
2. **Usar Simpson con número impar de intervalos**, o con paso variable.
3. **Confundir error local con global.** Euler es $O(h^2)$ por paso y $O(h)$
   acumulado; en la gráfica se ve la diferencia.
4. **Reportar el resultado de Euler como si fuera el del solver.** Son métodos
   distintos, con errores distintos.
5. **Elegir el método por costumbre.** `ode45` no es "el de MATLAB": es el de
   sistemas no rígidos. En un motor eléctrico suele ganar `ode15s`.
6. **No reportar el número de evaluaciones.** Es la evidencia objetiva de que
   el método elegido era el adecuado; sin ese número, la elección es una
   opinión.

---

## Fuente

Libro *Métodos numéricos para ingenieros*, 7ª edición: capítulo 6 (temas 21–24,
diferenciación e integración) y capítulo 7 (temas 25–28, ecuaciones
diferenciales ordinarias). Las filas marcadas "extensión del curso" no tienen
ecuación en el libro: son las reglas que se usan en un lazo de tiempo real y
que el cuaderno 02 programa a mano a propósito.
