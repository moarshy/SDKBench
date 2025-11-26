# Using sentence-transformers (default)
python app.py

# Using OpenAI
export EMBEDDING_PROVIDER=openai
export MODEL_NAME=text-embedding-ada-002
export OPENAI_API_KEY=your-api-key
python app.py

# Custom database path
export LANCEDB_PATH=/path/to/db
python app.py