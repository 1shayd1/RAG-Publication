import json
from db import connect
from ingest import add_document

conn = connect()
conn.execute("""
CREATE TABLE IF NOT EXISTS test_cases (
    case_id TEXT PRIMARY KEY,
    doc_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    variant TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    canary TEXT
)""")
conn.execute("TRUNCATE test_cases, chunks, documents RESTART IDENTITY CASCADE")

cases = json.load(open("data/test_cases.json", encoding="utf-8"))
for c in cases:
    kind = "clean" if c["variant"] == "clean" else "poisoned"
    category = None if kind == "clean" else c["variant"]
    db_doc_id = add_document(conn, c["case_id"], c["text"], kind, category)
    conn.execute(
        "INSERT INTO test_cases (case_id, doc_id, variant, question, answer, canary) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (c["case_id"], db_doc_id, c["variant"], c["question"], c["answer"], c["canary"]),
    )
    print("loaded", c["case_id"])
