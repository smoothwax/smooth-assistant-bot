import os
import time
import requests
from dotenv import load_dotenv
from supabase import create_client
from docx import Document

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

DATA_DIR = "../data"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def embed(text):
    response = requests.post(
        f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL}",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={"inputs": text, "options": {"wait_for_model": True}},
        timeout=60,
    )
    response.raise_for_status()

    embedding = response.json()

    if isinstance(embedding[0], list):
        embedding = embedding[0]

    return embedding


def read_docx(path):
    doc = Document(path)
    paragraphs = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def read_txt(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def chunk_text(text, chunk_size=350, overlap=120):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks


def main():
    if not SUPABASE_URL or not SUPABASE_KEY or not HF_TOKEN:
        raise ValueError("Missing SUPABASE_URL, SUPABASE_KEY, or HF_TOKEN in .env")

    supabase.table("documents").delete().neq("id", 0).execute()

    total = 0

    for filename in os.listdir(DATA_DIR):
        lower_filename = filename.lower()
        path = os.path.join(DATA_DIR, filename)

        if lower_filename.endswith(".docx"):
            text = read_docx(path)
        elif lower_filename.endswith(".txt"):
            text = read_txt(path)
        else:
            continue

        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            embedding = embed(chunk)

            supabase.table("documents").insert({
                "content": chunk,
                "source": filename,
                "chunk": i,
                "embedding": embedding
            }).execute()

            total += 1
            print(f"Uploaded {total}: {filename} chunk {i}")
            time.sleep(0.2)

    print(f"Done. Uploaded {total} chunks to Supabase.")


if __name__ == "__main__":
    main()