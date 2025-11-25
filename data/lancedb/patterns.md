# LanceDB Pattern Analysis Report
**Total Repositories Analyzed:** 10

## Import Patterns
- `import lancedb` (21 repos)
- `from lancedb.pydantic import LanceModel, Vector` (10 repos)
- `from lancedb.embeddings import EmbeddingFunctionRegistry` (4 repos)
- `from lancedb.table import Table` (2 repos)
- `from lancedb.rerankers import RRFReranker` (1 repos)
- `from lancedb.pydantic import LanceModel` (1 repos)
- `from lancedb.embeddings import with_embeddings` (1 repos)
- `from lancedb.rerankers import AnswerdotaiRerankers` (1 repos)
- `from lancedb.pydantic import pydantic_to_schema` (1 repos)
- `from lancedb.embeddings.registry import get_registry` (1 repos)

## Connection Patterns
```python
lancedb.connect(str(Path(lance_path)
```
```python
lancedb.connect("data/openai_db"
```
```python
lancedb.connect("data/image_table"
```
```python
lancedb.connect(uri)
```
```python
lancedb.connect(database)
```

## Embedding Models
- `all-MiniLM-L6-v2` (4 instances)
- `SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"` (1 instances)
- `SentenceTransformer('BAAI/bge-small-en-v1.5'` (1 instances)
- `SentenceTransformer('all-MiniLM-L6-v2'` (1 instances)

## Search Methods
```python
.search(
            "tutorial", limit=5, filter="uri LIKE '%example.com%'"
        )
```
```python
.search(
            "tutorial", limit=5, filter="uri = 'https://other.com/java.html'"
        )
```
```python
.search(search_query)
```
```python
.search(r"\[(\d+)
```
```python
.vector_search(
            "dummy_query",
            embedding_fn=lambda _, __: test_vectors["valid_vector"],
            vector_column_names=["vect
```

## Task Suitability

### Initialization (9 repos)
- haiku.rag
- lancedb-multimodal-myntra-fashion-search-engine
- JamAIBase

### Data Operations (10 repos)
- haiku.rag
- lancedb-multimodal-myntra-fashion-search-engine
- JamAIBase

### Vector Search (10 repos)
- haiku.rag
- lancedb-multimodal-myntra-fashion-search-engine
- JamAIBase

### Embeddings (3 repos)
- JamAIBase
- prompttools
- semantweet-search
