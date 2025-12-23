import os
from dotenv import load_dotenv

load_dotenv()

# ---------------- ENV ----------------
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

BLOB_CONTAINER = os.getenv("BLOB_CONTAINER_NAME", "raw-html")
AZURE_BLOB_CONN = os.getenv("AZURE_BLOB_CONNECTION")

SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
SEARCH_INDEX = os.getenv("SEARCH_INDEX_NAME")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_EMBED_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# ---------------- DRY RUN ----------------
def run_dry_mode():
    print("🟡 DRY RUN MODE (Embedding)")
    fake_vector = [0.01] * 1536
    print("Simulated embedding length:", len(fake_vector))
    print("✅ Dry run successful")

# ---------------- REAL MODE ----------------
def run_real_mode():
    from azure.storage.blob import BlobServiceClient
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from openai import AzureOpenAI

    print("🟢 REAL MODE ENABLED")

    # Blob
    blob_service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONN)
    container_client = blob_service.get_container_client(BLOB_CONTAINER)

    # Search
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    # Azure OpenAI
    aoai = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )

    for blob in container_client.list_blobs():
        print(f"📥 Reading blob: {blob.name}")
        content = container_client.download_blob(blob.name).readall().decode("utf-8")

        embedding = aoai.embeddings.create(
            model=AZURE_OPENAI_EMBED_DEPLOYMENT,  # DEPLOYMENT NAME
            input=content
        ).data[0].embedding
        safe_id = blob.name.replace(".", "_").replace("/", "_")
        doc = {
            "id": safe_id,
            "content": content,
            "embedding": embedding
        }

        search_client.upload_documents([doc])
        print(f"✅ Indexed: {blob.name}")

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    if DRY_RUN:
        run_dry_mode()
    else:
        run_real_mode()
