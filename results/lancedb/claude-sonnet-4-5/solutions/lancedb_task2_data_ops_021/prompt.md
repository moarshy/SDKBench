# System Prompt

You are an expert developer specializing in lancedb integration.
You are helping integrate lancedb (version 0.5.0) into a python application.


LanceDB is a developer-friendly, serverless vector database for AI applications.

Key Concepts:
1. Connection: lancedb.connect() to create or open a database
2. Tables: Schema-defined collections storing vectors and metadata
3. Search: Vector similarity search, full-text search, and hybrid search
4. Embeddings: Integration with embedding models for vectorization

LanceDB Patterns:
- Connection: db = lancedb.connect("./my_lancedb")
- Create table: db.create_table("name", data)
- Open table: table = db.open_table("name")
- Vector search: table.search(query_vector).limit(k).to_pandas()
- Hybrid search: table.search(query_type="hybrid").vector(vec).text(text)
- Full-text search: table.create_fts_index("column"), table.search(text)

Common integrations:
- sentence-transformers for embeddings
- pandas for data manipulation
- pyarrow for efficient data types


Your responses should:
1. Provide working code that follows best practices
2. Include all necessary imports
3. Add appropriate error handling
4. Follow the framework's conventions
5. Be production-ready

IMPORTANT: You MUST output files with the EXACT same filenames as provided in the input.
- If the input has "app.py", your output must also be named "app.py"
- If the input has "middleware.ts", your output must also be named "middleware.ts"
- Do NOT create new filenames - modify the existing files

When providing code, ALWAYS specify the file path as a comment on the FIRST LINE inside each code block:
- For Python: # filepath: app.py
- For JavaScript/TypeScript: // filepath: middleware.ts
- For other files: # filepath: requirements.txt

Example format:
```python
# filepath: app.py
import lancedb
# rest of code...
```


---

# User Prompt

Task: Data Operations
Handle token limits with chunking

Current project files:

=== requirements.txt ===
```
pandas>=2.0.0
numpy>=1.24.0
tiktoken>=0.5.0

```

=== data_ops.py ===
```
"""Handle token limits with chunking."""

# TODO: Import tiktoken for token counting
# TODO: Import lancedb

MAX_TOKENS = 8192

def count_tokens(text: str, model: str = "cl100k_base"):
    """Count tokens in text.

    TODO:
        1. Use tiktoken to encode
        2. Return token count
    """
    pass

def chunk_text(text: str, max_tokens: int = MAX_TOKENS):
    """Chunk text to fit token limit.

    TODO:
        1. Split text at sentence boundaries
        2. Ensure each chunk < max_tokens
        3. Return list of chunks
    """
    pass

def ingest_with_chunking(db, table_name: str, documents: list):
    """Ingest documents with automatic chunking.

    TODO:
        1. Chunk oversized documents
        2. Create table with chunks
    """
    pass

def main():
    # TODO: Create long document
    # TODO: Ingest with chunking
    print("Token-aware ingestion complete")

if __name__ == "__main__":
    main()

```


For this data operations task:
1. Create or open tables with proper schema
2. Add data with correct vector dimensions
3. Handle embeddings appropriately
4. Implement proper error handling

Please provide the complete solution by modifying the input files above.
Files to output: requirements.txt, data_ops.py

CRITICAL: Each code block MUST start with a filepath comment on the first line:
- Python: # filepath: filename.py
- JavaScript/TypeScript: // filepath: filename.ts
- Other: # filepath: filename.ext
