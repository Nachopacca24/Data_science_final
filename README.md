# ¿Qué juegos comprar en las ofertas de Steam con poco presupuesto?

Ciencia de Datos · Sección A · Proyecto Final
Fabiola Deras Gutierrez · José Ignacio Paccagnella · Juan David Contreras

**Decisión:** con un presupuesto fijo (Q300) en la oferta de invierno de Steam, qué juegos comprar y cuáles evitar.
La salida es una lista concreta: *"con Q300, compra estos 5"*.

---

## Resultado

Para un jugador al que le gustaron **DOOM** y **Hades**, con Q300 y un descuento supuesto de 50 %:

| Compra | Precio en oferta |
|---|---|
| DOOM Eternal | Q153.84 |
| Far Cry | Q38.38 |
| Risk of Rain (2013) | Q38.30 |
| DOOM + DOOM II | Q38.42 |
| Quake | Q15.36 |
| **Total** | **Q284.30** |

**Evitar:** Paranautical Activity, Rogue Girl, Dead Purge: Outbreak, I Shall Remain y Perseus: Titan Slayer. Se parecen mucho a sus gustos, pero el modelo predice que no serán bien recibidos y sus reseñas reales lo confirman (entre 45 % y 69 % positivas).

**El modelo propone, las reseñas reales confirman.** El modelo estima la calidad *sin leer reseñas*, así que sirve para juegos nuevos o con pocas reseñas. Cuando un juego ya tiene reseñas, se usan para confirmar: no se recomienda un juego con malas reseñas reales ni se manda a evitar uno con buenas.

Lo que encontró cada notebook:

| Notebook | Resultado principal |
|---|---|
| 01 · Datos | 44,568 juegos con ≥ 20 reseñas; 52.8 % son "bien recibidos" (> 80 % de reseñas positivas). |
| 02 · Clasificación | El boosting es el mejor modelo (AUC 0.81 en el examen, contra 0.50 del modelo perezoso). Con los costos del proyecto, el umbral es **0.66** y no 0.5. |
| 03 · Recomendador | La similitud coseno sobre etiquetas y géneros encuentra juegos parecidos a los favoritos. k-Means agrupa los juegos en 5 familias (el silhouette es bajo: las familias se traslapan). |
| 04 · Causal | Un descuento grande no indica en general un juego peor. Comparado con un descuento pequeño sí sale peor (5.8 puntos menos de % positivo dentro de grupos de antigüedad), pero no se puede decir que el descuento lo cause. |
| 05 · Decisión | Puntaje = calidad predicha × parecido. La mochila (programación dinámica) elige la mejor combinación dentro del presupuesto; con presupuestos chicos supera por mucho al método codicioso (con Q200: 2.75 contra 1.68). |

## Estructura

```
Data_science_final/
├── README.md
├── requirements.txt
├── Propuesta_Proyecto_Final.pdf
├── src/                         # código compartido (lo importan todos los notebooks)
│   ├── config.py                # rutas, supuestos (presupuesto, tasa Q/USD, umbral 80 %...) y columnas prohibidas
│   ├── datos.py                 # descarga + limpieza -> data/processed/juegos.parquet
│   ├── features.py              # construir_X(): predictores para el clasificador (sin columnas prohibidas)
│   ├── recomendador.py          # similitud(favoritos) y recomendar(favoritos, k)
│   └── decision.py              # puntaje, filtro de candidatos y mochila (elegir_optimo)
├── notebooks/
│   ├── 01_datos.ipynb           # limpieza y exploración
│   ├── 02_clasificacion.ipynb   # ¿será bien recibido? + umbral por costos
│   ├── 03_recomendador_clusters.ipynb  # similitud coseno + k-Means/PCA
│   ├── 04_causal.ipynb          # ¿descuento grande = juego peor?
│   └── 05_decision.ipynb        # lista de compra dentro del presupuesto
├── data/                        # NO se sube a git (se genera solo)
│   ├── raw/games.csv
│   └── processed/juegos.parquet
└── outputs/                     # resultados que pasan de un notebook a otro
    ├── pred_calidad.csv         # 02 -> 05: probabilidad de ser bien recibido por juego
    ├── umbral.json              # 02 -> 05: modelo y umbral elegidos
    ├── 02_resultados_cv.csv, 02_resultados_examen.csv
    ├── clusters.csv             # 03: familia de cada juego
    ├── lista_compra_q300.csv    # 05: la decisión final
    ├── lista_evitar.csv         # 05: juegos tentadores que conviene evitar
    └── figuras/                 # una figura por resultado, con el número del notebook
```

## Cómo correrlo

```bash
pip install -r requirements.txt
python -m src.datos        # descarga games.csv (~400 MB) y crea data/processed/juegos.parquet
```

Después se abren los notebooks en orden (01 → 05) desde la carpeta `notebooks/`; la primera celda ya agrega la raíz del repo al path. El 05 necesita las salidas del 02.

En cualquier notebook:

```python
from src import config as C
from src.datos import cargar_juegos
df = cargar_juegos()       # 44,568 juegos con ≥ 20 reseñas
```

## Cómo funciona

```
games.csv ──► src/datos.py ──► juegos.parquet ─┬─► 02 clasificación ──► pred_calidad.csv ─┐
                                               ├─► 03 recomendador  ──► similitud()      ─┼─► 05 decisión ──► lista Q300
                                               └─► 04 causal (independiente)              │
                                                                                          ┘
```

1. **Datos (01).** Un solo dataset limpio para todos. Objetivo: `bien_recibido = pct_positivo > 0.80`.
2. **Calidad (02).** Clasificadores comparados contra el modelo perezoso con Pipeline + validación cruzada estratificada. Precision, recall y AUC; el examen se usa una vez. Umbral elegido por costos: comprar un juego malo cuesta 1, perderse uno bueno cuesta 0.5.
3. **Gustos (03).** Cada juego = vector de etiquetas/géneros; similitud coseno con los favoritos. k-Means + silhouette + PCA para familias de juegos.
4. **Causal (04).** ¿Descuento grande → peor juego? Antigüedad como confusor; comparación dentro de grupos de antigüedad.
5. **Decisión (05).** Puntaje = calidad predicha × parecido; se elige la mejor combinación dentro del presupuesto (máximo 5 juegos) usando el precio en oferta. Las reseñas reales confirman lo que dice el modelo antes de recomendar o mandar a evitar un juego.

## Reglas del equipo

- **Supuestos solo en `src/config.py`.** Nadie escribe `300`, `0.8` o `7.7` a mano en un notebook.
- **No usar como predictores** las columnas de `C.COLUMNAS_PROHIBIDAS` (reseñas, recomendaciones, owners, playtime, metacritic): salen de lo mismo que queremos predecir.
- Semilla fija: `C.SEMILLA`.
- Lo que otro necesita va a `outputs/` con `appid` como llave.
- Cada quien trabaja en su notebook; commits pequeños y `git pull` antes de empezar.

## Notas sobre los datos

- Fuente: [FronkonGames/steam-games-dataset](https://huggingface.co/datasets/FronkonGames/steam-games-dataset) (MIT).
- Se usa `games.csv`: el parquet de Hugging Face trae las **etiquetas vacías**. El encabezado del CSV está corrido una columna (`"DiscountDLC count"`) y `datos.py` lo corrige.
- `Price` es el precio **con** el descuento del día de la foto; `precio_lista_usd` lo revierte.
- No hay historial de precios ni datos de la oferta de diciembre → **plan B**: precio en oferta = precio de lista × (1 − `DESCUENTO_TIPICO`).

## División

| Parte | Responsable |
|---|---|
| 01 datos, 02 clasificación y umbral | José Ignacio Paccagnella |
| 03 recomendador y clusters | Fabiola Deras Gutierrez |
| 04 causal | Fabiola Deras Gutierrez |
| 05 decisión | José Ignacio Paccagnella |
