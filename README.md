# U5: Derivadas, integrales y EDO

Unidad compacta de Métodos Numéricos que reúne diferenciación e integración
numéricas con ecuaciones diferenciales ordinarias. El enfoque es aprender a
seleccionar y utilizar funciones de NumPy, SciPy y MATLAB, interpretar sus
entradas y salidas y justificar los métodos en problemas de ingeniería.

## Cuadernos

| Cuaderno | Contenido |
|---|---|
| `notebooks/U5_01_Derivacion_Numerica.ipynb` | 5.1 Derivación numérica |
| `notebooks/U5_02_Integracion_Numerica.ipynb` | 5.2 Trapecio y Simpson; 5.3 intervalos desiguales |
| `notebooks/U5_03_EDO_Un_Paso.ipynb` | 6.1 Fundamentos; 6.2 métodos de un paso |
| `notebooks/U5_04_EDO_Multipaso.ipynb` | 6.3 Métodos de pasos múltiples |

Cada cuaderno organiza teoría, uso de bibliotecas, laboratorio, preguntas y
caso de ingeniería. Las implementaciones de `lib/` son material de consulta
para explicar los algoritmos; no se pide programarlos desde cero.

## Empezar

- **VS Code o Codespaces:** abre este repositorio y ejecuta el cuaderno desde
  `notebooks/`.
- **Google Colab:** abre el cuaderno desde GitHub. Si necesitas modificar
  archivos del proyecto, trabaja en una copia de Drive o en un Codespace.
- Instala las dependencias con `pip install -r requirements.txt`.

## Fuentes y figuras

La teoría sigue las partes 6 y 7 de *Métodos numéricos para ingenieros*,
7.ª edición: diferenciación (cap. 23), integración (cap. 21), introducción
a EDO, métodos de Runge-Kutta (cap. 25) y métodos multipaso (cap. 26).
Los cuadernos identifican las ecuaciones y figuras por su numeración impresa.

Las imágenes originales del libro no se redistribuyen en este repositorio.
Para una figura, consulta la edición del libro y el número indicado junto al
tema. Las imágenes didácticas propias del curso se alojarán en
`docs/figuras/`; sus enlaces GitHub raw tendrán la forma:

```text
https://raw.githubusercontent.com/ITH-MGL-MN/U5_derivadas_integrales_EDO/main/docs/figuras/<archivo>
```

La URL raw solo funcionará después de publicar el archivo en esa ruta de la
rama `main`.

## Proyecto final

Consulta [`proyecto_final.md`](proyecto_final.md): documenta un proyecto de
ingeniería propio, los métodos numéricos utilizados, sus algoritmos, argumentos
y resultados.

## Ramas

- `test`: desarrollo y validación de la unidad.
- `main`: versión pública del material y, cuando se integre el evaluador,
  únicamente el blob ofuscado destinado al alumnado.
