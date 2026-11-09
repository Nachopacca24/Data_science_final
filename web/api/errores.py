"""Todas las respuestas de error tienen el mismo formato:

    {"error": "<código>", "mensaje": "<para personas>", "detalles": [{"campo": ..., "problema": ...}]}
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

ENTRADA_INVALIDA = "La petición no es válida."

# Mensajes de pydantic traducidos. Si llega un tipo que no está aquí, se deja el original.
PROBLEMAS = {
    "missing": "falta este campo",
    "extra_forbidden": "este campo no existe en el contrato",
    "float_type": "debe ser un número",
    "int_type": "debe ser un número entero",
    "int_parsing": "debe ser un número entero",
    "int_from_float": "debe ser un número entero",
    "list_type": "debe ser una lista",
    "string_too_long": "admite como máximo {max_length} caracteres",
    "greater_than": "debe ser mayor que {gt}",
    "greater_than_equal": "debe ser mayor o igual que {ge}",
    "less_than_equal": "debe ser menor o igual que {le}",
    "too_short": "debe tener al menos {min_length} elemento(s)",
    "too_long": "admite como máximo {max_length} elemento(s)",
    "finite_number": "debe ser un número finito",
    "json_invalid": "el cuerpo no es un JSON válido",
    "model_attributes_type": "el cuerpo debe ser un objeto JSON",
}


class ErrorAPI(Exception):
    def __init__(self, estado: int, error: str, mensaje: str, detalles: list[dict] | None = None):
        super().__init__(mensaje)
        self.estado = estado
        self.cuerpo = {"error": error, "mensaje": mensaje, "detalles": detalles or []}


def entrada_invalida(detalles: list[dict]) -> ErrorAPI:
    return ErrorAPI(422, "entrada_invalida", ENTRADA_INVALIDA, detalles)


def detalle(err: dict) -> dict:
    """Convierte un error de pydantic en {"campo", "problema"}."""
    origen, *ruta = err["loc"]
    if err["type"] == "json_invalid" or not ruta:
        campo = "cuerpo" if origen == "body" else str(origen)
    else:
        campo = ".".join(str(x) for x in ruta)
    plantilla = PROBLEMAS.get(err["type"])
    problema = plantilla.format(**err.get("ctx", {})) if plantilla else err["msg"].removeprefix("Value error, ")
    return {"campo": campo, "problema": problema}


def registrar(app: FastAPI) -> None:
    @app.exception_handler(ErrorAPI)
    async def _error_api(_req: Request, e: ErrorAPI):
        return JSONResponse(e.cuerpo, status_code=e.estado)

    @app.exception_handler(RequestValidationError)
    async def _validacion(_req: Request, e: RequestValidationError):
        return JSONResponse(entrada_invalida([detalle(err) for err in e.errors()]).cuerpo, status_code=422)

    @app.exception_handler(StarletteHTTPException)
    async def _http(_req: Request, e: StarletteHTTPException):
        codigo, mensaje = {
            404: ("no_encontrado", "La ruta no existe."),
            405: ("metodo_no_permitido", "Método HTTP no permitido en esta ruta."),
        }.get(e.status_code, ("error_http", str(e.detail)))
        return JSONResponse({"error": codigo, "mensaje": mensaje, "detalles": []}, status_code=e.status_code)
