import os

from google import genai

EMBEDDING_MODEL = "gemini-embedding-001"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
            http_options={"api_version": "v1"},
        )
    return _client


def embed(text, task_type="RETRIEVAL_DOCUMENT"):
    client = _get_client()
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config={"task_type": task_type, "output_dimensionality": 768},
    )
    return result.embeddings[0].values
