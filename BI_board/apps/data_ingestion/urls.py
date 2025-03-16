from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UploadedDataViewSet, ProcessedDataViewSet, FileUploadView, ApiDataSyncView, GoogleSheetsSyncView

router = DefaultRouter()
router.register(r'uploaded-data', UploadedDataViewSet, basename='uploaded-data')
router.register(r'processed-data', ProcessedDataViewSet, basename='processed-data')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('api-sync/', ApiDataSyncView.as_view(), name='api-sync'),
    path('google-sheets-sync/', GoogleSheetsSyncView.as_view(), name='google-sheets-sync'),
]