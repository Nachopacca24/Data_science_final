# web/: API y pantallas

La API recomienda qué juegos comprar con un presupuesto. También sirve la pantalla. El formato de las peticiones y respuestas está en **[CONTRATO_API.md](CONTRATO_API.md)**.

```
web/
├── CONTRATO_API.md        # formato oficial de la API (para los demás)
├── catalogo_demo.csv      # 500 juegos que usa la API (se sube a git)
├── construir_catalogo.py  # regenera el catálogo desde el dataset y outputs/
├── requirements.txt       # lo que necesita la API para correr
├── requirements-dev.txt   # + pruebas y lint
├── api/
│   ├── main.py            # endpoints
│   ├── esquemas.py        # validación de la entrada y forma de la salida
│   ├── errores.py         # formato único de errores, en español
│   ├── recomendador.py    # similitud coseno + mochila (como el notebook 05)
│   ├── catalogo.py        # lee y valida catalogo_demo.csv
│   └── config.py          # límites, versión y ambiente
└── pantallas/             # pantalla de recomendaciones (HTML + JS, sin dependencias)
```

## Correr en local

Todo desde la raíz del repo:

```bash
pip install -r web/requirements-dev.txt
uvicorn web.api.main:app --reload       # pantalla: http://localhost:8000  ·  docs: /docs
```

Variables opcionales: `APP_VERSION` (SHA; por defecto se lee `web/VERSION`, y si no existe vale `local`) y `APP_AMBIENTE` (`dev` o `prod`; por defecto `dev`).

## Pruebas y lint

```bash
pytest                                              # unitarias (no necesitan el servidor)
API_URL=http://localhost:8000 pytest tests/integracion   # integración (con la API corriendo)
ruff check .
```

## Regenerar el catálogo

Hace falta el dataset completo y `outputs/pred_calidad.csv` del notebook 02:

```bash
pip install -r requirements.txt
python -m src.datos                # descarga el dataset (~400 MB)
python -m web.construir_catalogo   # escribe web/catalogo_demo.csv
```
