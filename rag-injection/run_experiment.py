import argparse
import time

from config import MODELS, SEED
from db import connect
from evaluate import canary_in_answer, is_correct
from rag import ask

parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=None, help="only the first N cases")
parser.add_argument("--models", nargs="*", default=MODELS)
parser.add_argument("--run", type=int, default=0, help="run index (changes the seed)")
args = parser.parse_args()

conn = connect()
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

cases = conn.execute(
    "SELECT case_id, doc_id, variant, question, answer, canary "
    "FROM test_cases ORDER BY doc_id"
).fetchall()
if args.limit:
    cases = cases[:args.limit]

total = len(cases) * len(args.models)
done = 0
for model in args.models:              
    for case_id, doc_id, variant, question, expected, canary in cases:
        done += 1
        exists = conn.execute(
            "SELECT 1 FROM results WHERE model=%s AND case_id=%s AND run_idx=%s",
            (model, case_id, args.run),
        ).fetchone()
        if exists:
            continue            

        t0 = time.time()
        answer, chunks = ask(conn, model, question, doc_ids=[doc_id], seed=SEED + args.run)
        seconds = time.time() - t0

        hit = canary_in_answer(answer, canary) if canary else None
        retrieved = any(canary.lower() in c[1].lower() for c in chunks) if canary else None
        correct = is_correct(answer, expected)

        conn.execute(
            "INSERT INTO results (model, case_id, run_idx, answer, canary_in_answer, "
            "canary_retrieved, correct, seconds) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (model, case_id, args.run, answer, hit, retrieved, correct, seconds),
        )
        print(f"[{done}/{total}] {model:14} {case_id:28} attack={hit} ok={correct} {seconds:.1f}s")
