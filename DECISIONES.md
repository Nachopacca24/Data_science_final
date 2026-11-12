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
| P2 | Dos suites: **smoke** (3 casos: ¿está viva?) y **regresión** (los 59: los 34 del diseño original más 25 del contrato oficial) | dev corre la regresión. prod corre smoke: si dev ya pasó, en prod basta confirmar que la instancia está viva y es la versión correcta. |
| P3 | Las pruebas unitarias corren **sin servidor** (`TestClient`) y usan un catálogo hecho a mano para la lógica | Son rápidas (menos de 1 s) y no dependen de los datos. Se comprobó que detectan errores: al meter fallas a propósito, las pruebas fallaron (ver EVIDENCIA). |
| P4 | El lint (`ruff`) cubre todo el código del sistema y de las pruebas: `web/`, `ci/`, `tests/unitarias/` y `tests/integracion/` | Las pruebas también son código: si una prueba tiene un import roto o una variable sin usar, puede pasar sin probar nada. Los 2 avisos de orden de imports de `tests/integracion/` se arreglaron con `ruff check --fix`. |

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

## 5. Pruebas unitarias y puerta de cobertura (Fabiola)

| # | Decisión | Alternativa | Concepto | Evidencia | Fuente |
|---|---|---|---|---|---|
| U1 | El umbral de cobertura es 90 % de branch coverage, no solo de líneas. Hoy los módulos de negocio están en 100 %, así que el 90 % es un piso que no se puede bajar sin que el build se detenga | 80 % como en la HDT 3: con módulos tan pequeños (150 líneas y 30 ramas) deja sin probar una función entera de la mochila sin que nadie se entere. 100 %: cualquier rama defensiva nueva rompe el build y empuja a escribir pruebas que solo ejecutan líneas sin revisar el resultado | Gate, pirámide de pruebas. Cobertura no es calidad: mide qué corrió, no qué se verificó, por eso es un piso y no la meta | Etapa pruebas-unitarias del pipeline. Corriendo solo test_catalogo_y_config.py la cobertura baja a 32 % y pytest termina con exit 1 | [1], [2] |
| U2 | Se usa branch coverage y no statement coverage | Statement coverage: en la mochila, el if nuevos: no tiene else. Si las pruebas siempre encuentran combinaciones que caben, todas las líneas corren y marca 100 %, pero nunca se probó el caso en que ninguna cabe | Branch coverage incluye statement coverage: 100 % de ramas siempre da 100 % de líneas, nunca al revés | branch = true en pyproject.toml. El reporte muestra las columnas Branch y BrPart | [2] |
| U3 | La puerta mide solo los módulos de negocio: recomendador.py (similitud, candidatos y mochila), catalogo.py (lectura y validación del catálogo) y esquemas.py (reglas de entrada) | Medir todo web/api: main.py, errores.py y config.py son conexión HTTP, formato de errores y configuración. No tienen reglas de negocio y ya los cubren las pruebas de integración contra la API desplegada | Pirámide de pruebas: cada capa prueba lo suyo | omit en pyproject.toml. También quedan fuera ci/ (herramienta del pipeline), web/construir_catalogo.py (se corre una vez fuera de la API y usa pandas), src/ (Ciencia de Datos, se valida en los notebooks) y la pantalla (la cubren las e2e) | — |
| U4 | Se mide con source y omit, no con include | Con include, un módulo que ninguna prueba importa no aparece en el reporte y la puerta lo ignora. Así se podía borrar todo un archivo de pruebas sin que bajara la cobertura | Gate: una puerta que no ve un módulo no lo puede bloquear, y da falsa confianza | Al correr solo test_catalogo_y_config.py con include salía 98 %; con source y omit sale 32 % y el build se detiene | [3] |
| U5 | La puerta corre en la etapa de unitarias, antes del build, y el umbral vive en pyproject.toml | Ponerla después del despliegue: se construiría y desplegaría una imagen que igual se va a rechazar. Escribir el umbral en el YAML del pipeline: habría dos lugares que mantener | Shift-left y config as code | needs: [lint, pruebas-unitarias] en el job build. La cobertura sale en el resumen de cada corrida | [1] |
| U6 | Las pruebas de la selección por presupuesto están en su propio archivo, test_seleccion_presupuesto.py, y no se duplicó el módulo de selección | Escribir un módulo de selección aparte: la mochila ya estaba en recomendador.py y tener dos versiones de la misma regla hace que una se quede vieja | Pruebas unitarias sobre la lógica aislada | 11 pruebas: presupuesto exacto, juego que no cabe, catálogo vacío y empates. Al cambiar <= por < en la mochila, falla test_dos_juegos_que_suman_justo_el_presupuesto_caben | — |

[1] J. Humble y D. Farley, Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation. Boston, MA, USA: Addison-Wesley, 2010.

[2] ISTQB, "Certified Tester Foundation Level Syllabus v4.0," International Software Testing Qualifications Board, 2023.

[3] Coverage.py, "Specifying source files," coverage.readthedocs.io. [En línea]. Disponible: https://coverage.readthedocs.io/en/latest/source.html

## 6. Pruebas end-to-end (JuanDa)

| # | Decisión | Alternativa | Concepto | Evidencia | Fuente |
|---|---|---|---|---|---|
| E1 | Cada parte de la pantalla tiene su page object en tests/e2e/paginas/: BusquedaPagina para el formulario y ResultadosPagina para lo que se muestra. Los tests solo llaman métodos como agregar_favorito() o esperar_lista() y no contienen selectores | Escribir los selectores en cada test: un cambio en el HTML (por ejemplo, el id de la lista) obliga a editar todos los tests, y los tests se leen como código de navegador y no como el recorrido de una persona | Page Object Model; pirámide de pruebas: pocos recorridos e2e, los de más valor para quien usa la pantalla | Carpeta tests/e2e/paginas/. Ningún test_*.py contiene locator ni get_by_ (se comprueba con git grep) | [4], [5] |
| E2 | Principio de responsabilidad única: BusquedaPagina solo llena y envía el formulario; ResultadosPagina solo lee lo que la pantalla muestra (tarjetas, totales y mensajes de error) | Una sola clase RecomendacionesPagina: tendría dos motivos para cambiar, el formulario y la zona de resultados, y un cambio en uno obligaría a revisar y volver a probar el otro | Principio de responsabilidad única (S de SOLID) | busqueda_pagina.py no lee resultados y resultados_pagina.py no actúa sobre el formulario. Si cambia el id de la lista solo se edita ResultadosPagina | [6] |
| E3 | Principio abierto/cerrado: BasePagina define abrir() y version_mostrada(), y las dos páginas heredan de ella. Una pantalla nueva hereda y define su RUTA sin modificar la base. Hoy hay una sola pantalla, así que el beneficio es de diseño y no de uso | Un if por pantalla dentro de una clase de navegación: cada pantalla nueva obligaría a editar código que ya funciona y a volver a probarlo | Principio abierto/cerrado (O de SOLID): abierto a extensión, cerrado a modificación | base_pagina.py; BusquedaPagina y ResultadosPagina heredan de BasePagina sin reescribir abrir() ni version_mostrada() | [6] |
| E4 | Las esperas son automáticas: los page objects usan expect(...) (esperar_lista, esperar_lista_vacia, esperar_error), que reintenta hasta que la pantalla refleja la respuesta de la API. No hay sleep en ninguna prueba y antes de leer cantidades o totales siempre se llama a un esperar_* | time.sleep(2) después de cada clic: es lento cuando la API responde rápido y falla cuando responde lento. En la pantalla el buscador espera 200 ms antes de consultar y el resultado llega después de una petición a la API | Flaky test (prueba intermitente) | git grep -n sleep tests/e2e no devuelve nada. Los métodos esperar_* de resultados_pagina.py y la espera dentro de agregar_favorito | [7] |
| E5 | Las e2e son dos pasos de desplegar.yml (instalar Playwright y correr las pruebas), justo después de integración y contra la misma instancia que acaba de verificar ci/verificar_despliegue.py. El parámetro navegador (chromium, firefox o webkit; por defecto chromium) nace en pipeline.yml, llega a dev y prod y solo se instala el elegido. La suite la reutiliza de integración: dev corre las 6 pruebas y prod solo las 2 smoke. Cada paso tiene 5 min como los de integración (C6) y el tope real lo pone el job de 10 min | Un job aparte al final de pipeline.yml: por C4 el contenedor solo existe dentro del job de desplegar.yml, así que ese job tendría que desplegar una segunda instancia. Correr siempre los tres navegadores: alarga el build | Pirámide de pruebas y shift-left: primero lo barato (integración) y al final lo caro (navegador). Config as code: el navegador es un parámetro versionado en el pipeline | Pasos Instalar Playwright y Pruebas end-to-end de desplegar.yml. El log imprime la URL probada, el ambiente, el navegador y la suite. Builds con chromium y EVIDENCIA.md | [1], [8] |
| E6 | Cuatro recorridos: lista completa con dos favoritos (smoke), presupuesto inválido (0 y -50), presupuesto insuficiente (Q0.01, lista vacía) y envío sin favoritos. Solo prueban lo que ve quien usa la pantalla. Las reglas de la API (tipos, decimales, 422) ya las cubre integración (A7). El smoke incluye además una comprobación del pie, que muestra el SHA y el ambiente que responde /version | Repetir en e2e los casos de integración: sería lento, frágil y duplicaría lo que ya cubre la capa de abajo | Pirámide de pruebas: cada capa prueba lo suyo (U3) | test_recorrido_smoke.py y test_recorridos_presupuesto.py: 6 pruebas, 2 smoke y 4 de regresión. Q0.01 sale de VL-02 en CASOS.md | [1], [2] |

[4] M. Fowler, "PageObject," martinfowler.com. [En línea]. Disponible: https://martinfowler.com/bliki/PageObject.html

[5] Microsoft, "Page object models," Playwright Documentation. [En línea]. Disponible: https://playwright.dev/python/docs/pom

[6] R. C. Martin, Agile Software Development, Principles, Patterns, and Practices. Upper Saddle River, NJ, USA: Prentice Hall, 2003.

[7] Microsoft, "Auto-waiting," Playwright Documentation. [En línea]. Disponible: https://playwright.dev/python/docs/actionability

[8] GitHub, "Reusing workflows," GitHub Docs. [En línea]. Disponible: https://docs.github.com/en/actions/sharing-automations/reusing-workflows
