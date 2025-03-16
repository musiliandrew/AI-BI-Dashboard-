import pandas as pd
from celery import shared_task
from .models import UploadedData, ProcessedData

@shared_task
def process_uploaded_file(uploaded_data_id):
    uploaded_data = UploadedData.objects.get(id=uploaded_data_id)
    file_path = uploaded_data.file.path
    
    print(f"📊 Processing file: {file_path}")

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        elif file_path.endswith(".json"):
            df = pd.read_json(file_path)
        else:
            print("❌ Unsupported file format")
            return None

        # Handle missing values with ffill() instead of fillna(method="ffill")
        df = df.ffill()

        # Convert categorical features
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col] = df[col].astype("category").cat.codes

        # Save processed data
        processed_json = df.to_json(orient="records")
        processed_data = ProcessedData.objects.create(
            uploaded_data=uploaded_data,
            processed_json=processed_json
        )

        # Mark as processed
        uploaded_data.processed = True
        uploaded_data.save()

        print(f"✅ File processed and saved: {file_path}")
        return processed_data.id

        
    except Exception as e:
        print(f"⚠ Error processing file: {e}")
        uploaded_data.processed = False
        uploaded_data.save()
        return None
