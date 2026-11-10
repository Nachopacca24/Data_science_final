# Imagen de la API. Se construye UNA vez por commit y la misma imagen se despliega en dev y prod.
# Construir desde la raíz del repo:
#   docker build -f web/Dockerfile --build-arg APP_VERSION=$(git rev-parse HEAD) -t recomendador:$(git rev-parse HEAD) .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY web/requirements.txt web/requirements.txt
RUN pip install -r web/requirements.txt

COPY web/ web/

# El SHA queda escrito dentro de la imagen: /version lo devuelve sin depender del ambiente.
ARG APP_VERSION
RUN test -n "$APP_VERSION" || (echo "Falta --build-arg APP_VERSION=<sha>" >&2; exit 1) \
    && echo "$APP_VERSION" > web/VERSION
LABEL org.opencontainers.image.revision=$APP_VERSION

RUN useradd --create-home app
USER app

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/salud', timeout=2)"
CMD ["uvicorn", "web.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
