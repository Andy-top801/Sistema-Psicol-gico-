from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django_tenants.test.cases import TenantTestCase
from tenants.models import Tenant
from clinica.models import ConsentimientoInformado, FirmaConsentimiento, Paciente
from accounts.models import Rol

Usuario = get_user_model()


class ConsentimientosTestCase(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.nombre = 'Test Centro'
        tenant.slug = 'test-centro'
        tenant.email_contacto = 'test@test.com'
        return tenant

    def setUp(self):
        super().setUp()
        self.rol, _ = Rol.objects.get_or_create(nombre='Admin Centro')
        self.user = Usuario.objects.create_user(
            email='admin@test.com', password='testpass123',
            nombre='Admin', apellido='Test', rol=self.rol, activo=True
        )
        self.client = APIClient(HTTP_HOST=self.tenant.get_primary_domain().domain)
        self.client.force_authenticate(user=self.user)
        self.paciente = Paciente.objects.create(
            usuario=self.user, codigo_expediente='EXP-TEST-001',
            ci='12345678', fecha_nacimiento='1990-01-01', genero='M',
        )

    def test_crear_plantilla(self):
        url = '/api/clinica/consentimientos-plantillas/'
        payload = {
            "codigo_plantilla": "CI-TEST-001",
            "cuerpo_plantilla": "Contenido del consentimiento",
            "titulo": "Test Consentimiento"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_actualizar_plantilla_patch(self):
        plantilla = ConsentimientoInformado.objects.create(
            titulo='Test', tipo='TEST', contenido_legal='Contenido', version='1.0', activo=True
        )
        url = f'/api/clinica/consentimientos-plantillas/{plantilla.id}/'
        response = self.client.patch(url, {'activo': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_eliminar_plantilla(self):
        plantilla = ConsentimientoInformado.objects.create(
            titulo='Test', tipo='TEST', contenido_legal='Contenido', version='1.0', activo=True
        )
        url = f'/api/clinica/consentimientos-plantillas/{plantilla.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_firmar_consentimiento_hash_autocalculado(self):
        plantilla = ConsentimientoInformado.objects.create(
            titulo='Test', tipo='TEST', contenido_legal='Contenido', version='1.0', activo=True
        )
        url = '/api/clinica/consentimientos-firmas/'
        payload = {
            "plantilla": str(plantilla.id),
            "paciente": str(self.paciente.id),
            "contenido_final_renderizado": "test",
            "firma_imagen": "data:image/png;base64,abc"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_revocar_firma(self):
        plantilla = ConsentimientoInformado.objects.create(
            titulo='Test', tipo='TEST', contenido_legal='Contenido', version='1.0', activo=True
        )
        firma = FirmaConsentimiento.objects.create(
            consentimiento=plantilla, paciente=self.paciente, firmado_por='Test'
        )
        url = f'/api/clinica/consentimientos-firmas/{firma.id}/revocar/'
        response = self.client.post(url, {'motivo': 'Retiro'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_descargar_pdf(self):
        plantilla = ConsentimientoInformado.objects.create(
            titulo='Test', tipo='TEST', contenido_legal='Contenido', version='1.0', activo=True
        )
        firma = FirmaConsentimiento.objects.create(
            consentimiento=plantilla, paciente=self.paciente, firmado_por='Test'
        )
        url = f'/api/clinica/consentimientos-firmas/{firma.id}/descargar_pdf/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('application/pdf', response['Content-Type'])

    def test_firmar_sin_plantilla_falla(self):
        url = '/api/clinica/consentimientos-firmas/'
        payload = {"paciente": str(self.paciente.id), "contenido_final_renderizado": "test"}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_revocar_sin_motivo_falla(self):
        plantilla = ConsentimientoInformado.objects.create(
            titulo='Test', tipo='TEST', contenido_legal='Contenido', version='1.0', activo=True
        )
        firma = FirmaConsentimiento.objects.create(
            consentimiento=plantilla, paciente=self.paciente, firmado_por='Test'
        )
        url = f'/api/clinica/consentimientos-firmas/{firma.id}/revocar/'
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
