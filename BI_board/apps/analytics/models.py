from django.db import models
from apps.data_ingestion.models import ProcessedData
from apps.users.models import Users

class AnalysisResults(models.Model):
    processed_data = models.ForeignKey('data_ingestion.ProcessedData', on_delete=models.CASCADE)
    efficiency = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    predicted_value = models.FloatField(null=True, blank=True)  # For sales forecast
    risk_score = models.FloatField(null=True, blank=True)  # For risk detection
    cluster_x = models.FloatField(null=True, blank=True)  # For clusters
    cluster_y = models.FloatField(null=True, blank=True)
    cluster_label = models.CharField(max_length=50, null=True, blank=True)
    factors = models.JSONField(null=True, blank=True)  # e.g., [{"name": "Marketing", "impact": 35}, ...]
    recommendations = models.JSONField(null=True, blank=True)  # e.g., ["Increase budget", ...]
    data_quality = models.FloatField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # In seconds

    class Meta:
        db_table = 'analysis_results'

class Dashboards(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True)
    dashboard_name = models.CharField(max_length=255)
    config = models.JSONField()  # e.g., {"chart_type": "bar", "data": "sales_forecast"}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dashboards'

class ScheduledReports(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True)
    report_name = models.CharField(max_length=255)
    cron_schedule = models.CharField(max_length=255)  # e.g., "0 0 * * *" (daily at midnight)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scheduled_reports'