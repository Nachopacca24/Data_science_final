# Pruebas de integración: diseño de casos

Pruebas de **caja negra** contra la API en ejecución: solo se mandan peticiones HTTP y se revisan las respuestas, sin mirar el código.
Herramienta: `pytest` + `requests`. La URL de la instancia se toma de la variable de entorno `API_URL`.

> ⚠️ **Contrato provisional.** Las rutas, los campos y los límites de abajo son una propuesta mientras D publica el formato oficial de la API. Cuando salga, se ajustan aquí y en `conftest.py`.

## Contrato supuesto

| Endpoint | Respuesta esperada |
|---|---|
| `GET /salud` | `200 {"estado": "ok"}` |
| `GET /version` | `200 {"version": "<sha>", "ambiente": "dev" \| "prod"}` |
| `GET /juegos/{appid}` | `200 {appid, nombre, precio_gtq, etiquetas, p_bien_recibido, pasa_umbral}` · `404` si no existe · `422` si no es un entero positivo |
| `POST /recomendaciones` | body `{"presupuesto": número, "favoritos": [appid, ...]}` → `200 {"juegos": [{appid, nombre, precio_gtq, puntaje}], "total_gtq", "restante_gtq"}` · `422` si la entrada no es válida |

**Reglas de entrada (a confirmar con D y C):**
- `presupuesto`: número con `0 < presupuesto ≤ PRESUPUESTO_MAX` (propuesta: Q10,000).
- `favoritos`: lista de `1` a `MAX_FAVORITOS` appids (propuesta: 5), todos existentes en el catálogo.

**Regla de negocio:** un juego entra a la lista si **pasa el umbral de calidad**, **cabe en el presupuesto** y **no es uno de los favoritos** (el usuario ya lo tiene).

---

## 1. Partición de equivalencia

| ID | Entrada | Clase | Esperado |
|---|---|---|---|
| PE-01 | presupuesto = 300 | válida | 200 |
| PE-02 | presupuesto = -50 | inválida: negativo | 422 |
| PE-03 | presupuesto = 0 | inválida: cero | 422 |
| PE-04 | presupuesto = "trescientos" | inválida: no numérico | 422 |
| PE-05 | presupuesto ausente | inválida: falta el campo | 422 |
| PE-06 | presupuesto = null | inválida: nulo | 422 |
| PE-07 | favoritos = [appid existente] | válida | 200 |
| PE-08 | favoritos = [] | inválida: lista vacía | 422 |
| PE-09 | favoritos = [appid inexistente] | inválida: juego que no existe | 422 |
| PE-10 | favoritos = ["abc"] | inválida: appid no numérico | 422 |
| PE-11 | favoritos ausente | inválida: falta el campo | 422 |
| PE-12 | `GET /juegos/{appid existente}` | válida | 200 con el mismo appid |
| PE-13 | `GET /juegos/{appid inexistente}` | inválida: no existe | 404 |
| PE-14 | `GET /juegos/abc` | inválida: no numérico | 422 |

## 2. Valores límite

Se prueban los dos lados de cada límite.

| ID | Límite | Valor | Esperado |
|---|---|---|---|
| VL-01 | presupuesto mínimo (> 0) | 0 | 422 |
| VL-02 | presupuesto mínimo | 0.01 | 200 (lista vacía: no alcanza para nada) |
| VL-03 | presupuesto máximo | PRESUPUESTO_MAX | 200 |
| VL-04 | presupuesto máximo | PRESUPUESTO_MAX + 0.01 | 422 |
| VL-05 | favoritos mínimo (≥ 1) | 0 favoritos | 422 |
| VL-06 | favoritos mínimo | 1 favorito | 200 |
| VL-07 | favoritos máximo | MAX_FAVORITOS | 200 |
| VL-08 | favoritos máximo | MAX_FAVORITOS + 1 | 422 |
| VL-09 | juego cabe justo | presupuesto = precio del juego más barato que pasa el umbral | 200, ese juego aparece |
| VL-10 | juego no cabe por un centavo | presupuesto = ese precio − 0.01 | 200, ese juego no aparece |

## 3. Tabla de decisión: ¿el juego entra a la lista?

| Regla | C1: pasa umbral | C2: cabe en presupuesto | C3: es favorito | Acción |
|---|---|---|---|---|
| TD-R1 | No | – | – | No entra |
| TD-R2 | Sí | No | – | No entra |
| TD-R3 | Sí | Sí | Sí | No entra |
| TD-R4 | Sí | Sí | No | **Entra** (si el presupuesto restante alcanza) |

Además, en toda respuesta válida se verifican las invariantes:
- `total_gtq ≤ presupuesto`
- `restante_gtq = presupuesto − total_gtq`
- ningún juego repetido

## Suites

- **smoke**: `GET /salud`, `GET /version` y PE-01. Es rápida y responde "¿la API está viva y responde lo básico?".
- **regresión**: todos los casos.

Se elige con `pytest -m smoke` o sin filtro (regresión). En el pipeline es el parámetro `SUITE`.
