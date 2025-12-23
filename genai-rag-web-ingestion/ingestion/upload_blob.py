import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()

AZURE_CONN_STR = os.getenv("AZURE_BLOB_CONNECTION")
CONTAINER_NAME = "raw-html"

# 🔹 Feature flag
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

def upload_text_to_blob(filename: str, text: str):
    if DRY_RUN:
        print("🟡 DRY RUN MODE ENABLED")
        print(f"Would upload file: {filename}")
        print(f"Text length: {len(text)} characters")
        return

    if not AZURE_CONN_STR:
        raise ValueError("AZURE_BLOB_CONNECTION environment variable is not set")

    blob_service = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
    container_client = blob_service.get_container_client(CONTAINER_NAME)

    try:
        container_client.create_container()
    except Exception:
        pass

    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(text, overwrite=True)

    print(f"✅ Uploaded to Blob Storage: {filename}")
