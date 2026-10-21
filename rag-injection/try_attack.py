import sys
from db import connect
from rag import ask
from config import MODELS

case_id = sys.argv[1]
conn = connect()
row = conn.execute(
    "SELECT doc_id, question, canary FROM test_cases WHERE case_id=%s", (case_id,)
).fetchone()
doc_id, question, canary = row

for model in MODELS:
    answer, chunks = ask(conn, model, question, doc_ids=[doc_id])
    print(f"\n=== {model} ===\n{answer}")
    print("canary in answer:", canary in answer if canary else "n/a")
    print("canary retrieved:", any(canary in c[1] for c in chunks) if canary else "n/a")
