# Bitácora de IA

Para qué usamos IA en el proyecto, qué aceptamos, qué rechazamos o corregimos y cómo lo verificamos. La regla del grupo fue: **nada entra al repo sin que lo corramos y lo entendamos**, y cualquier número que aparece en una conclusión sale de una celda ejecutada.

---

## José Ignacio Paccagnella · notebooks 01, 02 y 05

**Herramienta:** Claude (Claude Code, dentro de VS Code).

### Cómo me ayudó

| Parte | Cómo me ayudó |
|---|---|
| Estructura | Ideas para organizar el repo y el README |
| 01 · Datos | Entender cómo venían los datos crudos, cómo revisarlos y qué problemas tenían antes de limpiarlos |
| 02 · Clasificación | Apoyo en partes técnicas del código: el Pipeline, la validación cruzada y el cálculo del umbral por costos |
| 05 · Decisión | Apoyo técnico con la mochila y revisar que las conclusiones coincidieran con las tablas |

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
| 1 | La primera **lista de "evitar"** usaba solo el modelo. Otra revisión con IA nos avisó que 3 de los 5 juegos tenían buenas reseñas reales (Dreamscaper 88 %, SWORN 83 %) | Lo comprobamos con los datos: era cierto. Cambiamos la regla a **"el modelo propone, las reseñas reales confirman"**, en la lista de compra y en la de evitar. Esa misma revisión traía un dato al revés ("deja pasar el 58 % de los buenos", cuando en realidad *detecta* el 58 %), y no lo usamos. |
| 2 | Una conclusión del notebook 05 decía que *PERISH* quedaba fuera por su calidad predicha | Al volver a correr el notebook vimos que en realidad sí pasaba el umbral (0.72). La conclusión se corrigió: queda fuera por sus reseñas reales (72 %). |
| 3 | La conclusión decía que la mochila le ganaba al codicioso con Q300 | Después del cambio de la regla, con Q300 empatan. Probamos otros presupuestos, vimos que con Q50 a Q200 la mochila gana por mucho (con Q200, 2.75 contra 1.68) y cambiamos la tabla y la conclusión. |
| 4 | En el análisis de dónde falla el modelo, el primer borrador decía que la precision se mantenía "en 0.80 a 0.81" en los grupos con bajo recall | No era cierto para Early Access (0.775) ni para los gratis (0.787). Se reescribió para hablar solo de los grupos donde sí se cumple. |

---

## Fabiola Deras Gutierrez · notebooks 03 y 04

**Herramienta:** Claude (Claude Web).

### Cómo me ayudó

| Parte | Cómo me ayudó |
|---|---|
| 03 · Recomendador | Apoyo con dudas respecto a estructura y código creado por compañeros, además de preguntas respecto a MultiLabelBinarizer y el mejor enfoque para esa parte. Además de pruebas con las etiquetas para comprender mejor su impacto. |
| 03 · Familias | Aclaración de dudas y explicación sobre el susceso con la revisión de las 5 familias. |
| 04 · Causal | Explorar el descuento y la antigüedad, comprendelos mejor para tomar el mejor enfoque con la antigüedad que generaba dudas. |
| Revisión | Dos revisiones independientes del 03, 04 y 05 en concordancia numérica y alerta de errores |

### Lo que aceptamos, y cómo lo verificamos

| # | Sugerencia de la IA | Cómo se verificó |
|---|---|---|
| 1 | Reutilizar la función de Ignacio que arma columnas de 0 y 1 en vez de MultiLabelBinarizer | Así hay una sola forma de armar la matriz y no usamos algo que no vimos en clase. Se comprobó que con DOOM recomienda DOOM Eternal, Painkiller y Quake. |
| 2 | Ignorar las etiquetas que aparecen en menos de 50 juegos | Probamos también con 300: las recomendaciones casi no cambian, pero quedaban 30 juegos sin ninguna etiqueta. Nos quedamos con 50. |
| 3 | Elegir 5 familias aunque el silhouette más alto era con 11 | Casi empatan (0.145 contra 0.147). La revisión comprobó que con 5 salen casi las mismas familias con otras semillas, y con 11 no. Además, con 5 se pueden nombrar. |
| 4 | Tratar la antigüedad como confusor y comparar dentro de grupos de antigüedad | Se confirmó que la antigüedad se relaciona con el descuento (de 27 % a 40.7 %) y con el % positivo (de 85.1 % a 72.6 %). La revisión recalculó todo con otros cortes y la conclusión no cambió. |
| 5 | Ponerle nombre appid al índice que devuelve similitud | Sin eso, unirla con la tabla del 05 daba error. Se probó la unión con las predicciones del 02. |

### Lo que rechazamos o corregimos

| # | Qué pasó | Qué hicimos |
|---|---|---|
| 1 | El primer borrador decía que PCA mejoraba los grupos, porque el silhouette subía de 0.04 a 0.14 | La revisión mostró que con las columnas barajadas, sin ninguna relación entre etiquetas, también sube a 0.10. Lo cambiamos: PCA resume la matriz pero no mejora los grupos, y agregamos esos dos controles al notebook. |
| 2 | La conclusión decía que con favoritos muy distintos se recomienda "lo que queda en medio" | Con Stardew Valley y Hollow Knight casi todo se parecía a Hollow Knight. Se corrigió: el promedio puede quedar dominado por un favorito. |
| 3 | El plan decía que los juegos viejos tienden a ser mejores | Los datos muestran lo contrario en promedio por juego. Esto llevó a la correción en el notebook 02. |
| 4 | Una versión del 04 llamaba confusor a la popularidad | Las reseñas y los dueños vienen después del descuento y de la calidad, así que separar por ellos puede inventar relaciones. Lo dejamos como algo que no se separa a propósito. |