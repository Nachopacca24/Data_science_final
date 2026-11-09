# Contrato de la API · v1

Formato **oficial** de las peticiones y respuestas. Reemplaza al "contrato provisional" de `tests/integracion/CASOS.md`, que ya cumple: las 34 pruebas de integración pasan sin cambios.

- Todo es JSON en UTF-8. Los precios están en **quetzales** (precio en oferta = precio de lista × (1 − 50 %)).
- La documentación interactiva, generada del código, está en `GET /docs` (y el esquema en `GET /openapi.json`).
- Si algo de aquí cambia, se avisa al grupo y se cambian este archivo, `web/api/config.py` y las pruebas.

## Resumen

| Método y ruta | Para qué | Respuestas |
|---|---|---|
| `GET /salud` | ¿La API está viva? | `200` |
| `GET /version` | SHA y ambiente de la instancia | `200` |
| `GET /juegos?buscar=&limite=` | Buscar juegos por nombre | `200` · `422` |
| `GET /juegos/{appid}` | Detalle de un juego | `200` · `404` · `422` |
| `POST /recomendaciones` | La lista de compra | `200` · `422` |
| `GET /` | Pantalla de recomendaciones (HTML) | `200` |

## Límites

| Límite | Valor |
|---|---|
| `presupuesto` | número, `0 < presupuesto ≤ 10000`, máximo 2 decimales |
| `favoritos` | lista de 1 a 5 appids enteros > 0, sin repetidos, todos en el catálogo |
| juegos en la lista | máximo 5 |
| `limite` de búsqueda | de 1 a 1000 (por defecto 20) |
| `buscar` | máximo 100 caracteres |

---

## `GET /salud`

```json
{"estado": "ok"}
```

Si responde, el catálogo ya está cargado: la API no arranca con un catálogo dañado.

## `GET /version`

```json
{"version": "0a52f18", "ambiente": "dev"}
```

- `version`: SHA del commit del build. Sale de la variable `APP_VERSION` o del archivo `web/VERSION` (lo escribe el build). Sin ninguno de los dos, vale `"local"`.
- `ambiente`: `"dev"` o `"prod"`, de la variable `APP_AMBIENTE` (por defecto `"dev"`). Otro valor detiene el arranque.

## `GET /juegos`

Parámetros (query, opcionales): `buscar` (texto dentro del nombre, sin importar mayúsculas; vacío = todos) y `limite`.

Devuelve **una lista** de juegos en orden alfabético por nombre. Si no hay coincidencias, `[]`.

```json
[{"appid": 379720, "nombre": "DOOM", "...": "..."}, {"appid": 782330, "nombre": "DOOM Eternal", "...": "..."}]
```

## `GET /juegos/{appid}`

```json
{
  "appid": 379720,
  "nombre": "DOOM",
  "precio_gtq": 76.81,
  "etiquetas": ["FPS", "Gore", "Action", "Shooter", "..."],
  "generos": ["Action"],
  "p_bien_recibido": 0.9054,
  "pasa_umbral": true,
  "pct_positivo": 0.9552,
  "imagen": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/379720/header.jpg?t=1750784856"
}
```

| Campo | Significado |
|---|---|
| `precio_gtq` | precio en oferta; `0` = gratis |
| `p_bien_recibido` | probabilidad de que sea bien recibido según el modelo del notebook 02 (0 a 1) |
| `pasa_umbral` | `p_bien_recibido ≥ 0.66` (el umbral elegido por costos) |
| `pct_positivo` | % real de reseñas positivas (0 a 1) |

Errores: `404 no_encontrado` si el appid no está en el catálogo; `422 entrada_invalida` si no es un entero > 0.

## `POST /recomendaciones`

Petición:

```json
{"presupuesto": 300, "favoritos": [379720, 1145360]}
```

Respuesta `200` (DOOM y Hades, Q300):

```json
{
  "presupuesto": 300.0,
  "juegos": [
    {"appid": 782330, "nombre": "DOOM Eternal", "precio_gtq": 153.84, "p_bien_recibido": 0.8888, "similitud": 0.6999, "puntaje": 0.622, "imagen": "https://..."},
    {"appid": 248820, "nombre": "Risk of Rain (2013)", "precio_gtq": 38.3, "p_bien_recibido": 0.9492, "similitud": 0.5851, "puntaje": 0.5554, "imagen": "https://..."},
    {"appid": 220, "nombre": "Half-Life 2", "precio_gtq": 38.3, "...": "..."},
    {"appid": 219150, "nombre": "Hotline Miami", "precio_gtq": 38.3, "...": "..."},
    {"appid": 113200, "nombre": "The Binding of Isaac", "precio_gtq": 19.14, "...": "..."}
  ],
  "total_gtq": 287.88,
  "restante_gtq": 12.12
}
```

**Regla de negocio: un juego puede entrar a la lista si**

1. pasa el umbral de calidad (`pasa_umbral = true`),
2. es de pago (los gratis no se compran),
3. no es uno de los favoritos (el usuario ya lo tiene),
4. y cabe en lo que queda del presupuesto.

Entre los que pueden entrar se elige la combinación de **hasta 5** con más puntaje total (`puntaje = p_bien_recibido × similitud`), igual que el notebook 05. Si dos combinaciones empatan, gana la de más juegos y luego la más barata.

**Siempre se cumple:**

- `total_gtq ≤ presupuesto` y `restante_gtq = presupuesto − total_gtq` (se calcula en centavos: un juego que cuesta justo el presupuesto sí cabe).
- No hay juegos repetidos y la lista va de mayor a menor `puntaje`.
- Si no alcanza para ningún juego, la respuesta es `200` con `"juegos": []`.
- La misma petición da siempre la misma respuesta.

La entrada es **estricta**: `"300"` (texto), `true`, `300.001`, appids como texto o campos que no están en el contrato dan `422`.

## Errores

Todos los errores tienen el mismo formato:

```json
{
  "error": "entrada_invalida",
  "mensaje": "La petición no es válida.",
  "detalles": [
    {"campo": "presupuesto", "problema": "debe ser mayor que 0.0"},
    {"campo": "favoritos", "problema": "debe tener al menos 1 elemento(s)"}
  ]
}
```

| Estado | `error` | Cuándo |
|---|---|---|
| `422` | `entrada_invalida` | algún dato no cumple el contrato; `detalles` dice cuál y por qué |
| `404` | `no_encontrado` | el juego o la ruta no existen |
| `405` | `metodo_no_permitido` | p. ej. `GET /recomendaciones` |

`campo` es la ruta del dato: `presupuesto`, `favoritos`, `favoritos.1` (el segundo favorito), `appid`, `limite`, o `cuerpo` si el JSON no se puede leer.

## El catálogo

La API no usa el dataset completo: lee `web/catalogo_demo.csv`, con los **500 juegos con más reseñas en los que el modelo y las reseñas reales están de acuerdo** ("el modelo propone, las reseñas confirman", como en el notebook 05). Se regenera con `python -m web.construir_catalogo`. Los appids sirven como llave fija para las pruebas; por ejemplo DOOM `379720`, Hades `1145360`, DOOM Eternal `782330`.
