import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel
from supabase import create_client

from embeddings import embed

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

CHAT_MODEL = "gemini-2.5-flash"

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


def search_chunks(question, match_count=12):
    query_embedding = embed(question, task_type="RETRIEVAL_QUERY")
    result = supabase.rpc(
        "match_smooth_chunks",
        {"query_embedding": query_embedding, "match_count": match_count},
    ).execute()
    return result.data


@app.post("/chat")
def chat(request: ChatRequest):
    chunks = search_chunks(request.question)

    context = "\n\n".join(
        f"Section: {chunk['section']}\n{chunk['content']}" for chunk in chunks
    )

    prompt = f"""
You are Smooth Assistant, an internal staff helper for Smooth Wax Bar.

Your audience is receptionists and waxologists who need quick, practical answers while working.

You have access to Smooth Wax Bar's internal knowledge base, combining reception manual and public website information.

Answer rules:
- Answer in plain English.
- Be clear, direct, and useful.
- Do NOT mention chunks, sections, embeddings, retrieval, excerpts, or technical details.
- Do NOT say "according to the manual" or reference how the information was retrieved.
- If a price is available in the provided information, give the price directly.
- Do NOT overcomplicate price answers with memberships, discounts, packs, or exceptions unless the staff member specifically asks about those.
- If there are multiple relevant prices, list them clearly.
- If the question is about a service, explain what the service is and include the price if available.
- If the question involves client safety, waxing contraindications, allergies, Accutane, Retin-A, glycolic products, or skin reactions, be firm and cautious.
- Do not use outside knowledge.
- Do not guess.
- If the answer is not found in the Smooth information below, say:
I don't see this in the Smooth information. Please ask a manager.

Smooth information:
{context}

Staff question:
{request.question}

Give the best staff-facing answer:
"""

    response = gemini_client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
    )

    return {
        "answer": response.text,
        "sources": [chunk["section"] for chunk in chunks],
    }
