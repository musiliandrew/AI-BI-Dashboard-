from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet, ApiIntegrationsViewSet, RegisterView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'api-integrations', ApiIntegrationsViewSet, basename='api-integrations')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]