import time
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

UPLOAD_URL = "http://127.0.0.1:8000/data-ingestion/upload"  
WATCHED_FOLDER = "/media/"

class FileUploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        print(f"New file detected: {file_path}")
        self.upload_file(file_path)

    def upload_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(UPLOAD_URL, files={'file': f})
            if response.status_code == 201:
                print(f"✅ Successfully uploaded: {file_path}")
            else:
                print(f"❌ Upload failed: {response.text}")
        except Exception as e:
            print(f"⚠ Error uploading file: {e}")

if __name__ == "__main__":
    event_handler = FileUploadHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCHED_FOLDER, recursive=False)
    observer.start()
    
    print(f"📂 Watching directory: {WATCHED_FOLDER}")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
