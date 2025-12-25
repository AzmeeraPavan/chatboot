import sys
import indexing
import retrieval
import generation

def cmd_build():
    indexing.build_vectorstore()

def cmd_retrieve(q):
    docs = retrieval.hybrid_search(q)
    print(f"\n=== Retrieved {len(docs)} Chunks ===\n")
    for i, d in enumerate(docs, 1):
        print(f"--- CHUNK {i} ({d.metadata.get('source')}) ---\n{d.page_content}\n")

def cmd_answer(q, engine):
    docs = retrieval.hybrid_search(q)
    if not docs:
        print("[WARN] No relevant documents found.")
        return

    context = "\n\n".join(d.page_content for d in docs)
    print(f"[INFO] Context length = {len(context)} chars")

    if engine == "hf":
        ans = generation.generate_with_hf(context, q)
    else:
        ans = generation.generate_with_llama(context, q)

    print("\n===== ANSWER =====\n")
    print(ans)
    print("\n===================\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [build|retrieve|answer] <query>")
        sys.exit()

    cmd = sys.argv[1].lower()

    if cmd == "build":
        cmd_build()

    elif cmd == "retrieve":
        q = " ".join(sys.argv[2:])
        cmd_retrieve(q)

    elif cmd == "answer":
        args = sys.argv[2:]
        engine = "hf" if "--hf" in args else "llama"
        query = " ".join(a for a in args if not a.startswith("--"))
        cmd_answer(query, engine)

    else:
        print("Unknown command:", cmd)
