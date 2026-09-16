from rest_framework import serializers


class AuditEventSerializer(serializers.Serializer):
    timestamp = serializers.CharField()
    ip = serializers.CharField(allow_null=True)
    user_id = serializers.CharField(allow_null=True)
    user = serializers.CharField()
    tenant = serializers.CharField(allow_null=True)
    method = serializers.CharField()
    path = serializers.CharField()
    action = serializers.CharField()
    status_code = serializers.IntegerField()
    error = serializers.CharField(allow_null=True)
