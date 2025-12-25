import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import config
import loaders

def build_vectorstore():
    print("[INFO] Loading all documents...")
    docs = loaders.load_documents(config.DATA_DIR)
    print(f"[INFO] Loaded {len(docs)} documents")

    if not docs:
        print("[ERROR] No documents found.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(docs)
    print(f"[INFO] Created {len(chunks)} chunks")

    print("[INFO] Loading embedding model...")
    embedder = HuggingFaceEmbeddings(model_name=config.EMBED_MODEL)

    print("[INFO] Building FAISS index...")
    db = FAISS.from_documents(chunks, embedder)

    os.makedirs(config.VECTOR_DIR, exist_ok=True)
    db.save_local(config.VECTOR_DIR)

    print(f"[SUCCESS] Vectorstore saved to {config.VECTOR_DIR}")
