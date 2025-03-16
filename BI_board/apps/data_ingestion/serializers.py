from rest_framework import serializers
from .models import UploadedData, ProcessedData

class UploadedDataSerializer(serializers.ModelSerializer):
<<<<<<< Updated upstream
    class Meta:
        model = UploadedData
        fields = '__all__'
=======
    file_size = serializers.SerializerMethodField()
    file = serializers.FileField()  # Ensure file path is included

    class Meta:
        model = UploadedData
        fields = '__all__'

    def get_file_size(self, obj):
        return obj.file.size if obj.file else None
>>>>>>> Stashed changes

class ProcessedDataSerializer(serializers.ModelSerializer):
    uploaded_data = UploadedDataSerializer(read_only=True)  # Nest UploadedData details

    class Meta:
        model = ProcessedData
        fields = '__all__'
