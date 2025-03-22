from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Users, ApiIntegrations
from .serializers import UsersSerializer, ApiIntegrationsSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers



class RegisterView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Custom serializer to use email instead of username
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email  # Optional: Add email to token payload
        token['role'] = user.role
        return token

    def validate(self, attrs):
        # Replace username with email in validation
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }
        if not credentials['email'] or not credentials['password']:
            raise serializers.ValidationError('Email and password are required.')

        user = authenticate(**credentials)
        if user is None:
            raise serializers.ValidationError('Invalid email or password.')

        data = super().validate(attrs)
        data['user'] = {'id': user.id, 'email': user.email, 'role': user.role}
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

class ApiIntegrationsViewSet(viewsets.ModelViewSet):
    queryset = ApiIntegrations.objects.all()
    serializer_class = ApiIntegrationsSerializer
    permission_classes = [IsAuthenticated]
    
class UserSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UsersSerializer(user)
        # Add settings fields if stored separately
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        data = request.data
        # Update user fields or a separate settings model
        user.email = data.get('notificationEmail', user.email)
        user.save()
        # Handle additional settings (e.g., apiKey, dataRetention) in a settings model if needed
        return Response({"message": "Settings updated"}, status=200)
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UsersSerializer(request.user)
        return Response(serializer.data)