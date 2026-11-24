# 🧭 Catálogo de métodos: qué usar en cada caso

Esta es la tabla maestra de la Unidad 5. Los cuadernos la citan en cada subtema
"decídelo" y el proyecto integrador la usa como chuleta.

**Cómo leerla.** Cada método aparece con su ecuación del libro, su nombre exacto
en Python y en MATLAB, cuándo conviene y cuándo no. No hace falta memorizar la
fórmula: lo que se evalúa es la **decisión**.

> 📐 **Sobre las ecuaciones.** Se citan con la numeración del libro (*Métodos
> numéricos para ingenieros*, 7ª ed.). Las que son demasiado largas van en un
> bloque `$$` aparte, nunca dentro de una tabla: **Google Colab corta las
> ecuaciones que quedan dentro de una tabla**, y una fórmula cortada enseña
> mal. En las tablas solo se cita el número: "ec. (21.14)".

---

## 1 · Derivación numérica

Las tres diferencias básicas están en las figuras 23.1 a 23.3 (no llevan número
de ecuación propio):

$$
f'(x_i) \approx \frac{f(x_{i+1})-f(x_i)}{h}
\quad\text{(adelante, } O(h)\text{)}
$$

$$
f'(x_i) \approx \frac{f(x_i)-f(x_{i-1})}{h}
\quad\text{(atrás, } O(h)\text{)}
$$

$$
f'(x_i) \approx \frac{f(x_{i+1})-f(x_{i-1})}{2h}
\quad\text{(centrada, } O(h^2)\text{)}
$$

Con datos irregularmente espaciados, la centrada se generaliza dividiendo entre
el intervalo total, que es la ecuación (23.9) aplicada al caso lineal.

| Método | Ecuación | En Python | En MATLAB | Cuándo usarlo | Cuándo **no** |
|---|---|---|---|---|---|
| Diferencia hacia atrás | fig. 23.2, $O(h)$ | `(y[1:]-y[:-1])/dt` | `diff(y)./diff(t)` | Lazo de tiempo real: en el instante actual solo tienes la muestra actual y la anterior | Cuando puedes esperar una muestra más: la centrada cuesta lo mismo y gana un orden |
| Diferencia centrada | fig. 23.3, $O(h^2)$ | `np.gradient(y, t)` | `gradient(y, t)` | Lo normal fuera de línea, o en línea si toleras un retardo de una muestra | Primer y último punto (necesita vecino a cada lado); señales con escalones |
| Adelantada | fig. 23.1, $O(h)$ | `(y[1:]-y[:-1])/dt` desplazado | `diff(y)./diff(t)` | Solo si el sistema es predictivo y necesitas el valor futuro | Casi nunca: no es causal y no gana precisión |
| Derivada de datos con espaciado desigual | (23.9) | `np.gradient(y, t)` | `gradient(y, t)` | Muestras tomadas por un bus CAN o un event loop irregular | Cuando ya sabes que los tiempos son uniformes: complica sin ganar |
| Extrapolación de Richardson | (23.8) | a mano, con dos mallas | a mano, con dos mallas | Necesitas más orden con la misma malla y los datos están limpios | Con ruido: amplifica el error de medición |
| Segunda derivada | figs. 23.1–23.3, $O(h^2)$ | `np.gradient(np.gradient(y, t), t)` | `gradient(gradient(y, t), t)` | Aceleración a partir de posición | Sin filtrar antes: el ruido se amplifica como $1/h^2$ y el resultado es basura |

**Cómo se llaman en Python:**

```python
import numpy as np
np.diff(y)                 # diferencias simples, sin dividir entre dt
np.gradient(y, t)          # diferencia centrada; acepta el eje t no uniforme
np.convolve(y, np.ones(7) / 7, mode="same")           # media móvil
from scipy.signal import savgol_filter
savgol_filter(y, window_length=11, polyorder=3)        # suavizado que conserva la forma
```

**Cómo se llaman en MATLAB:**

```matlab
diff(y);  gradient(y, t);
filter(ones(1,7)/7, 1, y)          % media móvil
sgolayfilt(y, 3, 11)               % Signal Processing Toolbox
del2(y)                            % laplaciano (segunda derivada 2D)
```

**La trampa de la derivación.** El error de truncamiento baja con $h$, pero el
ruido **sube** como $1/h$. Reducir $h$ a la mitad mejora cuatro veces el primero
y empeora dos veces el segundo: existe un $h$ óptimo y, por debajo de él,
refinar empeora la estimación. Por eso al derivar dos veces se filtra primero.

---

## 2 · Integración numérica

### 2.1 Las fórmulas

Trapecio simple, ecuación (21.3):

$$
I = (b-a)\,\frac{f(a)+f(b)}{2}
$$

Trapecio múltiple, ecuación (21.9) con $h=(b-a)/n$:

$$
I = \frac{h}{2}\left[f(x_0) + 2\sum_{i=1}^{n-1} f(x_i) + f(x_n)\right]
$$

Simpson 1/3, ecuación (21.14) con $h=(b-a)/2$:

$$
I \cong \frac{h}{3}\left[f(x_0) + 4f(x_1) + f(x_2)\right]
$$

Simpson 3/8, ecuación (21.20):

$$
I \cong (b-a)\,\frac{f(x_0)+3f(x_1)+3f(x_2)+f(x_3)}{8}
$$

Trapecio con datos irregularmente espaciados, ecuación (21.22):

$$
I = \sum_{i=1}^{n} h_i\,\frac{f(x_{i-1})+f(x_i)}{2}
$$

### 2.2 La tabla

| Método | Ecuación | En Python | En MATLAB | Cuándo usarlo | Cuándo **no** |
|---|---|---|---|---|---|
| Rectángulo izquierda / derecha | extensión del curso | suma propia (cuaderno 02) | suma propia | Acumulador dentro de un lazo: `I += y[k]*dt` | Fuera de línea: el trapecio cuesta lo mismo y es mejor |
| Punto medio, datos muestreados | tabla 21.4 | promedio de extremos (cuaderno 02) | igual | Cuando no conoces más que los extremos | Si tienes la función: evalúa en el punto medio de verdad |
| Trapecio | (21.3) y (21.9) | `np.trapezoid(y, t)` | `trapz(t, y)` | Datos tabulados, `dt` irregular, señal suave | Necesitas $O(h^4)$ con pocos puntos |
| Trapecio acumulado | (21.9) | `scipy.integrate.cumulative_trapezoid` | `cumtrapz` | Quieres la integral **en cada instante**, no solo el total | Solo te interesa el total: gasta memoria de más |
| Simpson 1/3 | (21.14) y (21.18) | `scipy.integrate.simpson(y, x=t)` | se compone con `trapz` o `integral` | Función suave y número **par** de intervalos | Número impar de intervalos, o datos con ruido |
| Simpson 3/8 | (21.20) | `scipy.integrate.simpson(y, x=t)` con 3 segmentos | se compone | Cuando el número de intervalos es múltiplo de 3 | Como opción por defecto: 1/3 es más simple y del mismo orden |
| Cuadratura adaptativa | — | `scipy.integrate.quad(f, a, b)` | `integral(f, a, b)` | Tienes la **función** (no muestras) y quieres control del error | Solo tienes muestras; o necesitas el valor en cada instante |

**Cómo se llaman en Python:**

```python
import numpy as np
from scipy import integrate

np.trapezoid(y, t)                              # trapecio (NumPy 2.x; antes np.trapz)
integrate.trapezoid(y, t)                       # lo mismo desde SciPy
integrate.cumulative_trapezoid(y, t, initial=0) # acumulado
integrate.simpson(y, x=t)                       # Simpson, acepta x no uniforme
integrate.quad(f, a, b)                         # adaptativa: devuelve (valor, error)
```

**Cómo se llaman en MATLAB:**

```matlab
trapz(t, y)
cumtrapz(t, y)
integral(@(x) f(x), a, b)        % adaptativa
quadgk(@(x) f(x), a, b)          % Gauss-Kronrod, para precisión alta
```

> En MATLAB **no hay** una función estándar de Simpson. Se resuelve con
> `integral` (que es mejor) o componiendo `trapz` sobre un refinamiento.

### 2.3 Cómo se elige

- **¿Tienes la función o solo las muestras?** Con función, cuadratura adaptativa
  (`quad`, `integral`). Con muestras, trapecio.
- **¿Los tiempos son uniformes?** Si no, trapecio con `dt` por intervalo: es la
  única regla de Newton–Cotes que sobrevive sin inventar datos.
- **¿Necesitas el valor en cada instante?** Acumulado (`cumulative_trapezoid`,
  `cumtrapz`), no la integral total.
- **¿Quieres más orden gratis?** Con muestras uniformes, Simpson 1/3 sube de
  $O(h^2)$ a $O(h^4)$ sin evaluar nada nuevo. Con $dt$ irregular, no aplica.

---

## 3 · Ecuaciones diferenciales de un paso

Euler, ecuación (25.2):

$$
y_{i+1} = y_i + f(x_i, y_i)\,h
$$

Heun: predictor (25.15) y corrector (25.16).

$$
y_{i+1}^{0} = y_i + f(x_i,y_i)\,h, \qquad
y_{i+1} = y_i + \frac{f(x_i,y_i) + f(x_{i+1}, y_{i+1}^{0})}{2}\,h
$$

Punto medio, ecuación (25.27), con (25.25) para el medio paso.

$$
y_{i+1} = y_i + f\!\left(x_{i+1/2},\, y_{i+1/2}\right) h
$$

RK4 clásico, ecuación (25.40):

$$
y_{i+1} = y_i + \frac{1}{6}\left(k_1 + 2k_2 + 2k_3 + k_4\right)h
$$

| Método | Ecuación | En Python | En MATLAB | Cuándo usarlo | Cuándo **no** |
|---|---|---|---|---|---|
| Euler | (25.2) | a mano en el lazo: `y += f(t, y) * h` | `y = y + f(t,y)*h` | Lazo de control a paso fijo, o para entender qué es un paso | Cualquier cosa que se vaya a reportar como resultado: error global $O(h)$ |
| Heun (predictor-corrector) | (25.15)–(25.16) | a mano; o `solve_ivp(method='RK23')` | `ode23` | Quieres $O(h^2)$ con dos evaluaciones | Sistema rígido: el paso se encoge hasta el absurdo |
| Punto medio | (25.25) y (25.27) | `solve_ivp(method='RK23')` | `ode23` | Una evaluación más que Euler y un orden más | Cuando ya vas a pagar cuatro evaluaciones: usa RK4 |
| RK4 clásico | (25.40) | `solve_ivp(method='RK45')` | `ode45` | Opción por defecto para sistemas **no rígidos** | Sistemas rígidos; integraciones muy largas (muchas evaluaciones) |
| Dormand–Prince (RK45 adaptativo) | — | `solve_ivp(f, [t0, tf], y0, method='RK45')` | `ode45` | Casi todo lo no rígido, con control de error | Rigidez; o cuando cada evaluación de `f` es carísima y necesitas menos |
| DOP853 | — | `method='DOP853'` | no hay equivalente exacto: `ode45` con tolerancia ajustada | Tolerancias muy ajustadas | Uso general: cuesta más por paso |
| `odeint` (LSODA) | — | `scipy.integrate.odeint(f, y0, t)` | `ode15s` / `ode45` automático | Código viejo que ya lo usa; resuelve rígido y no rígido | Código nuevo: `solve_ivp` es la interfaz recomendada |

**Cómo se llaman en Python:**

```python
from scipy.integrate import solve_ivp, odeint

sol = solve_ivp(f, [0.0, 10.0], [y0], method="RK45", t_eval=t, rtol=1e-6)
sol.t, sol.y, sol.nfev, sol.status    # nfev = evaluaciones de f; status 0 = terminó bien

odeint(f, y0, t)                      # interfaz antigua, usa LSODA por dentro
```

**Cómo se llaman en MATLAB:**

```matlab
opciones = odeset('RelTol', 1e-6, 'Stats', 'on');
[t, y] = ode45(@(t, y) f(t, y), [0 10], y0, opciones);
sol = ode45(...);  sol.stats.nfev     % evaluaciones de f
```

---

## 4 · EDO multipaso y rigidez

Adams–Bashforth de 4º orden (predictor), ecuación (26.44):

$$
y_{i+1}^{0} = y_i + h\left(\frac{55}{24}f_i - \frac{59}{24}f_{i-1} + \frac{37}{24}f_{i-2} - \frac{9}{24}f_{i-3}\right)
$$

Adams–Moulton de 4º orden (corrector), ecuación (26.45):

$$
y_{i+1}^{j} = y_i + h\left(\frac{9}{24}f_{i+1}^{j-1} + \frac{19}{24}f_i - \frac{5}{24}f_{i-1} + \frac{1}{24}f_{i-2}\right)
$$

| Método | Ecuación | En Python | En MATLAB | Cuándo usarlo | Cuándo **no** |
|---|---|---|---|---|---|
| Adams–Bashforth 4 | (26.44) | no hay función suelta: se programa | igual | Cada evaluación de `f` es carísima: reutiliza cuatro pendientes ya calculadas | Al arrancar: necesita cuatro puntos previos de un método de un paso |
| Adams–Moulton 4 | (26.45) | se programa | igual | Como corrector del predictor anterior | Solo: es implícito y hay que iterarlo |
| Predictor–corrector con $\varepsilon$ | (26.46)–(26.47) | se programa | igual | Quieres controlar cuántas iteraciones del corrector haces | Implementación rápida: `ode113` ya lo hace |
| Milne–Simpson | (26.42)–(26.43) | se programa | igual | Como ejercicio de comparación: mismo orden, otra familia | Producción: los modificadores son delicados |
| Adams variable (`ode113`) | — | `solve_ivp(method='LSODA')` o a mano | `ode113` | Trayectorias largas y suaves, tolerancias exigentes | Sistemas rígidos: el paso se hunde |
| BDF | — | `solve_ivp(method='BDF')` | `ode15s` | **Sistemas rígidos**: varias constantes de tiempo muy distintas | Sistemas no rígidos de corta duración: más caro que RK45 |
| Radau (implícito, 5º orden) | — | `solve_ivp(method='Radau')` | `ode23s`, `ode23tb` | Rigidez fuerte con tolerancias ajustadas | Integraciones cortas y suaves |
| LSODA (cambia de método solo) | — | `solve_ivp(method='LSODA')` | `ode15s` automático | No sabes si es rígido y no quieres averiguarlo | Cuando quieres control explícito del método que se usa |

### 4.1 Cómo se diagnostica la rigidez

Un sistema es rígido cuando sus escalas de tiempo están muy separadas: el
cociente entre el eigenvalor más grande y el más pequeño de $\partial f/\partial y$
es enorme. En la práctica se detecta por el **síntoma**, no por el cálculo:

| Síntoma | Qué significa | Qué hacer |
|---|---|---|
| `nfev` altísimo sobre una curva que se ve suave | El paso explícito está limitado por estabilidad, no por precisión | Cambiar a un método implícito |
| El paso se encoge hasta casi cero en un tramo corto | Ahí hay una constante de tiempo rápida | `BDF`, `Radau`, `LSODA` |
| `status != 0` ("step size too small") | El integrador explícito no puede avanzar | Igual que arriba |
| RK45 tarda segundos donde BDF tarda milisegundos | Rigidez confirmada | Reportar el `nfev` de ambos como evidencia |

```python
sol45 = solve_ivp(f, [0, 1], y0, method="RK45")
solbdf = solve_ivp(f, [0, 1], y0, method="BDF")
print(sol45.nfev, solbdf.nfev)     # si difieren en órdenes de magnitud: es rígido
```

```matlab
s45 = ode45(@f, [0 1], y0, odeset('Stats', 'on'));
s15 = ode15s(@f, [0 1], y0, odeset('Stats', 'on'));
s45.stats.nfev, s15.stats.nfev
```

---

## 5 · Tabla de decisión rápida

| Si el problema es… | Usa | Porque |
|---|---|---|
| Derivar una señal con ruido | media móvil o `savgol_filter`, **después** centrada | El ruido se amplifica como $1/h$ |
| Derivar dentro de un microcontrolador | diferencia hacia atrás | Es la única causal y cuesta una resta |
| Integrar muestras con `dt` irregular | trapecio con `dt` por intervalo | Newton–Cotes necesita `dt` uniforme |
| Integrar muestras uniformes y quieres precisión | Simpson 1/3 | Sube a $O(h^4)$ gratis |
| Integrar una función conocida | `quad` / `integral` | Control de error adaptativo |
| Simular un lazo de control a paso fijo | Euler | Es lo que corre en el microcontrolador |
| Resolver una EDO no rígida | `RK45` / `ode45` | Buen equilibrio orden/costo |
| Evaluar `f` es carísimo | multipaso (`ode113`) | Reutiliza pendientes ya calculadas |
| El `nfev` explota o el paso se hunde | `BDF` / `ode15s` / `LSODA` | Implícitos: no los limita la estabilidad |
| No sé si es rígido | `LSODA` | Cambia solo entre explícito e implícito |
| Necesito la solución en instantes exactos | `t_eval=` / `odeset('Refine')` | Evita interpolar a mano |

---

## 6 · Errores que cuestan puntos

1. **Refinar $h$ sin mirar el ruido.** El error total tiene un mínimo; pasarse
   de fino empeora.
2. **Usar Simpson con número impar de intervalos**, o con `dt` irregular.
3. **Confundir error local con global.** Euler es $O(h^2)$ por paso y $O(h)$
   acumulado; en la gráfica se ve la diferencia.
4. **Reportar el resultado de Euler como si fuera el del solver.** Son métodos
   distintos con errores distintos; el integrador del cuaderno 03 lo distingue.
5. **Elegir el método por costumbre.** `ode45` no es "el de MATLAB": es el de
   sistemas no rígidos. En un motor eléctrico suele ganar `ode15s`.
6. **No reportar `nfev`.** Es la evidencia objetiva de que el método elegido era
   el adecuado; sin ese número, la elección es una opinión.

---

## 7 · Fuente

Libro *Métodos numéricos para ingenieros*, 7ª edición: capítulo 6 (temas 21–24,
diferenciación e integración) y capítulo 7 (temas 25–28, ecuaciones
diferenciales ordinarias). Las filas marcadas "extensión del curso" no tienen
ecuación en el libro: son las reglas que se usan en un lazo de tiempo real y que
el cuaderno 02 programa a mano a propósito.
