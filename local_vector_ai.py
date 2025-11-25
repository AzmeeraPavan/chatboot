# import os
# import sys
# import json
# from pathlib import Path
# from typing import List, Dict, Tuple
#
# import pandas as pd
# from sentence_transformers import SentenceTransformer
# import numpy as np
# import faiss
#
# from pypdf import PdfReader
# import docx
#
# # =============================
# # CONFIG (Your Paths)
# # =============================
# DATA_DIR = r"C:\Users\PavanAzmeeraSIDGloba\rowdata"
# VECTOR_STORE_DIR = r"C:\vectorData"
#
# EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
# EMBED_DIM = 384
# K_NEIGHBORS = 5
#
# # =============================
# # File Readers
# # =============================
# def read_txt(path: Path) -> str:
#     return path.read_text(encoding="utf-8", errors="ignore")
#
# def read_csv(path: Path) -> str:
#     try:
#         df = pd.read_csv(path, dtype=str, keep_default_na=False)
#         return df.to_string(index=False)
#     except Exception:
#         return path.read_text(errors="ignore")
#
# def read_xlsx(path: Path) -> str:
#     try:
#         df = pd.read_excel(path, dtype=str)
#         return df.to_string(index=False)
#     except Exception:
#         return path.read_text(errors="ignore")
#
# def read_pdf(path: Path) -> str:
#     try:
#         reader = PdfReader(str(path))
#         text = []
#         for p in reader.pages:
#             text.append(p.extract_text() or "")
#         return "\n".join(text)
#     except:
#         return ""
#
# def read_docx(path: Path) -> str:
#     try:
#         doc = docx.Document(str(path))
#         return "\n".join([p.text for p in doc.paragraphs])
#     except:
#         return ""
#
# def read_json(path: Path) -> str:
#     try:
#         import json
#         with open(path, "r", encoding="utf-8") as f:
#             return json.dumps(json.load(f), indent=2)
#     except Exception:
#         return path.read_text(errors="ignore")
#
# READERS = {
#     ".txt": read_txt,
#     ".csv": read_csv,
#     ".xlsx": read_xlsx,
#     ".xls": read_xlsx,
#     ".pdf": read_pdf,
#     ".docx": read_docx,
#     ".json": read_json,
# }
#
# def extract_text(path: Path) -> str:
#     reader = READERS.get(path.suffix.lower())
#     if reader:
#         return reader(path)
#     try:
#         return path.read_text(errors="ignore")
#     except:
#         return ""
#
# def discover_files(folder: str) -> List[Path]:
#     files = []
#     for p in Path(folder).rglob("*"):
#         if p.is_file() and p.suffix.lower() in READERS:
#             files.append(p)
#     return files
#
# # =============================
# # Vector Store Wrapper
# # =============================
# class FaissStore:
#     def __init__(self, dim: int, store_dir: str):
#         self.dim = dim
#         self.store_dir = store_dir
#         os.makedirs(store_dir, exist_ok=True)
#         self.index_path = os.path.join(store_dir, "faiss.index")
#         self.meta_path = os.path.join(store_dir, "meta.json")
#         self.text_path = os.path.join(store_dir, "texts.json")
#         self.index = None
#         self.meta = []
#         self.texts = []
#
#     def create(self, embeddings, meta, texts):
#         self.index = faiss.IndexFlatIP(self.dim)
#         self.index.add(embeddings)
#         self.meta = meta
#         self.texts = texts
#         self._save()
#
#     def _save(self):
#         faiss.write_index(self.index, self.index_path)
#         with open(self.meta_path, "w", encoding="utf-8") as f:
#             json.dump(self.meta, f, indent=2)
#         with open(self.text_path, "w", encoding="utf-8") as f:
#             json.dump(self.texts, f, indent=2)
#
#     def load(self):
#         self.index = faiss.read_index(self.index_path)
#         with open(self.meta_path, "r", encoding="utf-8") as f:
#             self.meta = json.load(f)
#         with open(self.text_path, "r", encoding="utf-8") as f:
#             self.texts = json.load(f)
#
#     def search(self, vec, topk=5):
#         D, I = self.index.search(vec, topk)
#         results = []
#         for score, idx in zip(D[0], I[0]):
#             if idx < 0:
#                 continue
#             results.append({
#                 "score": float(score),
#                 "meta": self.meta[idx],
#                 "text": self.texts[idx][:700]
#             })
#         return results
#
# def normalize(v):
#     n = np.linalg.norm(v, axis=1, keepdims=True)
#     n[n == 0] = 1
#     return v / n
#
# # =============================
# # Build Index
# # =============================
# def build_index():
#     print(f"\n[INFO] Scanning: {DATA_DIR}")
#     files = discover_files(DATA_DIR)
#     print(f"[INFO] {len(files)} files found")
#
#     docs = []
#     metas = []
#     for f in files:
#         text = extract_text(f)
#         if text.strip():
#             docs.append(text)
#             metas.append({
#                 "filename": f.name,
#                 "filepath": str(f),
#             })
#
#     print(f"[INFO] Loading model: {EMBED_MODEL_NAME}")
#     model = SentenceTransformer(EMBED_MODEL_NAME)
#
#     print(f"[INFO] Generating vectors...")
#     vecs = model.encode(docs, convert_to_numpy=True, show_progress_bar=True)
#     vecs = vecs.astype("float32")
#     vecs = normalize(vecs)
#
#     store = FaissStore(EMBED_DIM, VECTOR_STORE_DIR)
#     store.create(vecs, metas, docs)
#
#     print("\n[SUCCESS] Vector store created in:", VECTOR_STORE_DIR)
#
# # =============================
# # Query
# # =============================
# def query_vector(query: str):
#     model = SentenceTransformer(EMBED_MODEL_NAME)
#     store = FaissStore(EMBED_DIM, VECTOR_STORE_DIR)
#     store.load()
#
#     # Encode query
#     qvec = model.encode([query], convert_to_numpy=True)
#     qvec = normalize(qvec.astype("float32"))
#
#     # Search top 5 but we will filter manually
#     results = store.search(qvec, topk=5)
#
#     # Sort results by relevance score (descending)
#     results = sorted(results, key=lambda x: x['score'], reverse=True)
#
#     # Take only the best result
#     best = results[0]
#
#     # Apply minimum score threshold
#     if best["score"] < 0.20:
#         print("No relevant match found.")
#         return
#
#     # Print clean formatted output
#     print("\n====== RESULT ======\n")
#     print(f"Score: {best['score']}")
#     print(f"File:  {best['meta']['filename']}")
#     print(f"Path:  {best['meta']['filepath']}")
#     print("Text Excerpt:")
#     print(best["text"])
#     print("\n--------------------\n")
#
# # =============================
# # Main Menu
# # =============================
# if __name__ == "__main__":
#     print("1. Build Vector Store")
#     print("2. Query")
#     choice = input("Choose Option: ")
#
#     if choice == "1":
#         build_index()
#     elif choice == "2":
#         q = input("Enter employee name or question: ")
#         query_vector(q)
#     else:
#         print("Invalid option")
