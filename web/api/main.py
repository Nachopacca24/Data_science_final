"""API del recomendador de juegos en oferta. Contrato: web/CONTRATO_API.md

Correr desde la raíz del repo:
    uvicorn web.api.main:app --reload
Pantalla: http://localhost:8000/   ·   Documentación interactiva: http://localhost:8000/docs
"""
from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import FastAPI, Path, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from web.api import config, errores, recomendador
from web.api import esquemas as E
from web.api.catalogo import Juego, catalogo


@asynccontextmanager
async def arranque(_app: FastAPI):
    # Si el catálogo o el ambiente están mal, la API no arranca (mejor que fallar en cada petición).
    catalogo()
    config.ambiente()
    yield


app = FastAPI(title="Recomendador de juegos en oferta", version=config.version(), lifespan=arranque)
app.mount("/estaticos", StaticFiles(directory=config.ESTATICOS), name="estaticos")
errores.registrar(app)

ERROR = {"model": E.Error}


# ---------- sistema ----------

@app.get("/salud", response_model=E.Salud, tags=["sistema"])
def salud():
    """¿La API está viva? Si respondió, el catálogo ya está cargado."""
    return {"estado": "ok"}


@app.get("/version", response_model=E.Version, tags=["sistema"])
def version():
    """SHA del build y ambiente (dev o prod) de esta instancia."""
    return {"version": config.version(), "ambiente": config.ambiente()}


# ---------- juegos ----------

def _juego(j: Juego) -> dict:
    return asdict(j) | {"etiquetas": list(j.etiquetas), "generos": list(j.generos)}


@app.get("/juegos", response_model=list[E.Juego], responses={422: ERROR}, tags=["juegos"])
def buscar_juegos(
    buscar: str = Query("", max_length=100, description="Texto dentro del nombre (sin importar mayúsculas)"),
    limite: int = Query(config.LIMITE_BUSQUEDA_DEFECTO, ge=1, le=config.LIMITE_BUSQUEDA_MAX),
):
    """Juegos del catálogo cuyo nombre contiene `buscar`, en orden alfabético."""
    texto = buscar.strip().casefold()
    hallados = sorted((j for j in catalogo().values() if texto in j.nombre.casefold()),
                      key=lambda j: (j.nombre.casefold(), j.appid))
    return [_juego(j) for j in hallados[:limite]]


@app.get("/juegos/{appid}", response_model=E.Juego, responses={404: ERROR, 422: ERROR}, tags=["juegos"])
def detalle_juego(appid: int = Path(gt=0)):
    if (j := catalogo().get(appid)) is None:
        raise errores.ErrorAPI(404, "no_encontrado", f"El juego {appid} no está en el catálogo.")
    return _juego(j)


# ---------- recomendaciones ----------

@app.post("/recomendaciones", response_model=E.RespuestaRecomendaciones, responses={422: ERROR},
          tags=["recomendaciones"])
def recomendaciones(peticion: E.PeticionRecomendaciones):
    """Hasta 5 juegos que conviene comprar con el presupuesto, según los favoritos."""
    cat = catalogo()
    faltan = [{"campo": f"favoritos.{i}", "problema": f"el juego {a} no está en el catálogo"}
              for i, a in enumerate(peticion.favoritos) if a not in cat]
    if faltan:
        raise errores.entrada_invalida(faltan)

    presupuesto = round(peticion.presupuesto * 100)  # en centavos: sin errores de redondeo
    favoritos = [cat[a] for a in peticion.favoritos]
    elegidos = recomendador.elegir(recomendador.candidatos(cat, favoritos), presupuesto, config.MAX_JUEGOS_LISTA)
    total = sum(c.juego.precio_centavos for c in elegidos)

    return {
        "presupuesto": presupuesto / 100,
        "juegos": [{
            "appid": c.juego.appid, "nombre": c.juego.nombre, "precio_gtq": c.juego.precio_gtq,
            "p_bien_recibido": c.juego.p_bien_recibido, "similitud": round(c.similitud, 4),
            "puntaje": round(c.puntaje, 4), "imagen": c.juego.imagen,
        } for c in elegidos],
        "total_gtq": total / 100,
        "restante_gtq": (presupuesto + total) / 100,
    }


# ---------- pantallas ----------

@app.get("/", include_in_schema=False)
def pantalla_recomendaciones():
    return FileResponse(config.ESTATICOS / "recomendaciones.html")
