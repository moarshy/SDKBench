# Using sentence-transformers (default)
python app.py

# Using OpenAI
export EMBEDDING_PROVIDER=openai
export MODEL_NAME=text-embedding-ada-002
export OPENAI_API_KEY=your-key-here
python app.py

# Custom sentence-transformers model
export EMBEDDING_PROVIDER=sentence-transformers
export MODEL_NAME=all-mpnet-base-v2
python app.py

# Custom database path
export LANCEDB_PATH=/path/to/db
python app.py