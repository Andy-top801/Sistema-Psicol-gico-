from rest_framework import serializers


class AuditEventSerializer(serializers.Serializer):
    timestamp = serializers.CharField(required=False, default="")
    ip = serializers.CharField(allow_null=True, required=False, default="")
    user_id = serializers.CharField(allow_null=True, required=False, default=None)
    user = serializers.CharField(required=False, default="anonymous")
    tenant = serializers.CharField(allow_null=True, required=False, default=None)
    method = serializers.CharField(required=False, default="INFO", allow_null=True)
    path = serializers.CharField(required=False, default="", allow_null=True)
    action = serializers.CharField(required=False, default="")
    status_code = serializers.IntegerField(required=False, default=200)
    error = serializers.CharField(allow_null=True, required=False, default=None)

