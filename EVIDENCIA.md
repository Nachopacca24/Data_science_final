# Evidencia

Qué se corrió, cuándo y qué salió. Solo se registran resultados reales. Lo que todavía no se ha corrido está marcado como (por llenar).

Repositorio: https://github.com/Nachopacca24/Data_science_final
Rama entregada: calidad_final (rama por defecto del repositorio)
Pipeline: pestaña Actions, workflow pipeline
Capturas: carpeta [evidencia/](evidencia/)

## 1. Resumen de lo que pide la entrega

| Qué se pide | Build | Commit | Resultado | Capturas |
|---|---|---|---|---|
| Build verde | #19 | b59c469 | Todas las etapas en verde, 2 min 17 s | [01](evidencia/01-verde-run19-b59c469.png), [01b](evidencia/01b-verde-run19-b59c469-etapas.jpeg) |
| Build rojo, detenido por la puerta de cobertura | [#24](https://github.com/Nachopacca24/Data_science_final/actions/runs/43290789727) | 54cfc56 | pruebas-unitarias en rojo: las pruebas pasan, pero la cobertura baja a 81.82 % y no llega al 90 %. build, dev y prod no corren | (por llenar: 07, 07b log, 07c correo) |
| Build verde otra vez | [#25](https://github.com/Nachopacca24/Data_science_final/actions/runs/43291759699) | 71a118a | 108 pruebas unitarias, cobertura 100 %, todo en verde | (por llenar: 08) |
| Build en el ambiente dev, lanzado a mano | [#27](https://github.com/Nachopacca24/Data_science_final/actions/runs/43292296370) | 0c14655 | ambiente=dev: corre dev y no corre prod | (por llenar: 09) |
| Build en el ambiente prod, lanzado a mano | (por llenar) | (por llenar) | ambiente=prod: corre prod y no corre dev | (por llenar: 10) |
| Parámetro que cambia qué pruebas corren | #20 | b59c469 | Lanzado a mano con suite=smoke: en dev corren 3 pruebas de integración y se saltan 56 | [06](evidencia/06-manual-smoke-run20-b59c469.jpeg), [06b](evidencia/06b-manual-smoke-run20-b59c469-dev-log.jpeg) |
| Correo al fallar | #18 (intento 2) | c77f931 | Llegó con número de build, rama, commit, autor, resultado por etapa y enlace al log | [02b](evidencia/02b-correo-run18-c77f931.jpeg), [05](evidencia/05-rojo-integracion-run-correo18-c77f931.png) |

Todos los commits de esta tabla, menos el del correo (rama demo), están en el historial de calidad_final.

## 2. Cuántas pruebas tiene cada capa

| Capa | Pruebas | Dónde | Cómo corren |
|---|---|---|---|
| Unitarias | 108 | tests/unitarias/ | Sin servidor, antes del build, con la puerta de cobertura (90 % de ramas sobre recomendador.py, catalogo.py, esquemas.py y resumen.py) |
| Integración | 59 (3 de smoke) | tests/integracion/ | Caja negra contra la API desplegada. dev corre la suite que se escoja; prod corre smoke |
| End-to-end | 6 (2 de smoke) | tests/e2e/ | Playwright con page objects contra la pantalla desplegada, en el navegador que se escoja |

## 3. Corridas del pipeline

| Build | Fecha (UTC) | Rama · commit | Evento | lint | unitarias | build | dev | prod | correo | Enlace |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 | 2026-11-10 | calidad_final · 6edb8ec | push | ✅ | ✅ 87 | ✅ | ✅ 34 regresión | ✅ 3 smoke | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/42737504756) |
| #4 | 2026-11-10 | demo-rompe-unitarias · d1b4dc4 | push | ✅ | ❌ 1 falla | no corre | no corre | no corre | ❌ faltaban los secretos | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/42741165796) |
| #15 | 2026-11-12 | demo-rompe-e2e · 810d14c | push | ✅ | ✅ | ✅ | ❌ e2e: 2 fallan | no corre | ✅ en el intento 2 | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43149016724) |
| #17 | 2026-11-12 | calidad_final · 10837c8 | push | ✅ | ✅ | ✅ | ✅ 59 integración + 6 e2e | ✅ 3 + 2 smoke | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43159181319) |
| #18 | 2026-11-12 | demo-rompe-integracion · c77f931 | push | ✅ | ✅ | ✅ | ❌ integración: 1 falla | no corre | ✅ en el intento 2 | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43166417928) |
| #19 | 2026-11-12 | calidad_final · b59c469 | push | ✅ | ✅ | ✅ | ✅ | ✅ | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43171672341) |
| #20 | 2026-11-12 | calidad_final · b59c469 | a mano, suite=smoke | ✅ | ✅ | ✅ | ✅ 3 smoke | ✅ | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43281093110) |
| #21 | 2026-11-12 | calidad_final · b59c469 | a mano | ✅ | ✅ | ✅ | ✅ | ✅ | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43281797875) |
| #22 | 2026-11-12 | calidad_final · c805511 | push | ✅ | ✅ | ✅ | ✅ | ✅ | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43284323145) |
| #23 | 2026-11-12 | calidad_final · e4e791f | push | ✅ | ✅ | ✅ | ✅ | ✅ | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43289503901) |
| #24 | 2026-11-12 | calidad_final · 54cfc56 | push | ✅ | ❌ cobertura 81.82 % | no corre | no corre | no corre | ✅ enviado | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43290789727) |
| #25 | 2026-11-12 | calidad_final · 71a118a | push | ✅ | ✅ 108, 100 % | ✅ | ✅ | ✅ | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43291759699) |
| #26 | 2026-11-12 | calidad_final · 0c14655 | push | ✅ | ✅ | ✅ | ✅ | ✅ | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43292136778) |
| #27 | 2026-11-12 | calidad_final · 0c14655 | a mano, ambiente=dev | ✅ | ✅ | ✅ | ✅ | no corre | no hubo falla | [run](https://github.com/Nachopacca24/Data_science_final/actions/runs/43292296370) |
| (por llenar) | | calidad_final | a mano, ambiente=prod | | | | no corre | | | |

En los builds #15 y #18 el primer intento no mandó correo porque faltaban los secretos SMTP_USUARIO, SMTP_CONTRASENA y CORREO_DESTINO. Se agregaron y se volvieron a correr; en el intento 2 el correo llegó.

## 4. Los builds en rojo: qué etapa y qué prueba fallaron

Cada rama demo cambia solo el código del sistema, no las pruebas, y rompe una sola capa. Ninguna se une a calidad_final.

### Unitarias: demo-rompe-unitarias, build #4

Cambio: en web/api/esquemas.py, el presupuesto pasa de gt=0 a ge=0, así que la API acepta Q0, que el contrato prohíbe.

| Etapa | Resultado |
|---|---|
| lint | ✅ el error es de lógica, no de estilo |
| pruebas-unitarias | ❌ falla test_entrada_api.py::test_presupuesto_invalido[0-cero]: esperaba 422 y la API respondió 200. 1 falla, 86 pasan |
| build, dev, prod | no corren: la versión rota nunca se construye ni se despliega |

Capturas: [04](evidencia/04-rojo-unitarias-run4-d1b4dc4.png), [04b](evidencia/04b-rojo-unitarias-run4-d1b4dc4-log.jpeg)

### Integración: demo-rompe-integracion, build #18

Cambio: en web/api/main.py, restante_gtq pasa de (presupuesto - total) / 100 a (presupuesto + total) / 100.

| Etapa | Resultado |
|---|---|
| lint, unitarias, build | ✅ |
| dev | ❌ falla test_restante_es_presupuesto_menos_total: obtuvo Q522.88 y esperaba Q77.12. 58 pasan, 1 falla. E2E no corre |
| prod | no corre |
| correo | ✅ llegó en el intento 2 |

Capturas: [02](evidencia/02-rojo-integracion-run18-c77f931.png), [02b](evidencia/02b-correo-run18-c77f931.jpeg), [05](evidencia/05-rojo-integracion-run-correo18-c77f931.png)

### End-to-end: demo-rompe-e2e, build #15

Cambio: en web/pantallas/recomendaciones.js, la sección de resultados queda oculta aunque la API responda bien.

| Etapa | Resultado |
|---|---|
| lint, unitarias, build | ✅ las unitarias no prueban la pantalla |
| dev | La integración pasa, pero e2e falla: test_lista_completa_dentro_del_presupuesto (las tarjetas existen pero están ocultas) y test_presupuesto_insuficiente_avisa_que_no_alcanza (el mensaje existe pero está oculto). 2 fallan, 4 pasan, versión 810d14c en dev |
| prod | no corre |

Capturas: [03](evidencia/03-rojo-e2e-run15-810d14c.png), [03b](evidencia/03b-rojo-e2e-run15-810d14c-log.jpeg)

### Cobertura: build #24

Cambio: se agrega web/api/resumen.py (resumen de la lista de compra: total, cuánto sobra, porcentaje usado, el juego más caro, la etiqueta más común y si el presupuesto quedó ajustado u holgado) sin pruebas.

| Etapa | Resultado |
|---|---|
| lint | ✅ |
| pruebas-unitarias | ❌ las 98 pruebas pasan, pero "FAIL Required test coverage of 90.0% not reached. Total coverage: 81.82%". resumen.py queda en 0 % |
| build, dev, prod | no corren |
| correo | ✅ enviado |

En el commit siguiente (71a118a, build #25) se agregan 10 pruebas para resumen.py y el build vuelve a verde con 100 %.

Capturas: (por llenar: 07, 07b log, 07c correo, 08)

## 5. Ambientes y versión

Los dos ambientes son dos contenedores de la misma imagen, construida una sola vez con el SHA del commit: dev en el puerto 8001 y prod en el 8002, configurados con APP_AMBIENTE. Después de desplegar, ci/verificar_despliegue.py consulta /version y detiene el build si el SHA o el ambiente no coinciden. Ejemplo del build #1:

| Ambiente | Respuesta de la instancia |
|---|---|
| dev | OK: http://localhost:8001 responde version=6edb8ec5fd2022bf90eda0ea0d7cf0dfaee3caf6 ambiente=dev |
| prod | OK: http://localhost:8002 responde version=6edb8ec5fd2022bf90eda0ea0d7cf0dfaee3caf6 ambiente=prod |

Builds lanzados a mano por ambiente: dev en el build [#27](https://github.com/Nachopacca24/Data_science_final/actions/runs/43292296370) y prod en el build (por llenar). Capturas 09 y 10 (por llenar).

## 6. Verificación local · 2026-11-09

Se corrió en una Mac con Python 3.14.7 y Docker 28.3.2, sobre calidad_final en 945e292.

| Qué | Resultado |
|---|---|
| ruff check . | sin errores |
| actionlint 1.7.12 | sin errores |
| Build con SHA | imagen de 49 MB, usuario app (no root) |
| Build sin SHA | se niega a construir |
| dev y prod con la misma imagen | /version responde el mismo SHA con su ambiente |
| Verificación con ambiente o SHA equivocado | FALLA y código 1 |
| API que no levanta | FALLA después de 3 s y código 1 |
| APP_AMBIENTE=produccion | la API no arranca |
| Peor caso: Q10,000 con 5 favoritos | 18 ms |

Fallas metidas a propósito para comprobar que las pruebas las detectan (después se revirtieron):

| Falla | Resultado |
|---|---|
| Aceptar presupuesto 0 | 1 prueba unitaria falla |
| Un juego que cuesta justo el presupuesto ya no cabe (<= cambiado por <) | fallan 3 pruebas de Mati y test_dos_juegos_que_suman_justo_el_presupuesto_caben |
| Recomendar juegos que no pasan el umbral | 1 prueba falla |
| Correr solo test_catalogo_y_config.py | la cobertura baja a 32 % y la puerta termina con código 1 |

## 7. Cómo reproducir

```bash
pip install -r web/requirements-dev.txt
ruff check . && pytest --cov
SHA=$(git rev-parse HEAD)
docker build -f web/Dockerfile --build-arg APP_VERSION=$SHA -t recomendador:$SHA .
docker run -d --name recomendador-dev -p 8001:8000 -e APP_AMBIENTE=dev recomendador:$SHA
python ci/verificar_despliegue.py --url http://localhost:8001 --sha $SHA --ambiente dev
API_URL=http://localhost:8001 pytest tests/integracion
```

## 8. Entrega

| Qué | Valor |
|---|---|
| Tag | entrega-calidad (por llenar) |
| SHA del commit entregado | (por llenar, salida de git rev-parse "entrega-calidad^{commit}") |
| Build verde de ese commit | (por llenar) |
