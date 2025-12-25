
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import config

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False

def generate_with_llama(context, query):
    if not LLAMA_AVAILABLE:
        return "[ERROR] llama-cpp not installed."

    try:
        llm = Llama(model_path=config.LLAMA_MODEL_PATH, n_ctx=4096, verbose=False)
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        result = llm(prompt, max_tokens=300)
        return result["choices"][0]["text"]
    except Exception as e:
        return f"[ERROR] Llama failed: {e}"

def generate_with_hf(context, query):
    tok = AutoTokenizer.from_pretrained(config.HF_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(config.HF_MODEL)
    gen = pipeline(
        "text2text-generation",  # ✅ CORRECT pipeline
        model=model,
        tokenizer=tok
    )
    prompt = f"Use ONLY this context:\n{context}\n\nQ: {query}\nA:"
    out = gen(prompt, max_new_tokens=200, do_sample=False)
    return out[0]["generated_text"]
