import psycopg
from pgvector.psycopg import register_vector
from config import DB_DSN


def connect(register=True):
    conn = psycopg.connect(DB_DSN, autocommit=True)
    if register:
        register_vector(conn)
    return conn
