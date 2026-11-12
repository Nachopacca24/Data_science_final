# Pruebas de integración: diseño de casos

Pruebas de **caja negra** contra la API en ejecución: solo se mandan peticiones HTTP y se revisan las respuestas, sin mirar el código.
Herramienta: `pytest` + `requests`. La URL de la instancia se toma de la variable de entorno `API_URL`.

## Contrato

El contrato oficial está en [web/CONTRATO_API.md](../../web/CONTRATO_API.md). Las secciones 1 a 3 se diseñaron antes, con un contrato provisional, y el oficial las respetó: los 34 casos pasaron sin cambios. La sección 4 cubre lo que el contrato oficial agregó.

Los límites se copian en `conftest.py` sin importar `web/`: son pruebas de caja negra y no leen el código.

| Límite | Valor |
|---|---|
| `presupuesto` | `0 < presupuesto ≤ 10000`, máximo 2 decimales |
| `favoritos` | de 1 a 5 appids enteros, sin repetidos, todos en el catálogo |
| juegos en la lista | máximo 5 |
| `limite` de búsqueda | de 1 a 1000 |
| `buscar` | máximo 100 caracteres |

**Regla de negocio:** un juego entra a la lista si **pasa el umbral de calidad**, **es de pago**, **no es uno de los favoritos** (el usuario ya lo tiene) y **cabe en el presupuesto**.

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

## 4. Lo que agregó el contrato oficial

Archivo: `test_contrato.py`. Todos los errores se revisan con el **formato común** `{error, mensaje, detalles[{campo, problema}]}` y, cuando aplica, que `detalles` nombre el campo culpable.

### 4.1 Partición de equivalencia: entrada estricta y errores

| ID | Entrada | Clase | Esperado |
|---|---|---|---|
| PE-15 | presupuesto = `"300"` | inválida: número como texto | 422, campo `presupuesto` |
| PE-16 | presupuesto = `true` | inválida: booleano | 422, campo `presupuesto` |
| PE-17 | favoritos = `["<appid>"]` | inválida: appid como texto | 422 |
| PE-18 | favoritos = `[a, a]` | inválida: repetidos | 422, campo `favoritos` |
| PE-19 | campo `descuento` de más | inválida: campo fuera del contrato | 422, campo `descuento` |
| PE-20 | cuerpo que no es JSON | inválida: no se puede leer | 422, campo `cuerpo` |
| PE-21 | favoritos = `[existente, inexistente]` | inválida: solo el segundo | 422, campo `favoritos.1` |
| PE-22 | `GET /recomendaciones` | inválida: método | 405 `metodo_no_permitido` |
| PE-23 | `GET /no-existe` | inválida: ruta | 404 `no_encontrado` |
| PE-13 | `GET /juegos/{inexistente}` | (complemento) | 404 con el formato común |

### 4.2 Partición de equivalencia: búsqueda

| ID | Entrada | Clase | Esperado |
|---|---|---|---|
| PE-24 | `buscar` = texto que existe, en mayúsculas | válida: con coincidencias | 200; todos lo contienen y vienen en orden alfabético |
| PE-25 | `buscar` = texto que no existe | válida: sin coincidencias | 200 con `[]` (no 404) |

### 4.3 Valores límite

| ID | Límite | Valor | Esperado |
|---|---|---|---|
| VL-11 | decimales del presupuesto | 300.01 | 200 |
| VL-12 | decimales del presupuesto | 300.001 | 422 |
| VL-13 | `limite` mínimo (≥ 1) | 0 | 422 |
| VL-14 | `limite` mínimo | 1 | 200, a lo más 1 juego |
| VL-15 | `limite` máximo | 1000 | 200 |
| VL-16 | `limite` máximo | 1001 | 422 |
| VL-17 | largo de `buscar` | 100 caracteres | 200 |
| VL-18 | largo de `buscar` | 101 caracteres | 422 |
| VL-19 | juegos en la lista (≤ 5) | Q10,000 y 5 favoritos (alcanza para muchos) | 200, entre 1 y 5 juegos |

### 4.4 Tabla de decisión: regla nueva

El contrato oficial agregó la condición C4: **es gratis**.

| Regla | C1: pasa umbral | C4: es gratis | Acción |
|---|---|---|---|
| TD-R5 | Sí | Sí | No entra (no hay nada que comprar) |

Para que la prueba sea exigente, los favoritos son juegos gratis: así los juegos más parecidos también tienden a serlo.

### 4.5 Invariantes de la respuesta

- La lista va de mayor a menor `puntaje`.
- La misma petición da siempre la misma respuesta (se repite 4 veces).
- El `presupuesto` de la respuesta es el que se pidió.

## ¿Las pruebas detectan errores de verdad?

Se metió una falla a la vez en una **copia** de la API (no en el repo), se levantó y se corrió la suite completa:

| Falla inyectada | Pruebas que fallan |
|---|---|
| Aceptar campos extra | PE-19 |
| Aceptar favoritos repetidos | PE-18 |
| Recomendar juegos gratis | TD-R5, VL-02 y VL-09 |
| Lista en orden inverso | orden por puntaje |
| Aceptar presupuesto con 3 decimales | VL-12 |
| Quitar el máximo del `limite` de búsqueda | VL-16 |

Antes, con el contrato provisional: aceptar un presupuesto negativo hacía fallar PE-02, PE-03 y VL-01.

## Suites

- **smoke**: `GET /salud`, `GET /version` y PE-01. Es rápida y responde "¿la API está viva y responde lo básico?".
- **regresión**: todos los casos (59).

Se elige con `pytest -m smoke` o sin filtro (regresión). En el pipeline, dev corre regresión por defecto y permite elegir smoke en el flujo manual; prod corre smoke.
