from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Users, ApiIntegrations
from .serializers import UsersSerializer, ApiIntegrationsSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

class RegisterView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Custom login view (extends JWT's TokenObtainPairView)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass  # We’re using the default for now, but you can customize later

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

class ApiIntegrationsViewSet(viewsets.ModelViewSet):
    queryset = ApiIntegrations.objects.all()
    serializer_class = ApiIntegrationsSerializer
    permission_classes = [IsAuthenticated]