import ollama
from config import TOP_K, MAX_TOKENS, TEMPERATURE, SEED
from ingest import embed

SYSTEM_PROMPT = "You are a helpful assistant. Answer the question using the context."

USER_TEMPLATE = """Context:
{context}

Question: {question}"""


def retrieve(conn, question, k=TOP_K, doc_ids=None):
    qv = embed([question], prefix="search_query: ")[0]
    if doc_ids:
        sql = ("SELECT doc_id, text, embedding <=> %s AS dist FROM chunks "
               "WHERE doc_id = ANY(%s) ORDER BY dist LIMIT %s")
        params = (qv, doc_ids, k)
    else:
        sql = ("SELECT doc_id, text, embedding <=> %s AS dist FROM chunks "
               "ORDER BY dist LIMIT %s")
        params = (qv, k)
    return conn.execute(sql, params).fetchall()


def generate(model, question, chunk_texts, seed=SEED):
    context = "\n\n".join(f"[{i + 1}] {t}" for i, t in enumerate(chunk_texts))
    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(context=context, question=question)},
        ],
        options={"temperature": TEMPERATURE, "num_predict": MAX_TOKENS, "seed": seed},
    )
    return resp["message"]["content"]


def ask(conn, model, question, doc_ids=None, seed=SEED):
    rows = retrieve(conn, question, doc_ids=doc_ids)
    answer = generate(model, question, [r[1] for r in rows], seed=seed)
    return answer, rows
