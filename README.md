# ¿Qué juegos comprar en las ofertas de Steam con poco presupuesto?

Ciencia de Datos · Sección A · Proyecto Final
Fabiola Deras Gutierrez · José Ignacio Paccagnella · Juan David Contreras

**Decisión:** con un presupuesto fijo (Q300) en la oferta de invierno de Steam, qué juegos comprar y cuáles evitar.
La salida es una lista concreta: *"con Q300, compra estos 5"*.

---

## Estructura

```
Data_science_final/
├── README.md
├── requirements.txt
├── Propuesta_Proyecto_Final.pdf
├── src/                         # código compartido (lo importan todos los notebooks)
│   ├── config.py                # rutas, supuestos (presupuesto, tasa Q/USD, umbral 80 %...) y columnas prohibidas
│   ├── datos.py                 # descarga + limpieza -> data/processed/juegos.parquet
│   └── recomendador.py          # (Persona B) recomendar(favoritos, k)
├── notebooks/
│   ├── 01_datos.ipynb           # Persona A · limpieza y exploración
│   ├── 02_clasificacion.ipynb   # Persona A · ¿será bien recibido? + umbral por costos
│   ├── 03_recomendador_clusters.ipynb  # Persona B · similitud coseno + k-Means/PCA
│   ├── 04_causal.ipynb          # Persona C · ¿descuento grande = juego peor?
│   └── 05_decision.ipynb        # Persona C · lista de compra dentro del presupuesto
├── data/                        # NO se sube a git (se genera solo)
│   ├── raw/games.csv
│   └── processed/juegos.parquet
├── outputs/                     # resultados que pasan de un notebook a otro
│   ├── pred_calidad.csv         # A -> C
│   ├── clusters.csv             # B -> C
│   └── figuras/
└── informe/                     # documento final y presentación
```

## Cómo empezar

```bash
pip install -r requirements.txt
python -m src.datos        # descarga games.csv (~400 MB) y crea data/processed/juegos.parquet
```

En cualquier notebook:

```python
from src import config as C
from src.datos import cargar_juegos
df = cargar_juegos()       # 44,568 juegos con ≥ 20 reseñas
```

Los notebooks se abren desde la carpeta `notebooks/`; la primera celda ya agrega la raíz del repo al path.

## Cómo funciona

```
games.csv ──► src/datos.py ──► juegos.parquet ─┬─► 02 clasificación ──► pred_calidad.csv ─┐
                                               ├─► 03 recomendador  ──► recomendar()     ─┼─► 05 decisión ──► lista Q300
                                               └─► 04 causal (independiente)              │
                                                                                          ┘
```

1. **Datos (01).** Un solo dataset limpio para todos. Objetivo: `bien_recibido = pct_positivo > 0.80`.
2. **Calidad (02).** Clasificadores comparados contra el modelo perezoso con Pipeline + validación cruzada estratificada. Precision, recall y AUC; el examen se usa una vez. Umbral elegido por costos, no 0.5.
3. **Gustos (03).** Cada juego = vector de etiquetas/géneros; similitud coseno con los favoritos. k-Means + silhouette + PCA para familias de juegos.
4. **Causal (04).** ¿Descuento grande → peor juego? Antigüedad como confusor; comparación dentro de grupos de antigüedad.
5. **Decisión (05).** Puntaje = calidad predicha × parecido; se elige la mejor combinación dentro del presupuesto usando el precio en oferta.

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

| Persona | Parte | Entrega |
|---|---|---|
| A | 01 datos, 02 clasificación y umbral | `juegos.parquet`, `pred_calidad.csv` |
| B | 03 recomendador y clusters | `recomendar()`, `clusters.csv` |
| C | 04 causal, 05 decisión, integración del informe | lista final, informe |
