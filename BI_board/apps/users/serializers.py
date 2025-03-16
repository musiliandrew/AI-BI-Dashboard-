from rest_framework import serializers
from .models import Users, ApiIntegrations

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'password', 'role', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = Users(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'user'),
        )
        user.set_password(validated_data['password']) 
        user.save()
        return user

class ApiIntegrationsSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Users.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = ApiIntegrations
        fields = ['id', 'user', 'user_id', 'api_name', 'api_key', 'created_at']