"""Descarga y limpieza del Steam Games Dataset.

Uso desde la raíz del repo:
    python -m src.datos          # descarga (si falta) y genera data/processed/juegos.parquet

Uso desde un notebook:
    from src.datos import cargar_juegos
    df = cargar_juegos()
"""
import pandas as pd

from src import config as C

# El encabezado de games.csv trae "DiscountDLC count" pegado: hay 39 nombres para
# 40 columnas y todo queda corrido un lugar. Por eso se leen con estos nombres.
COLUMNAS_CSV = [
    "AppID", "Name", "Release date", "Estimated owners", "Peak CCU", "Required age",
    "Price", "Discount", "DLC count", "About the game", "Supported languages",
    "Full audio languages", "Reviews", "Header image", "Website", "Support url",
    "Support email", "Windows", "Mac", "Linux", "Metacritic score", "Metacritic url",
    "User score", "Positive", "Negative", "Score rank", "Achievements", "Recommendations",
    "Notes", "Average playtime forever", "Average playtime two weeks",
    "Median playtime forever", "Median playtime two weeks", "Developers", "Publishers",
    "Categories", "Genres", "Tags", "Screenshots", "Movies",
]

COLUMNAS_LISTA = {
    "Genres": "generos", "Tags": "etiquetas", "Categories": "categorias",
    "Developers": "desarrolladores", "Publishers": "publicadores",
}


def descargar(forzar: bool = False):
    """Descarga games.csv de Hugging Face a data/raw/ (unos 400 MB)."""
    if C.CSV_CRUDO.exists() and not forzar:
        return C.CSV_CRUDO
    from huggingface_hub import hf_hub_download
    C.DATA_RAW.mkdir(parents=True, exist_ok=True)
    hf_hub_download(C.HF_REPO, "games.csv", repo_type="dataset", local_dir=C.DATA_RAW)
    return C.CSV_CRUDO


def leer_crudo() -> pd.DataFrame:
    return pd.read_csv(C.CSV_CRUDO, header=None, skiprows=1, names=COLUMNAS_CSV,
                       index_col=False, low_memory=False)


def _a_lista(s: pd.Series) -> pd.Series:
    return s.fillna("").map(lambda x: [t.strip() for t in str(x).split(",") if t.strip()])


def limpiar(crudo: pd.DataFrame) -> pd.DataFrame:
    df = crudo.drop_duplicates("AppID").copy()

    out = pd.DataFrame({
        "appid": df["AppID"].astype(int),
        "nombre": df["Name"],
        "fecha": pd.to_datetime(df["Release date"], format="mixed", errors="coerce"),
        "precio_actual_usd": df["Price"].astype(float),
        "descuento_actual": df["Discount"].astype(float) / 100,
        "edad_requerida": df["Required age"],
        "dlc_count": df["DLC count"],
        "logros": df["Achievements"],
        "windows": df["Windows"].astype(bool),
        "mac": df["Mac"].astype(bool),
        "linux": df["Linux"].astype(bool),
        "n_idiomas": df["Supported languages"].fillna("[]").str.count("'") // 2,
        "imagen": df["Header image"],
        # --- columnas prohibidas como predictores (ver config.COLUMNAS_PROHIBIDAS) ---
        "positivas": df["Positive"],
        "negativas": df["Negative"],
        "recomendaciones": df["Recommendations"],
        "peak_ccu": df["Peak CCU"],
        "metacritic": df["Metacritic score"],
        "user_score": df["User score"],
        "playtime_promedio": df["Average playtime forever"],
        "playtime_mediana": df["Median playtime forever"],
    })
    owners = df["Estimated owners"].str.split(" - ", expand=True)
    out["owners_min"] = pd.to_numeric(owners[0], errors="coerce")
    out["owners_max"] = pd.to_numeric(owners[1], errors="coerce")

    for orig, nuevo in COLUMNAS_LISTA.items():
        out[nuevo] = _a_lista(df[orig])

    # Price es el precio con el descuento vigente el día de la foto -> recuperar precio de lista
    d = out["descuento_actual"].clip(upper=0.99)
    out["precio_lista_usd"] = (out["precio_actual_usd"] / (1 - d)).round(2)
    out["precio_lista_gtq"] = (out["precio_lista_usd"] * C.TASA_GTQ_USD).round(2)
    out["precio_oferta_gtq"] = (out["precio_lista_gtq"] * (1 - C.DESCUENTO_TIPICO)).round(2)
    out["es_gratis"] = out["precio_lista_usd"] == 0

    out["anio"] = out["fecha"].dt.year
    out["antiguedad_anios"] = (pd.Timestamp(C.FECHA_REFERENCIA) - out["fecha"]).dt.days / 365.25

    # Objetivo
    out["total_resenas"] = out["positivas"] + out["negativas"]
    out = out[out["total_resenas"] >= C.MIN_RESENAS].copy()
    out["pct_positivo"] = out["positivas"] / out["total_resenas"]
    out["bien_recibido"] = (out["pct_positivo"] > C.UMBRAL_BIEN_RECIBIDO).astype(int)

    return out.reset_index(drop=True)


def construir() -> pd.DataFrame:
    descargar()
    df = limpiar(leer_crudo())
    C.DATA_PROC.mkdir(parents=True, exist_ok=True)
    df.to_parquet(C.JUEGOS_LIMPIOS, index=False)
    return df


def cargar_juegos() -> pd.DataFrame:
    """Punto de entrada para todos: devuelve el dataset limpio (lo construye si no existe)."""
    if not C.JUEGOS_LIMPIOS.exists():
        return construir()
    return pd.read_parquet(C.JUEGOS_LIMPIOS)


if __name__ == "__main__":
    df = construir()
    print(f"{len(df):,} juegos -> {C.JUEGOS_LIMPIOS}")
    print(f"bien_recibido: {df['bien_recibido'].mean():.1%}")
