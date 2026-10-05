# HU-31: Consentimientos Informados Digitales

## Descripción
Sistema de gestión de consentimientos informados digitales para centros psicológicos. Permite crear plantillas legales con variables dinámicas, que los pacientes firman digitalmente con validez criptográfica (SHA-256).

## Casos de Uso Cubiertos
- CU18: Configuración y emisión de consentimientos informados (HU-31 + HU-32)

## Endpoints Implementados

### Plantillas
- GET    /api/clinica/consentimientos-plantillas/         → Listar
- POST   /api/clinica/consentimientos-plantillas/         → Crear
- PATCH  /api/clinica/consentimientos-plantillas/{id}/    → Actualizar
- DELETE /api/clinica/consentimientos-plantillas/{id}/    → Eliminar

### Firmas
- GET    /api/clinica/consentimientos-firmas/             → Listar
- POST   /api/clinica/consentimientos-firmas/             → Firmar
- POST   /api/clinica/consentimientos-firmas/{id}/revocar/ → Revocar
- GET    /api/clinica/consentimientos-firmas/{id}/descargar_pdf/ → PDF

## Flujo de Uso
1. Psicólogo crea plantilla con variables dinámicas ({PACIENTE_NOMBRE}, etc.)
2. Sistema almacena la plantilla cifrada/persistida
3. Paciente firma desde web con canvas táctil
4. Sistema calcula hash SHA-256 del contenido + firma + timestamp
5. Se genera PDF con la firma visual y sello criptográfico
6. Psicólogo puede revocar firmas indicando motivo

## Criterios de Aceptación Cumplidos
- [x] Crear/editar/eliminar plantillas de consentimiento
- [x] Firma digital con canvas táctil
- [x] Hash SHA-256 autocalculado al firmar
- [x] PDF descargable con firma visible
- [x] Revocación con motivo obligatorio
- [x] Trazabilidad (IP, user agent, timestamp, dispositivo)
- [x] UI con tipo legible y badges de estado
- [x] Multi-tenant (funciona en centro_esperanza y mentesana)

## Notas Técnicas
- Alias frontend ↔ backend: codigo_plantilla ↔ tipo, cuerpo_plantilla ↔ contenido_legal
- Hash SHA-256 calculado en FirmaConsentimiento.save() para robustez
- Validación de PATCH respeta partial=True (no exige campos requeridos en update)
- Serializer maneja aliases (plantilla → consentimiento, firma_imagen → firma_canvas_url)
- PDF generado con reportlab en el backend

## Estructura de Archivos Modificados
Backend:
- prototipo/backend/clinica/models.py (FirmaConsentimiento.save() + campos revocación)
- prototipo/backend/clinica/serializers.py (aliases + partial)
- prototipo/backend/clinica/views.py (descargar_pdf, revocar)
- prototipo/backend/clinica/migrations/0005_*.py

Frontend:
- prototipo/web/src/app/modules/consentimientos/consentimientos-hub.component.ts
- prototipo/web/src/app/core/services/clinica-sprint2.service.ts
- prototipo/web/src/app/core/models/clinica-sprint2.model.ts

## Instrucciones para Probar

### Desde el navegador
1. Login: carlos.mendoza@centroesperanza.com / Psicologo123*
2. Ir a http://localhost:4200/consentimientos
3. Crear plantilla nueva
4. Firmar consentimiento
5. Descargar PDF
6. Revocar firma

## Estado
✅ HU-31 completada y verificada
Fecha: Octubre 2026
