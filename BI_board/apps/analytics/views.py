from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AnalysisResults, Dashboards, ScheduledReports
from .serializers import AnalysisResultsSerializer, DashboardsSerializer, ScheduledReportsSerializer
from .tasks import run_analytics
from apps.data_ingestion.models import ProcessedData
import logging

logger = logging.getLogger(__name__)
class AnalyzeDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Request data: {request.data}")
        processed_data_id = request.data.get('processed_data_id')
        if not processed_data_id:
            logger.warning("processed_data_id missing in request")
            return Response({'error': 'processed_data_id required'}, status=400)
        
        task_result = run_analytics.delay(processed_data_id)
        return Response({'task_id': task_result.id, 'message': 'Analysis started'})

class AnalysisResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = AnalysisResults.objects.filter(processed_data__uploaded_data__user=request.user)
        serializer = AnalysisResultsSerializer(results, many=True)
        return Response(serializer.data)

class DashboardsViewSet(viewsets.ModelViewSet):
    queryset = Dashboards.objects.all()
    serializer_class = DashboardsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dashboards.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ScheduledReportsViewSet(viewsets.ModelViewSet):
    queryset = ScheduledReports.objects.all()
    serializer_class = ScheduledReportsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScheduledReports.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)