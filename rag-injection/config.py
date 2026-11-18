DB_DSN = "postgresql://postgres:pass@localhost:5432/postgres" # trascript - data base data source name

EMBED_MODEL = "nomic-embed-text"                              # model that turns text into vectors
EMBED_DIM = 768                                               # vector size; fixed for nomic-embed-text
MODELS = ["qwen2.5:3b","llama3.2:3b","gemma2:2b","phi3.5"]

CHUNK_SIZE = 500                                              # documents are split into chunks of 500 characters
OVERLAP = 50                                                  # adjacent chunks share 50 characters so text on the border is not lost
TOP_K = 3                                                     # number of most similar chunks returned by the search

MAX_TOKENS = 150                                              # max answer length in tokens (token is roughly part of a word)
TEMPERATURE = 0                                               # lower values make responses more deterministic, higher values increase creativity
SEED = 67                                                     # fixed starting value for the random generator, for reproducibility
