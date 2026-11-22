# CU21/CU22 (HU-47, HU-48) — Clasificación IA con Hugging Face + Matching HITL

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Terminar CU21 (clasificación del motivo de consulta con un modelo de Hugging Face y detección de crisis) y CU22 (Top 3 de psicólogos con fórmula transparente y aprobación humana), siguiendo mensaje por mensaje los diagramas `Secuencia_Corregido_CU21_Clasificacion_IA` y `Secuencia_Corregido_CU22_Matching_Asignacion_IA`.

**Architecture:** Ya existe una base: `clinica/ia_rules_engine.py`, los modelos `ClasificacionIA`/`SugerenciaMatching`, las vistas en `clinica/views.py:1708-1835` y `web/.../triaje/consola-triage.component.ts`. El plan **corrige y reestructura** esa base, no la reescribe desde cero. Cada mensaje del diagrama hacia una entidad (`CE_*`) pasa a ser un método de ese modelo Django. Los mensajes a sí mismo del controlador (`CTR_*`) son métodos del controlador. El modelo de ML vive en un módulo aparte que se carga una sola vez (lazy). Si no puede cargarse, se usa el motor de reglas de respaldo.

**Tech Stack:** Django 5 + DRF + django-tenants, `transformers` + `torch` (CPU), modelo zero-shot multilingüe `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`, Angular 17.

**Spec:** HU-47, HU-48, diagramas de clases y de secuencia CU21/CU22 (capturas en el chat del 2026-11-04).

## Bugs actuales que este plan corrige

1. `ClasificarIntakeView` (views.py:1726) lee `resp.escala_malestar`, que no existe (el campo es `nivel_urgencia_percibido`). Lanza **AttributeError**.
2. `GenerarMatchingView` (views.py:1778) hace prefetch de `horarios_disponibilidad` y `pacientes_asignados`, que no existen (el related_name real es `disponibilidades` y no hay pacientes asignados). Lanza **FieldError**.
3. `Paciente` no tiene `psicologo_asignado` ni `modalidad_preferencia`, y `Psicologo.incrementar_carga()` es un `pass`. Hoy la asignación HITL **no se guarda en ningún lado**.
4. Las severidades son `LEVE/MODERADO/SEVERO/CRITICA`, pero la HU-47 exige `BAJA/MODERADA/ALTA/CRITICA` y además un puntaje de 1 a 5.
5. No se escribe en `AuditoriaIA` ni en la bitácora, y la alerta de crisis no notifica a nadie.
6. La clasificación automática que corre al enviar el intake (`RespuestaPreConsultaViewSet.perform_create`, views.py:337) lee `resp.nivel_urgencia`, otro campo que no existe. La excepción se traga en un `try/except` que solo escribe un warning, así que **ningún intake se clasifica nunca** y la consola de triaje nunca recibe datos reales.
7. Hoy no hay IA: `ClasificadorMotivoConsulta` cuenta palabras clave, y la "confianza" es una fórmula inventada (`coincidencias/total*0.7+0.25`) que no mide nada. Esto se reemplaza.

## Cómo funciona realmente la IA en este proceso

**Solo CU21 usa machine learning. CU22 no.** El matching es una fórmula ponderada que no aprende nada, y así lo pide la HU-48 ("fórmula transparente"). Usar ML ahí sería contrario a la HU, porque el coordinador no podría auditar por qué se sugirió a un psicólogo.

**Qué modelo y por qué no se entrena.** `mDeBERTa-v3-base-mnli-xnli` es un modelo de *inferencia de lenguaje natural* (NLI) que ya viene entrenado en más de 100 idiomas, incluido el español. Recibe dos frases y responde con qué probabilidad la segunda se deduce de la primera. La técnica *zero-shot* aprovecha eso:

```
texto     = "no duermo, siento taquicardia y miedo de salir de casa"
hipótesis = "Este texto trata sobre ansiedad, miedo o pánico."         → 0.91
hipótesis = "Este texto trata sobre tristeza o depresión."             → 0.05
hipótesis = "Este texto trata sobre problemas de pareja o familia."    → 0.02 ...
→ categoria = ANSIEDAD_FOBIAS, confianza = 0.91
```
Por eso **no hace falta un dataset de entrenamiento**: las categorías se definen como frases en español y se pueden ajustar sin reentrenar. A cambio, el modelo no es clínico ni está validado clínicamente. Por eso existen la red de reglas y el HITL.

**Flujo completo de un intake, por capas:**

| Paso | Quién decide | Qué hace |
|---|---|---|
| 1. Anonimizar | Regex (código fijo) | Quita teléfono, CI, email y nombre del paciente. El modelo nunca ve PII. |
| 2. Categoría temática | **Modelo ML** (llamada 1, single-label) | Elige 1 de 5 áreas con su probabilidad = `confianza_score`. Si es menor a 0.30, la categoría es `OTRO`. |
| 3. Riesgo | **Modelo ML** (llamada 2, multi-label) | Calcula `p_riesgo` = probabilidad de "ideación suicida o autolesión" / "violencia o abuso". |
| 4. Red de seguridad | Reglas (código fijo) | Si hay patrones como "quiero morir" o "me golpea", el riesgo sube a 0.95 aunque el modelo diga 0. Las reglas solo pueden **subir** el riesgo. |
| 5. Severidad | Fórmula fija | `score = max(p_riesgo, malestar)`. Con 0.70 o más se activa el protocolo de crisis. |
| 6. Auditoría | Código | Guarda el hash SHA-256 de la entrada y la salida, el id real del modelo y si hubo alerta. |
| 7. Decisión | **Humano** | El coordinador ve la sugerencia. La IA nunca asigna, nunca diagnostica y nunca cierra un caso. |
| 8. Matching (CU22) | Fórmula fija | Usa la categoría del paso 2 como entrada de la "Afinidad". |

**Qué tiene que cumplirse en ejecución para que funcione de verdad** (parte de Task 2):
- Primera ejecución: descarga del modelo de ~1.1 GB a `HF_HOME` (variable en `.env`). Sin internet esa primera vez se usa el respaldo por reglas y la auditoría lo registra como `REGLAS-FALLBACK`.
- Memoria: ~1.2 GB de RAM por proceso que cargue el modelo. Gunicorn tiene `--workers 2` (`entrypoint.sh:64`), así que se agrega `--preload`: el modelo se carga una vez en el proceso maestro y los workers lo comparten (copy-on-write en Linux), lo que evita 2.4 GB.
- Latencia: ~1–2 s por intake en CPU (2 llamadas al modelo). Se acepta que corra síncrono al enviar el intake (`--timeout 120` lo cubre). En el primer request el modelo se carga (~10–20 s), por eso se precarga.
- Command `python manage.py precargar_modelo_ia`: descarga el modelo, lo calienta con un texto de prueba e imprime una clasificación. Se usa en el Dockerfile (`ARG PRELOAD_IA`) y para verificar en local.
- Tests: con `IA_HABILITADA=0` son deterministas y no descargan nada. La evaluación real del modelo es la Task 2b.

## Global Constraints

- Fórmula exacta (HU-48): `Score = 0.4×Afinidad + 0.3×Disponibilidad + 0.2×BalanceCarga + 0.1×Modalidad`. Cada factor va de 0 a 1 y el score se muestra de 0 a 100 con un decimal.
- Severidades (HU-47): `BAJA`, `MODERADA`, `ALTA`, `CRITICA`. Puntaje de 1 a 5.
- Umbral del protocolo de crisis (diagrama CU21, alt): `score_severidad >= 0.70 o alerta_crisis == true`.
- Categorías: `ANSIEDAD_FOBIAS`, `DEPRESION_ANIMO`, `PAREJA_FAMILIA`, `INFANTO_JUVENIL`, `DUELO_ADAPTACION` (más `OTRO`, que ya existe).
- La PII (teléfono, carnet, email y el nombre del propio paciente) se elimina **antes** de que el texto llegue al modelo.
- Ningún paciente se asigna sin un POST explícito del coordinador (HITL). Ni GET ni la clasificación asignan nunca.
- La detección de crisis por reglas **siempre** corre, aunque el modelo de ML esté disponible. El ML puede subir el riesgo, pero nunca puede bajar una alerta que detectaron las reglas.
- Los tests siguen el patrón del repo: scripts ejecutables con `venv/Scripts/python.exe tests/<archivo>.py` (no hay pytest). Los tests con BD usan `schema_context('centro_esperanza')`.

## Review Focus

- **Texto vacío o solo PII** (`"71234567"`): debe clasificar como `OTRO`/`BAJA` sin llamar al modelo y sin romperse. Test en Task 2.
- **Modelo HF no descargado o sin internet en el primer arranque**: se usa el respaldo por reglas, `modelo_ia='REGLAS-FALLBACK'` y la respuesta es 200, no 500. Test en Task 2.
- **Doble clic en “Aprobar”** (o aprobar una sugerencia ya decidida): debe responder 409 sin volver a incrementar la carga. Test en Task 5.
- **Paciente que ya tiene psicólogo asignado**: tanto aprobar como reasignar manualmente responden 409 (la reasignación queda fuera de alcance). Test en Task 5.
- **Todos los psicólogos con cupo completo**: el Top 3 sale igual, pero con `cupo_completo=true` y debajo de cualquiera que tenga cupo. Test en Task 4.

---

### Task 1: Migración de modelos (campos que piden los diagramas)

**Files:**
- Modify: `backend/clinica/models.py` (`Psicologo` :53, `Paciente` :209, `AuditoriaIA` :651, `ClasificacionIA` :824, `SugerenciaMatching` :876)
- Create: `backend/clinica/migrations/0008_cu21_cu22_ia_matching.py` (con `makemigrations` y luego un `RunPython` agregado a mano)
- Test: `backend/tests/test_cu21_cu22_modelos.py`

**Interfaces — Produces:**
- `Psicologo.carga_actual: PositiveIntegerField(default=0)`, `Psicologo.cupo_maximo: PositiveIntegerField(default=20)`
- `Psicologo.incrementar_carga() -> int`: hace `F('carga_actual') + 1` y luego `refresh_from_db`, y devuelve la carga nueva.
- `Psicologo.listar_candidatos_activos() -> QuerySet` (classmethod): `activo=True, usuario__is_active=True`, con `select_related('usuario')` y `prefetch_related('psicologoespecialidad_set__especialidad', 'disponibilidades')`.
- `Psicologo.cupo_completo -> bool` (property): `carga_actual >= cupo_maximo`.
- `Paciente.modalidad_preferencia: CharField(choices=Psicologo.MODALIDAD_CHOICES, default='MIXTA')`
- `Paciente.psicologo_asignado: FK(Psicologo, null=True, SET_NULL, related_name='pacientes_asignados')`
- `Paciente.obtener_paciente(paciente_id) -> dict` (classmethod): devuelve `{paciente_id, nombre, apellido, expediente, modalidad_preferencia}`. Reutiliza `obtener_paciente_asociado` y le agrega la modalidad.
- `ClasificacionIA.SEVERIDAD_CHOICES = BAJA/MODERADA/ALTA/CRITICA`. Campos nuevos: `puntaje_severidad: PositiveSmallIntegerField(1-5)`, `score_severidad: DecimalField(4,3)`, `nivel_atencion: CharField(choices=[('CRITICO','Crítico'),('REGULAR','Regular')])`, `modelo_ia: CharField(64)`.
- `AuditoriaIA`: campos nuevos `modelo_ia: CharField(64, default='')`, `alerta_crisis: BooleanField(default=False)`, `clasificacion: FK(ClasificacionIA, null=True, SET_NULL)`.
- `SugerenciaMatching`: campos nuevos `aprobado_hitl: BooleanField(null=True)`, `psicologo_asignado_final: FK(Psicologo, null=True, SET_NULL, related_name='+')`.
- `RunPython`: convierte las severidades viejas así: `LEVE→BAJA`, `MODERADO→MODERADA`, `SEVERO→ALTA`. Reverse: la operación inversa.

- [ ] **Step 1: Test que falla.** Dentro de `schema_context`, crear un psicólogo con `cupo_maximo=2` y llamar dos veces a `incrementar_carga()`. Assert: `carga_actual == 2` y `cupo_completo is True`. Assert: `Paciente.obtener_paciente(p.id)['modalidad_preferencia'] == 'MIXTA'`. Limpiar al final (marca `[TEST CU21-22]`).
- [ ] **Step 2:** `venv/Scripts/python.exe tests/test_cu21_cu22_modelos.py`. Se espera: FAIL (`carga_actual` no existe).
- [ ] **Step 3:** Agregar los campos y métodos. `makemigrations clinica` y añadir el `RunPython`. `migrate_schemas`.
- [ ] **Step 4:** Volver a correr el test. Se espera: PASS.
- [ ] **Step 5:** Commit `feat(cu21-cu22): campos de carga, asignación, severidad HU-47 y auditoría IA`.

---

### Task 2: Motor de inferencia Hugging Face + reglas de respaldo (CU21, mensajes 3, 7 y 8)

**Files:**
- Create: `backend/clinica/ia_nlp.py` (solo la carga y la inferencia del modelo HF)
- Create: `backend/clinica/management/commands/precargar_modelo_ia.py`: llama a `_pipeline()`, clasifica un texto de prueba e imprime el resultado y el tiempo.
- Modify: `backend/clinica/ia_rules_engine.py:150-260` (`ClasificadorMotivoConsulta` queda como respaldo por reglas y conserva `PATRONES_CRISIS`)
- Modify: `backend/clinica/models.py` (`RespuestaPreConsulta.sanitizar_pii`)
- Modify: `backend/requirements.txt` (`transformers>=4.44,<5`, `torch>=2.3` CPU, `sentencepiece`, `protobuf`), `backend/Dockerfile` (`pip install torch --index-url https://download.pytorch.org/whl/cpu` antes de requirements; precarga opcional del modelo con `RUN python -c ...` detrás de `ARG PRELOAD_IA=0`)
- Modify: `backend/sigepsi/settings.py`: `IA_MODELO_HF = os.getenv('IA_MODELO_HF', 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli')`, `IA_HABILITADA = os.getenv('IA_HABILITADA', '1') == '1'`. Agregar ambas a `.env.example`.
- Test: modificar `backend/tests/test_sprint3_clasificacion_ia.py`

**Interfaces — Produces:**
- `RespuestaPreConsulta.sanitizar_pii(self, texto_motivo: str) -> str`: usa las regex actuales (teléfono, CI de 6 a 9 dígitos, email) y además reemplaza `self.paciente.usuario.nombre` y `apellido` (sin importar mayúsculas, palabra completa) por `[NOMBRE ANONIMIZADO]`. Es el **mensaje 3** del diagrama.
- `ia_nlp.consultar_inferencia_nlp(texto_anonimizado: str) -> dict`. Es el **mensaje 7** y devuelve `{categoria: str, confianza: float, p_riesgo: float, modelo_ia: str}`.
  - `@functools.lru_cache(maxsize=1) def _pipeline()` construye `pipeline('zero-shot-classification', model=settings.IA_MODELO_HF, device=-1)`.
  - Categoría: una llamada single-label con `hypothesis_template='Este texto trata sobre {}.'` y estas etiquetas: `{'ansiedad, miedo o pánico':'ANSIEDAD_FOBIAS','tristeza o depresión':'DEPRESION_ANIMO','problemas de pareja o familia':'PAREJA_FAMILIA','problemas de un niño o adolescente':'INFANTO_JUVENIL','duelo o pérdida de un ser querido':'DUELO_ADAPTACION'}`. Si la confianza es menor a 0.30, la categoría es `OTRO`.
  - Riesgo: una segunda llamada con `multi_label=True` sobre `['ideación suicida o autolesión','violencia o abuso']`. `p_riesgo = max(scores)`.
  - Cualquier excepción (no hay librería, no hay red, OOM) o `IA_HABILITADA=False` hace que se use `ClasificadorMotivoConsulta` por reglas, y entonces `modelo_ia='REGLAS-FALLBACK'` y `p_riesgo` vale 0.95 si hay patrón de crisis o 0.0 si no.
  - Si el texto queda vacío después de quitarle los marcadores `[...]`, devuelve `{'OTRO', 0.0, 0.0, 'SIN-TEXTO'}` sin llamar al modelo.
- `ia_nlp.evaluar_patrones_riesgo_crisis(score: float, categoria: str, texto: str, escala_malestar: int) -> dict`. Es el **mensaje 8** y devuelve `{score_severidad, puntaje_severidad, nivel_severidad, alerta_crisis, palabras_clave}`. Algoritmo:
  ```
  reglas = [p for p in PATRONES_CRISIS if p in texto.lower()]
  score = max(score, (escala_malestar-1)/4 * 0.69)   # el malestar solo nunca dispara crisis
  if reglas: score = max(score, 0.95)                 # las reglas solo pueden subir el riesgo
  alerta = bool(reglas) or score >= 0.70
  nivel = BAJA (<0.35) | MODERADA (<0.55) | ALTA (<0.70) | CRITICA (>=0.70)
  puntaje = 1 + round(score*4)
  ```
  Además: agregar a `PATRONES_CRISIS` los términos de violencia (`'me golpea'`, `'me pega'`, `'abuso'`, `'violencia'`, `'amenaza de muerte'`), porque la HU pide “ideación autolítica **o violencia**”.

- [ ] **Step 1: Tests que fallan** (sin red y sin BD: con `monkeypatch` manual de `ia_nlp._pipeline` para que lance excepción, y otro caso con un stub que devuelve scores fijos):
  - `test_sanitizar_pii_incluye_nombre`: con un objeto fake que tiene `paciente.usuario.nombre='Ana'`, el resultado no contiene `Ana`, `8374829`, `ana@x.com` ni `71234567`.
  - `test_fallback_sin_modelo`: el pipeline lanza excepción, entonces `modelo_ia == 'REGLAS-FALLBACK'` y la categoría de un texto de ansiedad es `ANSIEDAD_FOBIAS`.
  - `test_texto_vacio`: `consultar_inferencia_nlp('[TELÉFONO ANONIMIZADO]')['categoria'] == 'OTRO'` sin llamar al pipeline (el stub falla si lo llaman).
  - `test_crisis_por_reglas_aunque_ml_diga_cero`: `evaluar_patrones_riesgo_crisis(0.0, 'DEPRESION_ANIMO', 'quiero morir', 2)`. Assert: `alerta_crisis is True`, `nivel_severidad == 'CRITICA'` y `puntaje_severidad == 5`.
  - `test_malestar_5_sin_texto_riesgo`: `(0.0, 'ANSIEDAD_FOBIAS', 'nervios', 5)`. Assert: `alerta_crisis is False` y `nivel_severidad == 'ALTA'`.
  - `test_violencia`: el texto `'mi pareja me golpea'` produce `alerta_crisis is True`.
  - `test_stub_hf`: el stub devuelve `ansiedad…=0.9` y `riesgo=0.8`, entonces la categoría es `ANSIEDAD_FOBIAS` y `alerta_crisis is True`.
- [ ] **Step 2:** Correr los tests. Se espera: FAIL (no existe el módulo `ia_nlp`).
- [ ] **Step 3:** Implementar. `pip install` las dependencias en el venv.
- [ ] **Step 4:** Correr los tests. Se espera: PASS. Prueba manual real (descarga unos 1.1 GB la primera vez): `venv/Scripts/python.exe -c "import django,os;os.environ['DJANGO_SETTINGS_MODULE']='sigepsi.settings';django.setup();from clinica.ia_nlp import consultar_inferencia_nlp as f;print(f('no puedo dormir, tengo ataques de pánico'))"` debe dar `categoria='ANSIEDAD_FOBIAS'` y `modelo_ia` igual al id de HF.
- [ ] **Step 5:** Commit `feat(cu21): inferencia zero-shot Hugging Face con red de seguridad por reglas`.

---

### Task 2b: Evaluación del modelo con casos en español (sin esto, "funciona" sería solo una suposición)

**Files:**
- Create: `backend/clinica/ia_eval/casos_evaluacion.json`: 50 textos de intake escritos a mano (10 por categoría). 12 de ellos son de riesgo y 4 son "trampas" que no son crisis ("me muero de risa", "quiero matar el tiempo", "mi abuela murió hace años y ya lo superé").
- Create: `backend/clinica/management/commands/evaluar_modelo_ia.py`
- Modify: `backend/clinica/management/commands/precargar_modelo_ia.py` (creado en Task 2)

**Interfaces — Produces:** `manage.py evaluar_modelo_ia` imprime la exactitud por categoría, la matriz de confusión, el **recall de crisis** y la cantidad de falsos positivos de crisis. Termina con exit code 1 si `recall_crisis < 1.0` o `exactitud_categoria < 0.70`.

- [ ] **Step 1:** Escribir el JSON. Formato: `[{"texto": str, "categoria": str, "crisis": bool}]`.
- [ ] **Step 2:** Correr `evaluar_modelo_ia` con el modelo real.
- [ ] **Step 3:** Si falla: ajustar **solo** las frases de las etiquetas, el `hypothesis_template`, el umbral `OTRO` (0.30) o agregar patrones a `PATRONES_CRISIS`. Nada de reentrenar. Repetir hasta que pase. Anotar los valores finales en el docstring de `ia_nlp.py`.
- [ ] **Step 4:** Commit `test(cu21): set de evaluación y métricas del modelo zero-shot`.

Criterio fijo: **no se acepta perder ninguna crisis** (recall = 1.0). Los falsos positivos se toleran porque los revisa un humano.

---

### Task 3: Controlador CU21 `POST /api/v1/ia/clasificar-triaje/` (mensajes 2 a 25)

**Files:**
- Modify: `backend/clinica/models.py`: `ClasificacionIA.persistir_clasificacion`, `AuditoriaIA.generar_hash_sha256` y `AuditoriaIA.registrar_auditoria_inferencia`. `marcar_crisis_prioritaria` ya existe.
- Modify: `backend/clinica/views.py:1713-1741`: `ClasificarIntakeView` se renombra a `CTR_ClasificacionIAController` (APIView) y se deja `ClasificarIntakeView = CTR_ClasificacionIAController` como alias para la ruta vieja.
- Modify: `backend/clinica/views.py:324-354` (`RespuestaPreConsultaViewSet.perform_create`): se borra el bloque duplicado (que tiene el bug 6) y se reemplaza por una llamada a `CTR_ClasificacionIAController.clasificar(resp, ip=...)`. Se mantiene el `try/except` para que un fallo de IA no impida guardar el intake, pero se registra con `logger.exception` (traza completa) en lugar de un warning silencioso. Test: crear un intake por `POST /intake/` hace que exista una `ClasificacionIA` para él.
- Modify: `backend/entrypoint.sh:64`: agregar `--preload`.
- Modify: `backend/clinica/urls.py`: `path('ia/clasificar-triaje/', ...)`
- Modify: `backend/clinica/serializers.py:1184` (exponer los campos nuevos)
- Test: `backend/tests/test_cu21_clasificacion_api.py`

**Interfaces — Produces:**
- `ClasificacionIA.persistir_clasificacion(respuesta, resultado: dict, nivel: str) -> ClasificacionIA` (classmethod, con `update_or_create` por `respuestapreconsulta`). Corresponde a los mensajes 9 y 19.
- `AuditoriaIA.generar_hash_sha256(input: str, inferencia: dict) -> str` (staticmethod): `sha256(input + json.dumps(inferencia, sort_keys=True))`. Corresponde a los mensajes 13 y 21.
- `AuditoriaIA.registrar_auditoria_inferencia(modelo: str, hash: str, alerta: bool, clasificacion, ip: str) -> AuditoriaIA` (classmethod). Crea la fila (`hash_prompt=hash`, `prioridad_sugerida=nivel_severidad`, `resumen_generado=explicacion`, `formulario_respuesta_id=respuesta.id`) y además llama a `audit.services.log_event(accion='IA_INFERENCIA', alerta_crisis=alerta, ...)` sin texto clínico. Corresponde a los mensajes 15 y 23.
- `CTR_ClasificacionIAController.clasificar(respuesta, texto_motivo=None, escala_malestar=None, ip='') -> (dict, int)`: lo usa también `perform_create`.
- Request: `{respuesta_id: uuid, texto_motivo?: str, escala_malestar?: 1-5}`. Si no vienen, se toman de la entidad. Si no existe la respuesta, devuelve 404. Si `escala_malestar` está fuera de 1 a 5, devuelve 400.
- Response con crisis (mensaje 17): `200 {alerta_crisis: true, nivel: 'ALTO', sugerencia_inmediata: 'Activar protocolo de crisis: contactar al paciente y derivar a atención inmediata.', clasificacion: {...}}`
- Response ordinaria (mensaje 25): `200 {alerta_crisis: false, nivel: 'REGULAR', clasificacion: {...}}`

Orden exacto del cuerpo (calcado del diagrama):
```
texto = respuesta.sanitizar_pii(texto_motivo)                 # 3-4
datos = Paciente.obtener_paciente(respuesta.paciente_id)      # 5-6
inf = consultar_inferencia_nlp(texto)                         # 7
r = evaluar_patrones_riesgo_crisis(inf['p_riesgo'], inf['categoria'], texto, escala_malestar)  # 8
if r.score_severidad >= 0.70 or r.alerta_crisis:              # alt Protocolo Crisis
    c = ClasificacionIA.persistir_clasificacion(..., nivel='CRITICO')   # 9-10
    c.marcar_crisis_prioritaria()                                       # 11-12
    h = AuditoriaIA.generar_hash_sha256(texto, inf)                     # 13-14
    AuditoriaIA.registrar_auditoria_inferencia(inf.modelo_ia, h, True)  # 15-16
    return 200 {alerta_crisis: True, nivel: 'ALTO', ...}               # 17
else:                                                         # Atención ordinaria
    c = persistir_clasificacion(..., nivel='REGULAR')                   # 19-20
    h = generar_hash_sha256(...); registrar_auditoria_inferencia(..., False)  # 21-24
    return 200 {alerta_crisis: False, nivel: 'REGULAR', ...}           # 25
```

- [ ] **Step 1: Tests que fallan** (API real con `APIClient` autenticado como coordinador, en el tenant `centro_esperanza`, con `IA_HABILITADA=0` para que sea determinista):
  - Un intake con `'quiero quitarme la vida'` produce 200, `alerta_crisis True`, `nivel 'ALTO'`, `ClasificacionIA.nivel_atencion=='CRITICO'`, `nivel_severidad=='CRITICA'`, y una fila de `AuditoriaIA` con `alerta_crisis=True` y un `hash_prompt` de 64 caracteres.
  - Un intake con `'discuto mucho con mi pareja'` y malestar 2 produce `alerta_crisis False`, `nivel 'REGULAR'`, categoría `PAREJA_FAMILIA` y una `AuditoriaIA` con `alerta_crisis=False`.
  - Volver a clasificar el mismo intake deja **una sola** `ClasificacionIA` (update_or_create).
  - El texto `'llamar al 71234567'`: el texto guardado en `palabras_clave_detectadas` y en la explicación no contiene `71234567`.
  - Con `respuesta_id` inexistente responde 404. Con `escala_malestar=9` responde 400.
  - `POST /api/v1/intake/<id>/clasificar/` (ruta vieja) también responde 200 (regresión del bug 1).
- [ ] **Step 2:** Correr. Se espera: FAIL (404 en la ruta nueva).
- [ ] **Step 3:** Implementar.
- [ ] **Step 4:** Correr. Se espera: PASS. Volver a correr `tests/test_sprint3_clasificacion_ia.py` para comprobar la regresión.
- [ ] **Step 5:** Commit `feat(cu21): controlador clasificar-triaje según secuencia corregida`.

---

### Task 4: Algoritmo de matching y `GET /api/v1/matching/sugerencias/?paciente_id=` (CU22, mensajes 2 a 18)

**Files:**
- Modify: `backend/clinica/ia_rules_engine.py:267-357`: `MatchingPsicologoService` pasa a `calcular_score(...)` puro. Se borran los `hasattr` defensivos.
- Modify: `backend/clinica/models.py`: `ClasificacionIA.extraer_triaje`, `PsicologoEspecialidad.verificar_especialidad`, `Especialidad.obtener_nombre`, `SugerenciaMatching.persistir_top3_candidatos`. `Usuario.get_full_name` ya existe (verificarlo en `accounts/models.py`).
- Modify: `backend/clinica/views.py:1753-1796`: nuevo `CTR_MatchingController(viewsets.ViewSet)` con la acción `sugerencias` (GET, list route). `GenerarMatchingView` queda como alias que delega en él.
- Modify: `backend/clinica/urls.py`: `router.register(r'matching', CTR_MatchingController, basename='matching')`
- Test: modificar `backend/tests/test_sprint3_matching.py` (unitario puro) y crear `backend/tests/test_cu22_matching_api.py`

**Interfaces — Produces:**
- `ClasificacionIA.extraer_triaje(paciente_id) -> dict | None` (classmethod): devuelve `{categoria, severidad, clasificacion_id}` de la última clasificación. Mensajes 3-4.
- `PsicologoEspecialidad.verificar_especialidad(psicologo_id) -> list[Especialidad]` (classmethod). Mensajes 9-10.
- `Especialidad.obtener_nombre() -> str`. Mensajes 11-12. Se compara contra `nombre + descripcion` en minúsculas.
- `MatchingPsicologoService.AREAS_POR_CATEGORIA = {'ANSIEDAD_FOBIAS':['ansiedad','cognitivo'], 'DEPRESION_ANIMO':['ánimo','animo','depres'], 'PAREJA_FAMILIA':['pareja','familiar'], 'INFANTO_JUVENIL':['infan','adolesc'], 'DUELO_ADAPTACION':['duelo','paliativ'], 'OTRO':[]}` (sale de las especialidades del seed de `seed_sprint1.py:170`).
- `MatchingPsicologoService.calcular_score(afinidad: float, carga: tuple[int,int], disponibilidad: int, modalidad_psico: str, modalidad_pac: str) -> dict`. Mensaje 15. Devuelve `{score: float (0-100, 1 decimal), factores: {afinidad, disponibilidad, balance_carga, modalidad} (cada uno entre 0 y 1), cupo_completo: bool}`.
  - `afinidad`: 1.0 si alguna especialidad contiene algún token de la categoría. Si no, 0.0.
  - `disponibilidad`: `min(1, bloques_activos/10)`.
  - `balance_carga`: `0.0` si `carga >= cupo`. Si no, `1 - carga/cupo`.
  - `modalidad`: 1.0 si `'MIXTA' in (psico, pac)` o `psico == pac`. Si no, 0.0.
  - `score = round(100*(0.4a + 0.3d + 0.2b + 0.1m), 1)`.
- Orden del Top 3: `sorted(key=lambda c: (c.cupo_completo, -c.score))[:3]`. Con esto se cumple el criterio b: los psicólogos con cupo completo quedan penalizados (balance 0) y además van detrás de cualquiera que tenga cupo.
- `SugerenciaMatching.persistir_top3_candidatos(paciente, clasificacion, candidatos: list[dict]) -> list[SugerenciaMatching]` (classmethod, `transaction.atomic`). Primero borra las sugerencias `PENDIENTE_VALIDACION` previas del paciente. Mensajes 16-17.
- Response 200 (mensaje 18): `{paciente: {...obtener_paciente}, triaje: {categoria, severidad}, top3_candidatos: [{sugerencia_id, psicologo_id, nombre_psicologo, especialidades: [str], score, factores, carga_actual, cupo_maximo, cupo_completo}]}`
- Si el paciente no existe responde 404. Si no tiene clasificación, la respuesta es 409 `{"error": "El paciente no tiene triaje IA; ejecute CU21 primero."}`. Esto respeta el diagrama, donde el mensaje 3 es obligatorio. Si el paciente ya tiene `psicologo_asignado`, la respuesta es 409.

- [ ] **Step 1: Tests que fallan.**
  - Unitario: `calcular_score(1.0, (5,20), 8, 'MIXTA', 'VIRTUAL')` da `score == 0.4*100 + 0.3*80 + 0.2*75 + 0.1*100 = 89.0` y `factores['balance_carga'] == 0.75`.
  - Unitario (Review Focus): con 4 candidatos y 3 de ellos con cupo completo, el top1 es el único con cupo aunque tenga menos score, y los saturados tienen `balance_carga == 0.0`.
  - API: un paciente con clasificación de ansiedad y 2 psicólogos (uno con la especialidad TCC) produce 200, el top1 es el de TCC, la respuesta trae el desglose de `factores` y se crean 2 filas `SugerenciaMatching` en `PENDIENTE_VALIDACION`.
  - API: si se llama dos veces, siguen existiendo solo las sugerencias pendientes de la última llamada.
  - API: un paciente sin clasificación produce 409.
  - API: el GET **no** modifica `paciente.psicologo_asignado` ni `carga_actual`.
- [ ] **Step 2:** Correr. Se espera: FAIL.
- [ ] **Step 3:** Implementar.
- [ ] **Step 4:** Correr. Se espera: PASS.
- [ ] **Step 5:** Commit `feat(cu22): matching multivariable transparente según secuencia corregida`.

---

### Task 5: Aprobación HITL y reasignación manual auditada (CU22, mensajes 20 a 38)

**Files:**
- Modify: `backend/clinica/models.py`: ajustar `SugerenciaMatching.marcar_aprobada()` / `marcar_rechazada_manual(motivo)`, y crear `asignacion_auditada(...)` y `asignacion_manual_auditada(...)`
- Modify: `backend/clinica/views.py`: acciones `aprobar` y `rechazar_y_reasignar` en `CTR_MatchingController`. `AsignarPsicologoHITLView` delega en ellas para mantener vivas las rutas `ia/confirmar-asignacion/` e `ia/asignacion-manual/`.
- Modify: `backend/clinica/permissions.py`: reutilizar el permiso de coordinador/admin que ya exista. Si no hay uno, crear `EsCoordinadorClinico` con el mismo patrón que los permisos de ese archivo.
- Test: `backend/tests/test_cu22_matching_api.py` (se amplía)

**Interfaces — Produces:**
- `POST /api/v1/matching/{sugerencia_id}/aprobar/` con `{psicologo_id}`. Mensaje 21. Orden: `marcar_aprobada()` (22) → `psicologo.incrementar_carga()` (24) → `asignacion_auditada(aprobado_hitl=True, coordinador)` (26) → 200 `{mensaje: 'Psicólogo asignado exitosamente', ...}` (28).
- `POST /api/v1/matching/{sugerencia_id}/rechazar_y_reasignar/` con `{psicologo_manual_id, motivo}`. Mensaje 31. Orden: `marcar_rechazada_manual(motivo)` (32) → `psicologo_manual.incrementar_carga()` (34) → `asignacion_manual_auditada(aprobado_hitl=False, justificacion=motivo)` (36) → 200 `{mensaje: 'Asignación manual registrada', ...}` (38).
- Las dos acciones van dentro de `transaction.atomic()` + `select_for_update()` sobre la sugerencia y el paciente. En las dos: `paciente.psicologo_asignado = psicologo` y las demás sugerencias pendientes del paciente pasan a `DESCARTADO`.
- `asignacion_auditada(aprobado_hitl: bool, coordinador, justificacion: str = '')`: guarda `aprobado_hitl`, `psicologo_asignado_final` y `validado_por_coordinador`, y llama a `audit.services.log_event(accion='MATCHING_HITL_APROBADO' | 'MATCHING_REASIGNACION_MANUAL', usuario=coordinador.email, paciente_id, psicologo_sugerido_id, psicologo_final_id, justificacion)`. Esto es la “bitácora del sistema” del criterio c.
- Validaciones: si la sugerencia no está `PENDIENTE_VALIDACION`, responde 409 (doble clic). Si `psicologo_id` no coincide con el sugerido, responde 400. Si falta `motivo` o tiene menos de 10 caracteres, responde 400. Si el psicólogo manual no está activo, responde 400. Si el paciente ya tiene psicólogo, responde 409. Si el usuario no es coordinador ni admin, responde 403.

- [ ] **Step 1: Tests que fallan.**
  - Aprobar el top1 da 200, `paciente.psicologo_asignado == top1`, `top1.carga_actual` aumenta en 1, la sugerencia queda `APROBADO` con `aprobado_hitl True`, las otras quedan `DESCARTADO` y hay una línea `MATCHING_HITL_APROBADO` en `audit.services.read_events()`.
  - Aprobar otra vez la misma sugerencia da 409 y la carga no cambia.
  - Rechazar y reasignar con el psicólogo C y un motivo da 200, la sugerencia queda `RECHAZADO_MANUAL` con `psicologo_asignado_final == C` y `aprobado_hitl False`, la carga de C aumenta en 1 y la del sugerido no cambia.
  - Rechazar sin motivo da 400.
  - Un usuario paciente que intenta aprobar recibe 403.
- [ ] **Step 2:** Correr. Se espera: FAIL.
- [ ] **Step 3:** Implementar.
- [ ] **Step 4:** Correr las suites de Task 4 y Task 5 y `test_sprint3_matching.py`. Se espera: todo PASS.
- [ ] **Step 5:** Commit `feat(cu22): aprobación HITL y reasignación manual auditada en bitácora`.

---

### Task 6: Consola web de triaje y matching (UI_ConsolaTriajeIA + UI_ConsolaMatchingWeb)

**Files:**
- Modify: `web/src/app/core/services/triaje-ia.service.ts`
- Modify: `web/src/app/modules/triaje/consola-triage.component.ts` (398 líneas, componente standalone con template inline; se mantiene así)
- Modify: `web/src/app/layout/main-layout.component.ts` (badge de alertas para el criterio c, “notificación prioritaria inmediata”)

**Interfaces — Consumes:** los endpoints de las Tasks 3, 4 y 5. **Produces (service):**
- `clasificarTriaje(respuestaId: string): Observable<ClasificarTriajeResponse>` hace POST a `ia/clasificar-triaje/`
- `obtenerSugerencias(pacienteId: string): Observable<SugerenciasResponse>` hace GET a `matching/sugerencias/?paciente_id=`
- `aprobar(sugerenciaId: string, psicologoId: string)` hace POST a `matching/{id}/aprobar/`
- `rechazarYReasignar(sugerenciaId: string, psicologoManualId: string, motivo: string)` hace POST a `matching/{id}/rechazar_y_reasignar/`
- Se eliminan `generarMatching` y `asignarPsicologoHITL`. Antes, grep para confirmar que nadie más los usa.

Comportamiento (con nombres de método iguales a la clase de frontera del diagrama):
- `activar_banner_alerta_roja_prioritaria()` (mensaje 18): las tarjetas con `alerta_crisis` van arriba, con fondo rojo y banner “PROTOCOLO CRISIS”, y se muestra `sugerencia_inmediata`. `mostrar_tarjeta_triaje_ordinaria()` (mensaje 26): tarjeta normal con categoría, % de confianza, severidad y puntaje del 1 al 5.
- `seleccionar_emparejamiento(pacienteId)` (mensaje 1) → `mostrar_ranking_matching_IA(candidatos)` (mensaje 19): 3 tarjetas con el score y una barra por factor (`afinidad×0.4`, etc.) y la etiqueta “Cupo completo” cuando aplica.
- `confirmar_asignacion_IA()` (mensaje 20) → `mostrar_confirmacion_asignacion_ok()` (mensaje 29).
- `rechazar_y_reasignar_manual()` (mensaje 30): `<select>` con los psicólogos activos (reutiliza el servicio de psicólogos que ya existe en `core/services`) y un `<textarea>` de motivo obligatorio (mínimo 10 caracteres) → `mostrar_confirmacion_asignacion_manual()` (mensaje 39).
- Los botones se deshabilitan mientras la petición está en curso (complementa el 409 del backend).
- Notificación: `main-layout` consulta `triaje/alertas/` cada 30 s con `interval(30000)` y `switchMap` solo si el rol es coordinador/admin. Muestra un badge rojo con el número de alertas nuevas y un `Notification` del navegador si el permiso fue concedido.
- Texto de transparencia fijo bajo el ranking: “Sugerencia generada por IA. Requiere su confirmación; ningún paciente se asigna automáticamente.”

- [ ] **Step 1:** Implementar el service y el componente.
- [ ] **Step 2:** `cd web && npx ng build`. Se espera: build sin errores.
- [ ] **Step 3:** Prueba manual con `/run`. Login como coordinador, abrir la consola, clasificar un intake de crisis (debe salir el banner rojo y el badge en el layout), generar el Top 3, aprobar uno, y luego en otro paciente rechazar y reasignar. Verificar que en la bitácora aparecen los dos eventos.
- [ ] **Step 4:** Commit `feat(cu21-cu22): consola web de triaje IA y matching HITL`.

---

### Task 7: Seed de demostración y cierre

**Files:**
- Create: `backend/clinica/management/commands/seed_cu21_cu22.py` (mismo patrón que `agenda/management/commands/seed_cu12.py`)

- [ ] **Step 1:** El seed crea, en `centro_esperanza`, 3 intakes (crisis, pareja y duelo) y les pone `cupo_maximo`/`carga_actual` variados a los psicólogos del seed (uno saturado). Luego clasifica los intakes llamando a `CTR_ClasificacionIAController.clasificar`. Debe ser idempotente y usar la marca `[SEED CU21-22]`.
- [ ] **Step 2:** `venv/Scripts/python.exe manage.py seed_cu21_cu22` dos veces. Se espera: la misma cantidad de filas en ambas corridas.
- [ ] **Step 3:** Correr todas las suites: `test_sprint3_clasificacion_ia.py`, `test_sprint3_matching.py`, `test_cu21_cu22_modelos.py`, `test_cu21_clasificacion_api.py` y `test_cu22_matching_api.py`. Se espera: todo PASS.
- [ ] **Step 4:** Commit `chore(cu21-cu22): seed de demostración`.

---

## Desviaciones del diagrama que hay que decidir o corregir en Enterprise Architect

1. **`modelo='HF-ClinicalBert'`**: ClinicalBERT es un modelo en inglés y no clasifica estas categorías. Se usa `mDeBERTa-v3-base-mnli-xnli`, que también es de Hugging Face, y en la auditoría se registra **el id real del modelo** (escribir otro nombre falsearía la auditoría). Sugerencia: actualizar el diagrama a `modelo='HF-mDeBERTa-XNLI'`.
2. **Mensaje 9 `nivel='CRITICO'` y mensaje 17 `nivel:'ALTO'`**: el diagrama usa dos nombres para lo mismo. El plan implementa los dos al pie de la letra (`nivel_atencion='CRITICO'` en la BD y `nivel:'ALTO'` en el JSON), pero conviene unificarlos.
3. **Notificación prioritaria (HU-47 c)**: no aparece en la secuencia. Se implementa con polling y un badge web para el coordinador, porque los tokens FCM existentes son de pacientes, no de coordinadores.

---

## Resultado de la implementación (2026-11-05)

Decisiones tomadas al implementar (desvíos del plan, con su motivo):

- **Sin commits**: `clinica/models.py` y `main-layout.component.ts` ya tenían cambios sin commitear de CU11/CU12; un commit los habría mezclado. Todo quedó en el working tree.
- **torch 2.7.1** (no 2.15): 2.15 no se instala en Windows con la ruta larga del proyecto (WinError 206).
- **Sin `pipeline()` de transformers**: el zero-shot se implementó directo (`ClasificadorZeroShotNLI`) evaluando todas las hipótesis en un lote. Mismo resultado y **1.3 s por intake en lugar de 23 s**.
- **Sin `gunicorn --preload`**: con torch, el fork tras cargar el modelo puede colgar los workers. Cada worker precarga el modelo en segundo plano (`IA_PRECARGAR`, en `wsgi.py`). Costo: ~1.2 GB de RAM por worker.
- **Disponibilidad = bloques semanales / 40**: contar filas de horario no reflejaba las horas reales.
- **Riesgo por ML**: el zero-shot no separa crisis de casos normales (cualquier redacción que detecta 10/10 crisis marca 17-39/40 normales). Se mantuvo la hipótesis conservadora y la red de reglas garantiza recall 1.0.
- **Permisos**: el triaje y el matching quedaron solo para el coordinador o admin (antes cualquier usuario autenticado podía leer y borrar alertas de crisis).

Evaluación (`manage.py evaluar_modelo_ia`): categoría 38/50 (0.76), crisis 10/10, 4 falsos positivos. Los patrones nuevos se agregaron mirando este mismo set, así que la cifra es optimista: conviene ampliar el set con casos nuevos.
