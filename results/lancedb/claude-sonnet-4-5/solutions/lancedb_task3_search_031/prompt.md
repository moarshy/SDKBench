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

Task: Search
Basic vector similarity search

Current project files:

=== requirements.txt ===
```
pandas>=2.0.0
numpy>=1.24.0

```

=== search.py ===
```
"""Basic vector similarity search."""

# TODO: Import lancedb
# TODO: Import embedding model

def search_similar(query_text: str, k: int = 5):
    """Search for similar documents.

    TODO:
        1. Connect to database and open table
        2. Generate query embedding
        3. Perform table.search(query_vector).limit(k)
        4. Return results as pandas DataFrame
    """
    pass

def main():
    results = search_similar("machine learning", k=10)
    print(f"Found results")

if __name__ == "__main__":
    main()

```


For this search task:
1. Implement vector similarity search
2. Use appropriate search parameters (limit, filter)
3. Handle hybrid search if needed
4. Return results in proper format

Please provide the complete solution by modifying the input files above.
Files to output: requirements.txt, search.py

CRITICAL: Each code block MUST start with a filepath comment on the first line:
- Python: # filepath: filename.py
- JavaScript/TypeScript: // filepath: filename.ts
- Other: # filepath: filename.ext
