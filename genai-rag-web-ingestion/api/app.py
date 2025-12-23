import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

# Azure SDK
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from azure.search.documents.models import VectorizedQuery
load_dotenv()

# ---------------- ENV ----------------
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
SEARCH_INDEX = os.getenv("SEARCH_INDEX_NAME")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
CHAT_MODEL = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_EMBED_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")

app = FastAPI(title="GenAI RAG API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- REQUEST MODEL ----------------
class Question(BaseModel):
    question: str

# ---------------- DRY RUN MOCK DATA ----------------
MOCK_CONTEXT = [
    "Azure Kubernetes Service is a managed Kubernetes offering.",
    "Azure Blob Storage stores unstructured data.",
    "Azure AI Search enables vector-based semantic search."
]

# ---------------- DRY RUN MODE ----------------
def answer_dry_run(question: str) -> str:
    print("🟡 DRY RUN MODE ENABLED (API)")
    context = "\n".join(MOCK_CONTEXT)
    return (
        "This is a DRY RUN response.\n\n"
        f"Question: {question}\n\n"
        f"Context used:\n{context}"
    )

# ---------------- REAL MODE ----------------
def answer_real(question: str) -> str:
    # 1️⃣ Initialize Azure OpenAI client
    aoai_client = AzureOpenAI(
        # api_type="azure",
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version="2023-07-01-preview"
      # Add this line
)


    # 2️⃣ Initialize Azure Cognitive Search client
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    # 3️⃣ Generate embedding for the question
    embedding_resp = aoai_client.embeddings.create(
        model=AZURE_OPENAI_EMBED_DEPLOYMENT,
        input=question
    )
    question_embedding = embedding_resp.data[0].embedding

    # 4️⃣ Vector search in Azure Search
    results = search_client.search(
        search_text=None,
        vector_queries=[
            VectorizedQuery(
                vector=question_embedding, 
                k_nearest_neighbors=3, 
                fields="embedding"
    )]
    )

    # 5️⃣ Prepare context
    context = "\n".join([doc["content"] for doc in results])

    # 6️⃣ LLM completion
    response = aoai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Answer only using the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )

    return response.choices[0].message["content"]

# ---------------- API ENDPOINT ----------------
@app.post("/chat")
def chat(req: Question):
    if DRY_RUN:
        return {"answer": answer_dry_run(req.question)}
    else:
        return {"answer": answer_real(req.question)}
