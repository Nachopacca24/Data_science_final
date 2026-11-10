# Decisiones

Qué se decidió, por qué y qué se descartó. Si una decisión cambia, se edita aquí en el mismo commit que la cambia.

## 1. Lo que el sistema hereda de Ciencia de Datos

Detalle completo en el [README](README.md) y en los notebooks.

| # | Decisión | Por qué |
|---|---|---|
| D1 | Un juego es "bien recibido" si tiene **más de 80 %** de reseñas positivas | Es el corte que define la pregunta del proyecto (`src/config.py`). |
| D2 | El umbral del clasificador es **0.66**, no 0.5 | Comprar un juego malo (costo 1) duele más que perderse uno bueno (costo 0.5). El 0.66 minimiza el costo (notebook 02). |
| D3 | `puntaje = calidad predicha × parecido` y se elige la combinación con una **mochila** de hasta 5 juegos | El método codicioso desperdicia presupuesto. Con Q200, la mochila logra 2.75 y el codicioso 1.68 (notebook 05). |
| D4 | **El modelo propone, las reseñas confirman** | No se recomienda un juego que el modelo cree bueno si las reseñas reales dicen que es malo (notebook 05). |

## 2. API y catálogo

| # | Decisión | Por qué | Descartado |
|---|---|---|---|
| A1 | La API lee un **catálogo fijo de 500 juegos** (`web/catalogo_demo.csv`) que se sube a git | La API arranca en segundos, la imagen pesa menos de 50 MB y las pruebas usan appids fijos. | Cargar el dataset de 400 MB: lento, no cabe en git y las pruebas no serían repetibles. |
| A2 | El catálogo trae solo juegos donde **modelo y reseñas coinciden** (los 500 con más reseñas) | Aplica D4 de una vez. Así, dentro del catálogo, "pasa el umbral" ya es la regla completa y coincide con la tabla de decisión de `CASOS.md`. | Meter juegos en desacuerdo y filtrar por dos campos: hacía más complicado el contrato. |
| A3 | La API **no importa `src/`**: la similitud y la mochila se reescribieron en Python puro | La imagen no lleva pandas ni sklearn. El resultado coincide con el notebook 05: con DOOM y Hades salen DOOM Eternal (parecido 0.6999 en ambos) y Risk of Rain. | Importar `src/`: arrastra el dataset y todas las librerías de ciencia de datos. |
| A4 | La mochila trabaja en **centavos (enteros)** y es exacta, con frontera de Pareto | Un juego que cuesta justo el presupuesto **sí** cabe (VL-09). El notebook redondea al quetzal hacia arriba y lo dejaría fuera. Una prueba la compara contra la fuerza bruta. | Redondear a quetzales: falla en los valores límite. |
| A5 | A igual puntaje gana la lista con **más juegos** y luego la más barata | La respuesta es siempre la misma, y un juego que cabe no se pierde por empatar en 0. | — |
| A6 | Los juegos **gratis no se recomiendan** | No hay nada que comprar. Además, con Q0.01 la lista debe quedar vacía (VL-02). | — |
| A7 | Entrada **estricta**: `"300"`, `true`, `300.001`, favoritos repetidos o campos extra dan `422` | Un error de quien llama a la API se ve de inmediato en vez de convertirse en silencio en otra cosa. | Dejar que pydantic convierta tipos: `"300"` pasaría como válido. |
| A8 | Todos los errores tienen **el mismo formato** (`error`, `mensaje`, `detalles[campo, problema]`), en español | La pantalla y las pruebas leen un solo formato. | El formato por defecto de FastAPI (`detail`), en inglés. |
| A9 | Límites: presupuesto `0 < p ≤ 10000`, de 1 a 5 favoritos, máximo 5 juegos en la lista | Son los que proponía `CASOS.md`. Se oficializaron en [web/CONTRATO_API.md](web/CONTRATO_API.md). | — |
| A10 | Un catálogo dañado o un `APP_AMBIENTE` desconocido **impiden que la API arranque** | Es mejor fallar en el despliegue que en cada petición. Por eso `/salud` puede responder solo `{"estado": "ok"}`. | — |

## 3. Pruebas

| # | Decisión | Por qué |
|---|---|---|
| P1 | Las pruebas de integración son de **caja negra** contra la API desplegada: partición de equivalencia, valores límite y tabla de decisión | Diseño de José Ignacio en [tests/integracion/CASOS.md](tests/integracion/CASOS.md). Prueban lo que ve quien usa la API, no el código. |
| P2 | Dos suites: **smoke** (3 casos: ¿está viva?) y **regresión** (los 34) | dev corre la regresión. prod corre smoke: si dev ya pasó, en prod basta confirmar que la instancia está viva y es la versión correcta. |
| P3 | Las pruebas unitarias corren **sin servidor** (`TestClient`) y usan un catálogo hecho a mano para la lógica | Son rápidas (menos de 1 s) y no dependen de los datos. Se comprobó que detectan errores: al meter fallas a propósito, las pruebas fallaron (ver EVIDENCIA). |
| P4 | El lint (`ruff`) cubre `web/`, `ci/` y `tests/unitarias/`. `tests/integracion/` queda fuera por ahora | Tiene 2 avisos de estilo (orden de imports). Se arreglan con `ruff check --fix` cuando su autor lo apruebe. |

## 4. Pipeline

| # | Decisión | Por qué | Descartado |
|---|---|---|---|
| C1 | **GitHub Actions** | El repo ya está en GitHub, no requiere instalar nada y cada corrida queda guardada con sus logs. | Jenkins: hay que mantener un servidor. |
| C2 | **Build único**: una imagen Docker por commit, con el SHA escrito adentro (`web/VERSION`). dev y prod cargan **esa misma** imagen | Lo que se probó en dev es exactamente lo que llega a prod. El build se niega a construir sin SHA. | Construir por ambiente: dev y prod podrían terminar con cosas distintas. |
| C3 | **Verificación de versión** después de cada despliegue (`ci/verificar_despliegue.py`): `/version` debe decir el SHA del commit y el ambiente correcto | Evita probar o aprobar una versión vieja o la del otro ambiente. | Confiar en que el despliegue funcionó. |
| C4 | Los dos ambientes son **dos contenedores de la misma imagen** en el runner (dev en el puerto 8001, prod en el 8002), configurados solo con `APP_AMBIENTE` | El curso no da servidores. Así se prueba el flujo completo sin cuentas externas. **Limitación:** las instancias viven lo que dura la corrida, no quedan publicadas. | Hosting externo (Render, etc.): más cuentas y secretos que solo el dueño puede agregar. |
| C5 | prod solo corre **después de que dev pasa** y nunca en pull requests | Un PR no debe tocar prod. | — |
| C6 | **Tiempos máximos por etapa**: 5 min para lint, unitarias y correo, y 10 min para build, dev y prod. Dentro de cada despliegue: 2 min para verificar y 5 min para las pruebas. Además, cada petición de las pruebas tiene 10 s como máximo | Una etapa colgada no bloquea el pipeline por horas (GitHub permite hasta 6 h), y una etapa que se pasa de tiempo cuenta como falla y manda correo. | — |
| C7 | **Correo** por Gmail SMTP con contraseña de aplicación, solo cuando algo falla o se pasa de tiempo | Trae rama, SHA, autor, resultado de cada etapa y enlace a los logs. Si faltan los secretos, la etapa falla y lo dice, para que no se pierda en silencio. | Correo en cada corrida: termina ignorado. |
| C8 | Versiones fijas de todo: las librerías con `==` y las acciones por versión mayor | El mismo commit da el mismo resultado hoy y en un mes. | — |
