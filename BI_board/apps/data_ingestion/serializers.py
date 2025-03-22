from rest_framework import serializers
from .models import UploadedData, ProcessedData

class UploadedDataSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()
    file = serializers.FileField()  # Returns the file URL

    class Meta:
        model = UploadedData
        fields = ['id', 'user', 'file', 'file_type', 'file_size', 'uploaded_at', 'processed']
        read_only_fields = ['id', 'user', 'file_size', 'uploaded_at', 'processed']

    def get_file_size(self, obj):
        return obj.file.size if obj.file else None

class ProcessedDataSerializer(serializers.ModelSerializer):
    uploaded_data = UploadedDataSerializer(read_only=True)  # Nested UploadedData details

    class Meta:
        model = ProcessedData
        fields = ['id', 'uploaded_data', 'processed_json', 'processed_at']
        read_only_fields = ['id', 'uploaded_data', 'processed_json', 'processed_at']