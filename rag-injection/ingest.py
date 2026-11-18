import numpy as np
import ollama
from config import EMBED_MODEL, CHUNK_SIZE, OVERLAP


def chunk_text(text, size=CHUNK_SIZE, overlap=OVERLAP):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])         # cut text by characters, not by words
        if (start + size >= len(text)):                 # this chunk reaches the end of the text
            break
        start += size - overlap                         # next chunk starts 'overlap' chars earlier, because adjacent chunks share 'overlap' chars
    return [c.strip() for c in chunks if c.strip()]     # strips spaces at the edges and drop empty chunks


def embed(texts, prefix="search_document: "):                                  # nomic-embed-text needs a task prefix for stored texts 
    resp = ollama.embed(model=EMBED_MODEL, input=[prefix + t for t in texts])
    return [np.array(v) for v in resp["embeddings"]]                          # numpy arrays, so register_vector can store them as 'vector'


def add_document(conn, name, content, kind="clean", category=None):           
    chunks = chunk_text(content)
    vectors = embed(chunks)
    doc_id = conn.execute(
        "INSERT INTO documents (name, kind, category, content) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (name, kind, category, content),
    ).fetchone()[0]                                                            # takes document id from response
    for i, (text, vec) in enumerate(zip(chunks, vectors)):                     # zip pairs each chunk with its vector, enumerate gives i = chunk_index
        conn.execute(
            "INSERT INTO chunks (doc_id, chunk_index, text, embedding) "
            "VALUES (%s, %s, %s, %s)",
            (doc_id, i, text, vec),
        )                                                                      # insert values into chunks table
    return doc_id
