from rest_framework import serializers
from .models import AnalysisResults, Dashboards, ScheduledReports

class AnalysisResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResults
        fields = '__all__'

class DashboardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboards
        fields = '__all__'

class ScheduledReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledReports
        fields = '__all__'
