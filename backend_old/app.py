import requests
import chromadb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "smooth_manual"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(COLLECTION_NAME)


class ChatRequest(BaseModel):
    question: str


def embed(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]


def ask_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False
        }
    )
    response.raise_for_status()
    return response.json()["response"]


@app.post("/chat")
def chat(request: ChatRequest):
    question_embedding = embed(request.question)

    # 1. Semantic/vector search
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=12
    )

    semantic_chunks = results["documents"][0]
    semantic_metas = results["metadatas"][0]

    # 2. Robust keyword search across all chunks
    all_docs = collection.get()

    stop_words = {
        "a", "an", "the", "and", "or", "but", "if", "then", "to", "of", "in",
        "on", "for", "with", "who", "what", "when", "where", "why", "how",
        "can", "could", "should", "would", "is", "are", "was", "were", "be",
        "been", "being", "do", "does", "did", "get", "got", "have", "has",
        "had", "client", "customer", "someone"
    }

    question_words = [
        word.strip(".,?!:;()[]{}\"'").lower()
        for word in request.question.split()
    ]

    question_words = [
        word for word in question_words
        if len(word) > 2 and word not in stop_words
    ]

    scored_keyword_results = []

    for doc, meta in zip(all_docs["documents"], all_docs["metadatas"]):
        doc_lower = doc.lower()

        score = 0

        for word in question_words:
            if word in doc_lower:
                score += 3

        # Bonus if multiple meaningful words appear in same chunk
        if score > 0:
            score += len([word for word in question_words if word in doc_lower])

        if score > 0:
            scored_keyword_results.append((score, doc, meta))

    scored_keyword_results.sort(reverse=True, key=lambda x: x[0])

    keyword_chunks = [item[1] for item in scored_keyword_results[:12]]
    keyword_metas = [item[2] for item in scored_keyword_results[:12]]

    # 3. Combine results and remove duplicates
    chunks = []
    metadatas = []
    seen = set()

    for chunk, meta in zip(
        semantic_chunks + keyword_chunks,
        semantic_metas + keyword_metas
    ):
        unique_id = f"{meta['source']}_{meta['chunk']}"

        if unique_id not in seen:
            chunks.append(chunk)
            metadatas.append(meta)
            seen.add(unique_id)

    context = "\n\n".join(
        f"Source: {meta['source']}, chunk {meta['chunk']}\n{chunk}"
        for chunk, meta in zip(chunks, metadatas)
    )

    prompt = f"""
You are Smooth Assistant, an internal staff helper for Smooth Wax Bar.

Your audience is receptionists and waxologists who need quick, practical answers while working.

You have access to Smooth Wax Bar internal manual information and public website information.

Answer rules:
- Answer in plain English.
- Be clear, direct, and useful.
- Do NOT mention chunks, source numbers, embeddings, retrieval, excerpts, or technical details.
- Do NOT say "according to chunk" or "according to the manual."
- If a price is available in the provided information, give the price directly.
- Do NOT overcomplicate price answers with memberships, discounts, packs, or exceptions unless the staff member specifically asks about those.
- If there are multiple relevant prices, list them clearly.
- If the question is about a service, explain what the service is and include the price if available.
- If the question involves client safety, waxing contraindications, allergies, Accutane, Retin-A, glycolic products, or skin reactions, be firm and cautious.
- Do not use outside knowledge.
- Do not guess.
- If the answer is not found in the Smooth information below, say:
I don’t see this in the Smooth information. Please ask a manager.

Smooth information:
{context}

Staff question:
{request.question}

Give the best staff-facing answer:
"""

    answer = ask_ollama(prompt)

    return {
        "answer": answer,
        "sources": metadatas
    }

# De-bugging
@app.get("/debug-search")
def debug_search(q: str):
    all_docs = collection.get()

    matches = []

    for doc, meta in zip(all_docs["documents"], all_docs["metadatas"]):
        if q.lower() in doc.lower():
            matches.append({
                "metadata": meta,
                "text": doc[:1000]
            })

    return {
        "query": q,
        "number_of_matches": len(matches),
        "matches": matches[:10]
    }