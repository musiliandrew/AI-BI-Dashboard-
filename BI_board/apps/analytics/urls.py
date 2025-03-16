# apps/analytics/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyzeDataView, AnalysisResultsView, DashboardsViewSet, ScheduledReportsViewSet

router = DefaultRouter()
router.register(r'dashboards', DashboardsViewSet, basename='dashboards')
router.register(r'scheduled-reports', ScheduledReportsViewSet, basename='scheduled-reports')

urlpatterns = [
    path('', include(router.urls)),
    path('analyze/', AnalyzeDataView.as_view(), name='analyze-data'),
    path('analysis-results/', AnalysisResultsView.as_view(), name='analysis-results'),
]