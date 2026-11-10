# Bitácora de IA

Para qué usamos IA en el proyecto, qué aceptamos, qué rechazamos o corregimos y cómo lo verificamos. La regla del grupo fue: **nada entra al repo sin que lo corramos y lo entendamos**, y cualquier número que aparece en una conclusión sale de una celda ejecutada.

---

## José Ignacio Paccagnella · notebooks 01, 02 y 05

**Herramienta:** Claude (Claude Code, dentro de VS Code). Lo usé como asistente de programación: escribía código y texto que yo revisaba, corría y aceptaba o corregía.

### Para qué la usé

| Parte | Qué le pedí | Qué hice yo |
|---|---|---|
| Estructura | Proponer la estructura del repo (`src/` compartido, un notebook por parte, `outputs/` con `appid` como llave) y el README | Revisé la propuesta y dividí el trabajo del grupo sobre esa estructura |
| 01 · Datos | Código de descarga y limpieza (`src/datos.py`) y exploración | Revisé la limpieza y los hallazgos; el corte de > 80 % positivo viene de nuestra propuesta |
| 02 · Clasificación | Pipeline, validación cruzada, umbral por costos, importancia por permutación y el análisis de dónde falla | Elegí los costos con el grupo y revisé que el examen se usara una sola vez |
| 05 · Decisión | Puntaje, mochila con programación dinámica y comparación con el método codicioso | Definí la decisión (Q300, máximo 5 juegos) y revisé cada conclusión contra las tablas |

### Lo que aceptamos, y cómo lo verificamos

| # | Sugerencia de la IA | Cómo se verificó |
|---|---|---|
| 1 | Usar `games.csv` y no el parquet de Hugging Face, y leer el CSV con nombres de columna explícitos | Al explorar, el parquet traía las etiquetas vacías y el encabezado del CSV estaba corrido una columna (`"DiscountDLC count"`). Se comprobó que después de corregirlo los precios y las reseñas tienen valores razonables (notebook 01). |
| 2 | Una lista de columnas prohibidas (`COLUMNAS_PROHIBIDAS`) y un `assert` en `construir_X` | Evita la fuga de datos: reseñas, owners, playtime y metacritic salen de lo mismo que queremos predecir. Si alguien agrega una de esas columnas, el notebook se detiene. |
| 3 | Elegir el umbral con predicciones fuera de fold (`cross_val_predict`), no con el examen | El examen se usó una sola vez, al final. La diferencia entre CV (0.80) y examen (0.81) es chica. |
| 4 | Costos de 1 (comprar un malo) y 0.5 (perderse un bueno) | Lo aceptamos con una justificación propia (en una oferta grande hay muchos sustitutos buenos) y agregamos un análisis de sensibilidad: con otros costos el umbral va de 0.33 a 0.79 (notebook 02). |
| 5 | Resolver la lista de compra como problema de la mochila | La función se comparó contra la fuerza bruta en 300 casos al azar, sin ninguna diferencia. |

### Lo que rechazamos o corregimos

| # | Qué pasó | Qué hicimos |
|---|---|---|
| 1 | La IA dio por hecho que había que entregar un **informe** y lo puso en el README y en la división del trabajo | El enunciado no lo pide. Le preguntamos de dónde lo había sacado, admitió que fue una suposición suya y lo quitamos. |
| 2 | La primera **lista de "evitar"** usaba solo el modelo. Otra revisión con IA nos avisó que 3 de los 5 juegos tenían buenas reseñas reales (Dreamscaper 88 %, SWORN 83 %) | Lo comprobamos con los datos: era cierto. Cambiamos la regla a **"el modelo propone, las reseñas reales confirman"**, en la lista de compra y en la de evitar. Esa misma revisión traía un dato al revés ("deja pasar el 58 % de los buenos", cuando en realidad *detecta* el 58 %), y no lo usamos. |
| 3 | Una conclusión del notebook 05 decía que *PERISH* quedaba fuera por su calidad predicha | Al volver a correr el notebook vimos que en realidad sí pasaba el umbral (0.72). La conclusión se corrigió: queda fuera por sus reseñas reales (72 %). |
| 4 | La conclusión decía que la mochila le ganaba al codicioso con Q300 | Después del cambio de la regla, con Q300 empatan. Probamos otros presupuestos, vimos que con Q50 a Q200 la mochila gana por mucho (con Q200, 2.75 contra 1.68) y cambiamos la tabla y la conclusión. |
| 5 | En el análisis de dónde falla el modelo, el primer borrador decía que la precision se mantenía "en 0.80 a 0.81" en los grupos con bajo recall | No era cierto para Early Access (0.775) ni para los gratis (0.787). Se reescribió para hablar solo de los grupos donde sí se cumple. |

### Lo que aprendí

- La IA escribe rápido código que corre, pero **que corra no quiere decir que la conclusión sea cierta**. Los errores que encontramos (2 a 5) no eran de código: eran conclusiones que no coincidían con los números o con la realidad.
- Lo que más sirvió fue revisar los resultados contra el dato real (las reseñas) y contra un método simple (fuerza bruta, método codicioso, modelo perezoso).

---

## Fabiola Deras Gutierrez · notebooks 03 y 04

_(pendiente: Fabi completa su parte con el mismo formato)_

### Para qué la usé

| Parte | Qué le pedí | Qué hice yo |
|---|---|---|
| | | |

### Lo que aceptamos, y cómo lo verificamos

| # | Sugerencia de la IA | Cómo se verificó |
|---|---|---|
| | | |

### Lo que rechazamos o corregimos

| # | Qué pasó | Qué hicimos |
|---|---|---|
| | | |
