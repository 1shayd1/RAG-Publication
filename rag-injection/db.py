import psycopg
from pgvector.psycopg import register_vector
from config import DB_DSN


def connect(register=True):
    conn = psycopg.connect(DB_DSN, autocommit=True) # connect to database with address DB_DSN, every command is committed automatically
    if register:
        register_vector(conn)                       # teach the connection the 'vector' type (numpy array <-> DB vector); needs the extension to exist
    return conn
