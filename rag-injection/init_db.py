from db import connect
from config import EMBED_DIM

conn = connect(register=False)
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
conn.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'clean',   -- 'clean' or 'poisoned'
    category TEXT,                        -- attack category (poisoned only)
    content TEXT NOT NULL
)""")
conn.execute(f"""
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    doc_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    text TEXT NOT NULL,
    embedding vector({EMBED_DIM}) NOT NULL
)""")
print("tables ready")
