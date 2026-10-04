# ==============================================================================
# MÓDULO: clinica/validators.py
# CAPA: SERVICIOS Y REGLAS DE NEGOCIO / VALIDACIÓN DINÁMICA JSONB
# CASOS DE USO: CU14 (Intake Digital y Formulario Pre-Consulta)
# HISTORIAS DE USUARIO: HU-23, HU-24
# RESPONSABLE: Andy Mauricio Mújica Vallejos (Backend Lead)
# DESCRIPCIÓN: Validador de esquemas dinámicos JSONB de preguntas y comprobación
#              cruzada de consistencia de respuestas enviadas por pacientes.
# ==============================================================================
import re
from rest_framework.exceptions import ValidationError

TIPOS_PREGUNTA_VALIDOS = {'texto', 'escala_1_5', 'booleano', 'opcion_multiple', 'likert'}


def validar_esquema_preguntas(preguntas):
    """
    Valida la estructura formal del esquema JSONB de preguntas definido en FormularioPreConsulta.
    Reglas:
      1. Debe ser una lista no vacía.
      2. Cada elemento debe ser un diccionario con 'id', 'texto', 'tipo' y 'requerido'.
      3. 'id' debe ser único, alfanumérico y no vacío.
      4. 'tipo' debe pertenecer a TIPOS_PREGUNTA_VALIDOS.
      5. Si 'tipo' es 'opcion_multiple' o 'likert', 'opciones' debe ser una lista de al menos 2 elementos no vacíos.
    """
    if not isinstance(preguntas, list):
        raise ValidationError({"preguntas_schema": "El esquema de preguntas debe ser una lista de campos JSON."})

    if len(preguntas) == 0:
        raise ValidationError({"preguntas_schema": "El formulario debe contener al menos una pregunta clínica."})

    ids_vistos = set()

    for idx, item in enumerate(preguntas):
        if not isinstance(item, dict):
            raise ValidationError({
                "preguntas_schema": f"La pregunta en el índice {idx} debe ser un objeto JSON (clave-valor)."
            })

        # Validar ID
        q_id = item.get('id')
        if not q_id or not isinstance(q_id, str) or not q_id.strip():
            raise ValidationError({
                "preguntas_schema": f"La pregunta en el índice {idx} carece de un identificador 'id' válido y no vacío."
            })
        q_id = q_id.strip()
        if not re.match(r'^[a-zA-Z0-9_\-]+$', q_id):
            raise ValidationError({
                "preguntas_schema": f"El ID '{q_id}' en el índice {idx} contiene caracteres no permitidos. Use solo letras, números, guiones y guiones bajos."
            })
        if q_id in ids_vistos:
            raise ValidationError({
                "preguntas_schema": f"El identificador de pregunta '{q_id}' está duplicado en el esquema."
            })
        ids_vistos.add(q_id)

        # Validar Texto
        texto = item.get('texto')
        if not texto or not isinstance(texto, str) or not texto.strip():
            raise ValidationError({
                "preguntas_schema": f"La pregunta '{q_id}' en el índice {idx} debe incluir el texto o enunciado clínico."
            })

        # Validar Tipo
        tipo = item.get('tipo')
        if not tipo or tipo not in TIPOS_PREGUNTA_VALIDOS:
            raise ValidationError({
                "preguntas_schema": (
                    f"El tipo '{tipo}' en la pregunta '{q_id}' no es válido. "
                    f"Tipos permitidos: {', '.join(sorted(TIPOS_PREGUNTA_VALIDOS))}."
                )
            })

        # Validar Requerido
        requerido = item.get('requerido')
        if not isinstance(requerido, bool):
            raise ValidationError({
                "preguntas_schema": f"El campo 'requerido' en la pregunta '{q_id}' debe ser booleano (true o false)."
            })

        # Validar Opciones en preguntas de selección
        if tipo in ('opcion_multiple', 'likert'):
            opciones = item.get('opciones')
            if not isinstance(opciones, list) or len(opciones) < 2:
                raise ValidationError({
                    "preguntas_schema": (
                        f"La pregunta '{q_id}' de tipo '{tipo}' debe incluir una lista 'opciones' "
                        f"con al menos 2 alternativas."
                    )
                })
            for opt_idx, opt in enumerate(opciones):
                if not isinstance(opt, str) or not opt.strip():
                    raise ValidationError({
                        "preguntas_schema": (
                            f"La opción {opt_idx} de la pregunta '{q_id}' no puede estar vacía."
                        )
                    })

    return preguntas


def validar_respuestas_contra_esquema(formulario, respuestas_detalle):
    """
    Verifica que las respuestas enviadas por el paciente satisfagan el esquema
    definido en el FormularioPreConsulta asociado.
    Reglas:
      1. 'respuestas_detalle' debe ser un diccionario.
      2. Preguntas con requerido=True deben tener un valor no nulo ni vacío.
      3. Tipos de datos deben corresponder estrictamente al tipo definido:
         - 'texto': str
         - 'escala_1_5': int entre 1 y 5
         - 'booleano': bool
         - 'opcion_multiple' / 'likert': valor contenido en la lista de opciones
    """
    if not isinstance(respuestas_detalle, dict):
        raise ValidationError({"respuestas_detalle": "El detalle de respuestas debe ser un objeto JSON (diccionario)."})

    preguntas_schema = getattr(formulario, 'preguntas_schema', None)
    if not preguntas_schema or not isinstance(preguntas_schema, list):
        return respuestas_detalle

    errores = {}

    for q in preguntas_schema:
        q_id = q.get('id')
        q_texto = q.get('texto', q_id)
        q_tipo = q.get('tipo')
        q_requerido = q.get('requerido', False)

        val = respuestas_detalle.get(q_id)

        # Validación de obligatoriedad
        if q_requerido:
            if val is None or (isinstance(val, str) and not val.strip()):
                errores[q_id] = f"La pregunta '{q_texto}' es obligatoria."
                continue

        # Validación de tipo de dato si se proveyó un valor
        if val is not None and val != "":
            if q_tipo == 'texto':
                if not isinstance(val, str):
                    errores[q_id] = f"La respuesta a '{q_texto}' debe ser texto."

            elif q_tipo == 'escala_1_5':
                try:
                    num_val = int(val)
                    if num_val < 1 or num_val > 5:
                        errores[q_id] = f"La escala para '{q_texto}' debe ser un valor entero entre 1 y 5."
                except (ValueError, TypeError):
                    errores[q_id] = f"La respuesta a '{q_texto}' debe ser un número entero entre 1 y 5."

            elif q_tipo == 'booleano':
                if not isinstance(val, bool):
                    errores[q_id] = f"La respuesta a '{q_texto}' debe ser verdadero o falso (booleano)."

            elif q_tipo in ('opcion_multiple', 'likert'):
                opciones_validas = q.get('opciones', [])
                if str(val) not in [str(opt) for opt in opciones_validas]:
                    errores[q_id] = (
                        f"Opción inválida para '{q_texto}'. "
                        f"Opciones aceptadas: {', '.join(opciones_validas)}."
                    )

    if errores:
        raise ValidationError({"respuestas_detalle": errores})

    return respuestas_detalle
