#!/usr/bin/env bash
# Rebuilds all experiment data from scratch: drop tables -> create schema -> build test cases -> load chunks + embeddings.
# WARNING: deletes everything in the DB, including the results table.

set -euo pipefail                  # stop on the first error, on unset variables and on failed pipes

cd "$(dirname "$0")"               # run from the project folder, wherever the script is called from

DSN=$(python -c "from config import DB_DSN; print(DB_DSN)")   # take the DB address from config.py (one source of truth)

echo "==> 1/4 Dropping old tables"
psql "$DSN" -q -c "DROP TABLE IF EXISTS results, test_cases, chunks, documents CASCADE;"

echo "==> 2/4 Creating schema"
python init_db.py

echo "==> 3/4 Building test cases"
python build_dataset.py

echo "==> 4/4 Loading documents, chunks and embeddings"
python load_dataset.py > /dev/null   # hide 60 loading lines

echo "Finished"
