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

Task: Initialization
Connection with index creation

Current project files:

=== requirements.txt ===
```
pandas>=2.0.0
numpy>=1.24.0

```

=== app.py ===
```
"""LanceDB with IVF-PQ index creation."""

# TODO: Import lancedb
# TODO: Import LanceModel, Vector from lancedb.pydantic

# TODO: Define document schema

def create_indexed_table(db, table_name: str, data):
    """Create table and build IVF-PQ index.

    TODO:
        1. Create table with data
        2. Create IVF-PQ index:
           table.create_index(
               metric="cosine",
               num_partitions=4,
               num_sub_vectors=32
           )
        3. Return table
    """
    pass

def main():
    # TODO: Connect to database
    # TODO: Create indexed table
    print("Indexed database ready")

if __name__ == "__main__":
    main()

```


For this initialization task:
1. Import lancedb library
2. Create database connection with lancedb.connect()
3. Handle connection path appropriately
4. Verify connection is working

Please provide the complete solution by modifying the input files above.
Files to output: requirements.txt, app.py

CRITICAL: Each code block MUST start with a filepath comment on the first line:
- Python: # filepath: filename.py
- JavaScript/TypeScript: // filepath: filename.ts
- Other: # filepath: filename.ext
