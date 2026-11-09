"""Constantes compartidas por todo el proyecto. Si se cambia algo aquí, avisar al grupo."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DATA_RAW = RAIZ / "data" / "raw"
DATA_PROC = RAIZ / "data" / "processed"
OUTPUTS = RAIZ / "outputs"
FIGURAS = OUTPUTS / "figuras"

CSV_CRUDO = DATA_RAW / "games.csv"
JUEGOS_LIMPIOS = DATA_PROC / "juegos.parquet"

HF_REPO = "FronkonGames/steam-games-dataset"

# --- Supuestos del proyecto ---
MIN_RESENAS = 20            # menos reseñas = el % positivo no es confiable
UMBRAL_BIEN_RECIBIDO = 0.80  # objetivo: > 80 % de reseñas positivas
TASA_GTQ_USD = 7.70          # quetzales por dólar (supuesto fijo)
DESCUENTO_TIPICO = 0.50      # plan B: descuento supuesto en la oferta de invierno
PRESUPUESTO_GTQ = 300
MAX_JUEGOS_LISTA = 5         # nadie juega 40 juegos: la lista final tiene como máximo 5
N_CANDIDATOS = 300           # solo se consideran los juegos más parecidos a los favoritos
FAVORITOS_EJEMPLO = [379720, 1145360]  # DOOM y Hades: el jugador de ejemplo del notebook 05
FECHA_REFERENCIA = "2026-11-08"  # fecha de la foto del dataset, para calcular antigüedad
SEMILLA = 42

# Costos para elegir el umbral del clasificador (unidades relativas).
# Comprar un juego malo = perder el dinero completo. Perderse uno bueno duele menos:
# en una oferta grande hay muchos sustitutos buenos.
COSTO_COMPRAR_MALO = 1.0   # falso positivo
COSTO_PERDER_BUENO = 0.5   # falso negativo

# Recomendador y clusters (notebook 03)
MIN_JUEGOS_ETIQUETA = 50     # etiquetas que aparecen en menos juegos se ignoran (ruido)
K_CLUSTERS = range(3, 13)    # valores de k que se prueban en k-Means
MUESTRA_SILHOUETTE = 10_000  # silhouette con todos los juegos tarda mucho
N_COMPONENTES_PCA = 10       # k-Means se corre sobre estos ejes de PCA, no sobre las 0/1
K_FAMILIAS = 5               # silhouette casi plano entre k=3 y 12; 5 empata con el mejor y se puede nombrar

# Columnas que NO pueden usarse como predictores de calidad (fuga de datos:
# salen de las reseñas o de la popularidad, que es lo que queremos predecir).
COLUMNAS_PROHIBIDAS = [
    "positivas", "negativas", "total_resenas", "pct_positivo", "bien_recibido",
    "recomendaciones", "owners_min", "owners_max", "peak_ccu",
    "metacritic", "user_score", "playtime_promedio", "playtime_mediana",
]
