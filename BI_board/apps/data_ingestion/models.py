from django.db import models
from apps.users.models import Users

class UploadedData(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to='uploads/',  default='default_file.txt')  # Now using FileField instead of file_path
    file_type = models.CharField(max_length=10, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        db_table = 'uploaded_data'

class ProcessedData(models.Model):
    uploaded_data = models.ForeignKey(UploadedData, on_delete=models.CASCADE, blank=True, null=True)
    processed_json = models.JSONField()
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processed_data'
