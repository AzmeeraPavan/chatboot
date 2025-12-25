from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever

import config

def load_vectorstore():
    embedder = HuggingFaceEmbeddings(model_name=config.EMBED_MODEL)
    return FAISS.load_local(config.VECTOR_DIR, embedder, allow_dangerous_deserialization=True)

def hybrid_search(query: str, top_k=config.TOP_K):
    try:
        db = load_vectorstore()
    except Exception as e:
        print("[ERROR] Vectorstore not found. Run: python main.py build")
        print("Error:", e)
        return []

    # Semantic
    emb_docs = db.similarity_search(query, k=top_k)

    # Keyword BM25
    all_docs = list(db.docstore._dict.values())
    bm25 = BM25Retriever.from_documents(all_docs)
    bm25.k = top_k
    bm_docs = bm25.invoke(query)

    # Exact Match
    exact_docs = [d for d in all_docs if query.lower() in d.page_content.lower()]

    # Merge = Exact > Embedding > BM25
    merged = exact_docs + emb_docs + bm_docs

    final, seen = [], set()
    for d in merged:
        key = (d.metadata.get("source"), d.page_content[:40])
        if key not in seen:
            final.append(d)
            seen.add(key)
        if len(final) >= top_k:
            break

    return final
