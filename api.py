from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
from file_watcher import start_watching
import indexing
import retrieval
import generation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # your React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def start_background_watch():
    thread = threading.Thread(target=start_watching, args=("C:/Users/azmee/rowdata",), daemon=True)
    thread.start()
    print("🔥 Auto Chunk + Index updater activated")

# ----------------- Models -----------------
class QueryPayload(BaseModel):
    query: str
    engine: str = "llama"

# ----------------- Endpoints -----------------
@app.get("/")
def home():
    return {"status": "Backend running"}

@app.post("/build")
def build_index():
    indexing.build_vectorstore()
    return {"message": "Index built successfully"}

@app.post("/retrieve")
def retrieve(payload: QueryPayload):
    docs = retrieval.hybrid_search(payload.query)
    return {"documents": [d.page_content for d in docs]}

@app.post("/answer")
def answer(payload: QueryPayload):
    docs = retrieval.hybrid_search(payload.query)
    if not docs:
        return {"answer": "No relevant documents found"}

    context = "\n\n".join(d.page_content for d in docs)

    if payload.engine == "hf":
        ans = generation.generate_with_hf(context, payload.query)
    else:
        ans = generation.generate_with_llama(context, payload.query)

    return {"answer": ans}