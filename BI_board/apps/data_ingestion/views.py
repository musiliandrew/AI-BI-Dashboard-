from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from .models import UploadedData, ProcessedData
from .serializers import UploadedDataSerializer, ProcessedDataSerializer
from .processing import process_uploaded_file
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.core.files.base import ContentFile
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

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
            user=request.user,
            file=file_obj,
            file_type=file_name.split('.')[-1].lower(),  # e.g., 'csv', 'xlsx', 'json'
            file_size=file_obj.size  # Optional: track file size
        )
        uploaded_data.save()
        logger.info(f"File uploaded by {request.user.id}: {file_name}, ID: {uploaded_data.id}")

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
        logger.info(f"API data synced by {request.user.id}, ID: {uploaded_data.id}")

        # Trigger processing
        task_result = process_uploaded_file.delay(uploaded_data.id)
        return Response({
            "message": "API data received and queued for processing.",
            "task_id": task_result.id,
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
            logger.info(f"Google Sheet synced by {request.user.id}, ID: {uploaded_data.id}")

            # Trigger processing
            task_result = process_uploaded_file.delay(uploaded_data.id)
            return Response({
                "message": "Google Sheet data synced and processing.",
                "task_id": task_result.id,
                "file_id": uploaded_data.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Google Sheet sync failed for {request.user.id}: {str(e)}")
            return Response({"error": f"Failed to sync Google Sheet: {str(e)}"}, 
                           status=status.HTTP_400_BAD_REQUEST)