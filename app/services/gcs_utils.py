import logging
from google.cloud import storage
import asyncio 
from google.api_core import exceptions
from app.config import settings

# This automatically finds and uses the GOOGLE_APPLICATION_CREDENTIALS env var
try:
    storage_client = storage.Client()
except Exception as e:
    logging.error(f"FATAL: Could not initialize Google Cloud Storage client. Is the credential file valid? Error: {e}")
    storage_client = None

def upload_to_gcs(local_file_path: str, destination_blob_name: str) -> bool:

    # Uploads a file to the configured GCS bucket and returns True on success.
    # The destination_blob_name is the path/name of the file in the bucket.
    if not storage_client or not settings.GCS_BUCKET_NAME:
        logging.warning("GCS client or bucket name not configured. Skipping upload.")
        return False
        
    try:
        bucket = storage_client.bucket(settings.GCS_BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        
        logging.info(f"Attempting to upload {local_file_path} to gs://{settings.GCS_BUCKET_NAME}/{destination_blob_name}")
        blob.upload_from_filename(local_file_path)
        
        logging.info("Upload successful.")
        return True
    except FileNotFoundError:
        logging.error(f"Local file not found for upload: {local_file_path}")
        return False
    except exceptions.GoogleAPICallError as e:
        logging.error(f"Failed to upload {local_file_path} to GCS. API Error: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during GCS upload: {e}")
        return False
    

async def upload_to_gcs_async(local_file_path: str, destination_blob_name: str) -> bool:
    # Asynchronously uploads a file to GCS by running the blocking upload function in a separate thread.
    # asyncio.to_thread tells the event loop to run the given function (upload_to_gcs)in a separate thread from the default thread pool, and to await the result
    # This prevents the main application from blocking.
    return await asyncio.to_thread(upload_to_gcs, local_file_path, destination_blob_name)