# Evidencia

Qué se corrió, cuándo y qué salió. Solo resultados reales: lo que todavía no se ha corrido dice **pendiente**.

## 1. Corridas del pipeline en GitHub Actions

Se agregan aquí a medida que corren. Pestaña *Actions* del repo, workflow `pipeline`.

| Fecha | Rama · SHA | lint | unitarias | build | dev | prod | correo | Enlace |
|---|---|---|---|---|---|---|---|---|
| pendiente: primera corrida al subir el pipeline | | | | | | | | |

Por probar en GitHub:
- [ ] Corrida completa en verde (push a `calidad_final`).
- [ ] Corrida a mano con `suite = smoke`.
- [ ] Una falla a propósito llega por correo (necesita los secretos `SMTP_*`; ver README).
- [ ] En un pull request, prod se salta.

## 2. Verificación local · 2026-11-09

Se corrió en una Mac con Python 3.14.7 y Docker 28.3.2. Fue sobre `calidad_final` en `945e292`, con los cambios del pipeline todavía sin commit. El pipeline usa Python 3.12, que es el de la imagen.

### Lint

| Herramienta | Alcance | Resultado |
|---|---|---|
| `ruff check .` | `web/`, `ci/`, `tests/unitarias/` | All checks passed |
| `actionlint` 1.7.12 | `.github/workflows/*.yml` | sin errores |

### Pruebas unitarias: 87 pasan (0.6 s)

| Archivo | Pruebas | Qué cubre |
|---|---|---|
| `test_entrada_api.py` | 48 | validación de entrada (presupuesto, favoritos, cuerpo, appid, búsqueda), formato de errores, `/salud`, `/version`, pantalla |
| `test_recomendador.py` | 19 | similitud, las 3 reglas de candidato, mochila (incluye comparación contra la fuerza bruta y el precio justo/un centavo menos) |
| `test_catalogo_y_config.py` | 15 | catálogo dañado no carga, versión por variable/archivo/`local`, ambientes válidos e inválidos |
| `test_verificar_despliegue.py` | 5 | SHA o ambiente distinto detienen el pipeline, API que no responde agota la espera |

**¿Las pruebas detectan errores de verdad?** Se metieron fallas a propósito en el código, una a la vez, y se revirtieron:

| Falla inyectada | Resultado |
|---|---|
| Aceptar presupuesto = 0 (`gt=0` → `ge=0`) | 1 prueba falla ✔ |
| Un juego que cuesta justo el presupuesto ya no cabe (`<=` → `<`) | 3 pruebas fallan ✔ |
| Recomendar juegos que no pasan el umbral | 1 prueba falla ✔ |

### Build único y despliegue en dos ambientes (simulación local del pipeline)

```
docker build -f web/Dockerfile --build-arg APP_VERSION=945e292fff2a… -t recomendador:945e292fff2a… .
```

| Paso | Resultado |
|---|---|
| Build con SHA | imagen de 49 MB, `org.opencontainers.image.revision` = SHA, usuario `app` (no root) |
| Build **sin** SHA | se niega a construir ✔ |
| dev (`:8001`, `APP_AMBIENTE=dev`) | `OK: version=945e292fff2aa1b793fb833e3bbd0f015463afea ambiente=dev` |
| Integración en dev (regresión) | **34 pasan** (0.17 s) |
| prod (`:8002`, misma imagen, `APP_AMBIENTE=prod`) | `OK: version=945e292fff2aa1b793fb833e3bbd0f015463afea ambiente=prod` |
| Integración en prod (smoke) | **3 pasan**, 31 no seleccionadas |
| Healthcheck del contenedor | `healthy` |
| Peor caso: Q10,000 con 5 favoritos | 18 ms |

**La verificación de versión detiene lo que debe detener:**

| Caso | Salida | Código |
|---|---|---|
| Instancia de prod verificada como dev | `FALLA: ambiente es 'prod' y se esperaba 'dev'` | 1 |
| SHA distinto al del build | `FALLA: version es '945e292…' y se esperaba 'deadbeef'` | 1 |
| API que no levanta | `FALLA: …/salud no respondió 'ok' en 3 s (… Connection refused)` | 1 |
| Contenedor con `APP_AMBIENTE=produccion` | la API no arranca | 3 |

### Pantalla

Se probó en un navegador real (Playwright) a 1200 px y a 375 px de ancho, con este flujo: buscar "doom", elegir DOOM, elegir Hades y recomendar con Q300. Salió la misma lista que la API (DOOM Eternal, Risk of Rain, Half-Life 2, Hotline Miami y The Binding of Isaac, por un total de Q287.88). Con un presupuesto de `300.555` muestra el error `presupuesto: admite como máximo 2 decimales (centavos)` y oculta la lista anterior. La consola no muestra más errores que ese 422, que es el esperado.

## Cómo reproducir

```bash
pip install -r web/requirements-dev.txt
ruff check . && pytest
SHA=$(git rev-parse HEAD)
docker build -f web/Dockerfile --build-arg APP_VERSION=$SHA -t recomendador:$SHA .
docker run -d --name recomendador-dev -p 8001:8000 -e APP_AMBIENTE=dev recomendador:$SHA
python ci/verificar_despliegue.py --url http://localhost:8001 --sha $SHA --ambiente dev
API_URL=http://localhost:8001 pytest tests/integracion
```
