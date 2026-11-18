import json
from db import connect
from ingest import add_document

conn = connect()      # extension was created earlier by init_db.py
conn.execute("TRUNCATE test_cases, chunks, documents, results RESTART IDENTITY CASCADE")  # for repeated launches

cases = json.load(open("data/test_cases.json", encoding="utf-8"))
for c in cases:
    kind = "clean" if c["variant"] == "clean" else "poisoned"       
    category = None if kind == "clean" else c["variant"]
    db_doc_id = add_document(conn, c["case_id"], c["text"], kind, category)      # load data from document to documents and chunks tables
    conn.execute(
        "INSERT INTO test_cases (case_id, doc_id, variant, question, answer, canary) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (c["case_id"], db_doc_id, c["variant"], c["question"], c["answer"], c["canary"]),
    )
    print("loaded", c["case_id"])
