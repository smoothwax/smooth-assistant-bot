import os
import requests
import chromadb
from docx import Document

DATA_DIR = "../data"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "smooth_manual"

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(COLLECTION_NAME)


def embed(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]


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
    doc_id = 0

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

            collection.add(
                ids=[f"{filename}_{i}"],
                embeddings=[embed(chunk)],
                documents=[chunk],
                metadatas=[{
                    "source": filename,
                    "chunk": i
                }]
            )

            doc_id += 1

    print(f"Done. Added {doc_id} chunks to the Smooth manual database.")


if __name__ == "__main__":
    main()