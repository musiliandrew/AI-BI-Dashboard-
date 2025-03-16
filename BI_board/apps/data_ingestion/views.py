from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UploadedData, ProcessedData
from .serializers import UploadedDataSerializer, ProcessedDataSerializer
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.core.files.base import ContentFile
from rest_framework.parsers import MultiPartParser
from .processing import process_uploaded_file
import pandas as pd
import json

class FileUploadView(APIView):
<<<<<<< Updated upstream
    permission_classes = [IsAuthenticated]  # Only logged-in users can upload
    parser_classes = [MultiPartParser]
=======
    permission_classes = [IsAuthenticated]
>>>>>>> Stashed changes

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file_name = file_obj.name
        if not file_name.endswith(('.csv', '.xlsx', '.json')):
            return Response({"error": "Unsupported file format. Use CSV, Excel, or JSON."}, 
                           status=status.HTTP_400_BAD_REQUEST)

        # Save the uploaded file
        uploaded_data = UploadedData(
            user=request.user,  # Tie to the authenticated user
            file=file_obj,
<<<<<<< Updated upstream
            file_type=file_name.split('.')[-1]  # e.g., 'csv', 'xlsx', 'json'
=======
            file_type=file_name.split('.')[-1]
>>>>>>> Stashed changes
        )
        uploaded_data.save()

        # Run processing asynchronously
        task_result = process_uploaded_file.delay(uploaded_data.id)
        return Response({
            "message": "File uploaded successfully. Processing started.",
            "task_id": task_result.id,
            "uploaded_data_id": uploaded_data.id
        }, status=status.HTTP_202_ACCEPTED)

class UploadedDataViewSet(viewsets.ModelViewSet):
    queryset = UploadedData.objects.all()
    serializer_class = UploadedDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show data uploaded by the current user
        return UploadedData.objects.filter(user=self.request.user)

class ProcessedDataViewSet(viewsets.ModelViewSet):
    queryset = ProcessedData.objects.all()
    serializer_class = ProcessedDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProcessedData.objects.filter(uploaded_data__user=self.request.user)
    

class ApiDataSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.get('data')
        if not data or not isinstance(data, (dict, list)):
            return Response({"error": "Invalid data format. Send JSON as dict or list."}, 
                           status=status.HTTP_400_BAD_REQUEST)

        # Simulate file-like storage for processing
        uploaded_data = UploadedData(
            user=request.user,
            file_type='json',
            processed=False
        )
        uploaded_data.file.save('api_sync.json', ContentFile(json.dumps(data).encode()))
        uploaded_data.save()

        # Trigger processing
        process_uploaded_file.delay(uploaded_data.id)

        return Response({
            "message": "API data received and queued for processing.",
            "file_id": uploaded_data.id
        }, status=status.HTTP_201_CREATED)
        
class GoogleSheetsSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sheet_url = request.data.get('sheet_url')
        if not sheet_url:
            return Response({"error": "No sheet URL provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Authenticate with Google Sheets
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('BI_board/credentials.json', scope)
            client = gspread.authorize(creds)

            # Open the sheet and get data
            sheet = client.open_by_url(sheet_url).sheet1
            data = sheet.get_all_records()

            # Save as JSON
            uploaded_data = UploadedData(
                user=request.user,
                file_type='json'
            )
            uploaded_data.file.save(f'gsheet_{sheet_url.split("/")[-2]}.json', 
                                  ContentFile(json.dumps(data).encode()))
            uploaded_data.save()

            process_uploaded_file.delay(uploaded_data.id)
            return Response({"message": "Google Sheet data synced and processing.", "file_id": uploaded_data.id}, 
                           status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Failed to sync Google Sheet: {str(e)}"}, 
                           status=status.HTTP_400_BAD_REQUEST)