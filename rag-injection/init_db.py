from db import connect
from config import EMBED_DIM

conn = connect(register=False)                                                 # the extension may not exist yet, so register=False
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")                          # create extension 'vector', so now db knows what is 'vector' type
conn.execute("""
CREATE TABLE IF NOT EXISTS documents (                                         
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'clean',                                        -- clean or poisoned
    category TEXT,                                                             -- direct override/goal hijacking/hidden text/fake authority; NULL for clean docs
    content TEXT NOT NULL                                                      -- text from document
)""")

conn.execute(f"""
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    doc_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,            -- from which doc this chunk is
    chunk_index INT NOT NULL,                                                  -- index number of chunk in doc
    text TEXT NOT NULL,                                                        -- chunk text
    embedding vector({EMBED_DIM}) NOT NULL                                     -- chunk vector
)""")  

conn.execute("""
 CREATE TABLE IF NOT EXISTS test_cases (
     case_id TEXT PRIMARY KEY,
     doc_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
     variant TEXT NOT NULL,
     question TEXT NOT NULL,
     answer TEXT NOT NULL,
     canary TEXT
)""")

conn.execute("""
CREATE TABLE IF NOT EXISTS results (
     id SERIAL PRIMARY KEY,
     model TEXT NOT NULL,
     case_id TEXT NOT NULL,
     run_idx INT NOT NULL,
     answer TEXT NOT NULL,
     canary_in_answer BOOLEAN,
     canary_retrieved BOOLEAN,
     correct BOOLEAN NOT NULL,
     seconds REAL,
     created_at TIMESTAMPTZ DEFAULT now(),
     UNIQUE (model, case_id, run_idx)
)""")

print("tables ready")
