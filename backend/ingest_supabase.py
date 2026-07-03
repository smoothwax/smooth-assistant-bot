import os
import re

from dotenv import load_dotenv
from supabase import create_client

from embeddings import embed

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "smooth-knowledge-base.md")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def split_into_sections(markdown_text):
    """Split the knowledge base on '## ' headings so each chunk is one topic."""
    parts = re.split(r"\n(?=## )", markdown_text)
    sections = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        heading_match = re.match(r"#+\s*(.+)", part)
        heading = heading_match.group(1).strip() if heading_match else "Overview"
        sections.append((heading, part))

    return sections


def main():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    sections = split_into_sections(markdown_text)
    print(f"Found {len(sections)} sections to embed.")

    try:
        supabase.table("smooth_chunks").delete().neq("id", 0).execute()
    except Exception:
        pass

    rows = []
    for heading, content in sections:
        embedding = embed(content)
        rows.append({"section": heading, "content": content, "embedding": embedding})
        print(f"Embedded: {heading}")

    supabase.table("smooth_chunks").insert(rows).execute()
    print(f"Uploaded {len(rows)} chunks to Supabase.")


if __name__ == "__main__":
    main()
