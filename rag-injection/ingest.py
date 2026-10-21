import numpy as np
import ollama
from config import EMBED_MODEL, CHUNK_SIZE, OVERLAP


def chunk_text(text, size=CHUNK_SIZE, overlap=OVERLAP):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return [c.strip() for c in chunks if c.strip()]


def embed(texts, prefix="search_document: "):
    resp = ollama.embed(model=EMBED_MODEL, input=[prefix + t for t in texts])
    return [np.array(v) for v in resp["embeddings"]]


def add_document(conn, name, content, kind="clean", category=None):
    chunks = chunk_text(content)
    vectors = embed(chunks)
    doc_id = conn.execute(
        "INSERT INTO documents (name, kind, category, content) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (name, kind, category, content),
    ).fetchone()[0]
    for i, (text, vec) in enumerate(zip(chunks, vectors)):
        conn.execute(
            "INSERT INTO chunks (doc_id, chunk_index, text, embedding) "
            "VALUES (%s, %s, %s, %s)",
            (doc_id, i, text, vec),
        )
    return doc_id
