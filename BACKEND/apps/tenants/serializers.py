from rest_framework import serializers
from .models import Centro, Dominio

class DominioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dominio
        fields = ['id', 'domain', 'is_primary']

class CentroSerializer(serializers.ModelSerializer):
    domains = DominioSerializer(many=True, read_only=True)
    domain_url = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Centro
        fields = ['id', 'name', 'schema_name', 'is_active', 'created_at', 'domains', 'domain_url']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        domain_url = validated_data.pop('domain_url', None)
        # Create the tenant (this automatically creates the PostgreSQL schema)
        tenant = Centro.objects.create(**validated_data)
        
        if domain_url:
            Dominio.objects.create(
                domain=domain_url,
                tenant=tenant,
                is_primary=True
            )
        return tenant
