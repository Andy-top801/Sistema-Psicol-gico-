from rest_framework import serializers
from core.models import Centro

class CentroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Centro
        fields = [
            'id', 'nombre', 'direccion', 'telefono', 'email',
            'logo', 'horarios_atencion', 'configuracion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_actualizacion']
