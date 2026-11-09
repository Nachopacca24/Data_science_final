"""Formato de entrada y salida de la API (el contrato está en web/CONTRATO_API.md).

La entrada es estricta: "300" (texto), true o 300.001 no se aceptan como presupuesto.
"""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, field_validator

from web.api import config

AppId = Annotated[StrictInt, Field(gt=0)]


class PeticionRecomendaciones(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # StrictFloat acepta 300 y 300.5, pero no "300" ni true.
    presupuesto: Annotated[StrictFloat, Field(gt=0, le=config.PRESUPUESTO_MAX, allow_inf_nan=False)]
    favoritos: Annotated[list[AppId], Field(min_length=1, max_length=config.MAX_FAVORITOS)]

    @field_validator("presupuesto")
    @classmethod
    def _maximo_dos_decimales(cls, v):
        if abs(v * 100 - round(v * 100)) > 1e-6:
            raise ValueError("admite como máximo 2 decimales (centavos)")
        return v

    @field_validator("favoritos")
    @classmethod
    def _sin_repetidos(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("no se pueden repetir juegos")
        return v


class Juego(BaseModel):
    appid: int
    nombre: str
    precio_gtq: float
    etiquetas: list[str]
    generos: list[str]
    p_bien_recibido: float
    pasa_umbral: bool
    pct_positivo: float
    imagen: str


class JuegoRecomendado(BaseModel):
    appid: int
    nombre: str
    precio_gtq: float
    p_bien_recibido: float
    similitud: float
    puntaje: float
    imagen: str


class RespuestaRecomendaciones(BaseModel):
    presupuesto: float
    juegos: list[JuegoRecomendado]
    total_gtq: float
    restante_gtq: float


class Salud(BaseModel):
    estado: str


class Version(BaseModel):
    version: str
    ambiente: str


class Detalle(BaseModel):
    campo: str
    problema: str


class Error(BaseModel):
    error: str
    mensaje: str
    detalles: list[Detalle] = []
