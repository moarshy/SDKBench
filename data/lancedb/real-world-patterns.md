# LanceDB Real-World Usage Patterns Analysis

> Analysis of 10 production repositories using LanceDB to inform better benchmark sample generation.

## Executive Summary

After analyzing 10 real-world LanceDB repositories, we identified key patterns that should inform our benchmark samples. The current samples are too simplistic compared to production usage. This document outlines patterns, code snippets, and recommendations for creating more realistic and challenging benchmark tasks.

---

## 1. Repository Overview

| Repository | Stars | Use Case | Key Patterns |
|------------|-------|----------|--------------|
| **hegelai/prompttools** | 2965 | LLM experimentation | Embedding function registry, batch processing |
| **EmbeddedLLM/JamAIBase** | 1077 | AI platform | Production architecture, async patterns |
| **ggozad/haiku.rag** | - | RAG framework | Hybrid search, reranking, FTS indexing |
| **prrao87/lancedb-study** | - | Learning resource | Index creation, batch embedding |
| **sankalp1999/code_qa** | - | Code search | HYDE, two-stage retrieval, Redis caching |
| **sankalp1999/semantweet-search** | - | Tweet search | Hybrid search, prefiltering, async embeddings |
| **ishandutta0098/multimodal-search** | - | Fashion search | CLIP embeddings, multimodal search |
| **wzdavid/ThinkRAG** | - | Chinese RAG | BM25+Vector fusion, custom tokenization |
| **kuzudb/graph-rag-workshop** | - | Graph+Vector RAG | Cohere reranking, hybrid retrieval |
| **plaggy/rag-containers** | - | Containerized RAG | External TEI service, IVF-PQ indexing |

---

## 2. Critical Patterns Missing from Current Samples

### 2.1 Embedding Function Registry (HIGH PRIORITY)

**Current samples use:** Direct `SentenceTransformer` instantiation
**Production uses:** `EmbeddingFunctionRegistry` for pluggable models

```python
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("openai").create(name="text-embedding-3-large", max_retries=2)

class Document(LanceModel):
    text: str = model.SourceField()  # Auto-embed this field
    vector: Vector(model.ndims()) = model.VectorField()
    metadata: str
```

**Why it matters:** This is the recommended pattern for production. It handles retries, batching, and model switching automatically.

---

### 2.2 Hybrid Search with FTS Index (HIGH PRIORITY)

**Current samples use:** Basic vector search only
**Production uses:** Hybrid search combining BM25 + vector with RRF reranking

```python
# Create both vector and FTS indices
table.create_index(metric="cosine", num_partitions=4, num_sub_vectors=32)
table.create_fts_index("content", replace=True, with_position=True)

# Hybrid search with Reciprocal Rank Fusion
from lancedb.rerankers import RRFReranker

reranker = RRFReranker()
results = (
    table.search(query_type="hybrid")
    .vector(query_embedding)
    .text(query_text)
    .rerank(reranker)
    .limit(10)
    .to_pandas()
)
```

**Why it matters:** Hybrid search significantly improves relevance by combining semantic and keyword matching.

---

### 2.3 Advanced Filtering with Prefilter (HIGH PRIORITY)

**Current samples use:** No filtering or post-filtering
**Production uses:** SQL WHERE clauses with prefilter optimization

```python
# Dynamic filter building
def build_filter(year_from, year_to, category=None, min_likes=None):
    parts = []
    if year_from:
        parts.append(f"year >= {year_from}")
    if year_to:
        parts.append(f"year <= {year_to}")
    if category:
        parts.append(f"category = '{category}'")
    if min_likes:
        parts.append(f"likes >= {min_likes}")
    return " AND ".join(parts) if parts else None

# Apply with prefilter for efficiency
filter_clause = build_filter(2020, 2024, category="tech")
results = (
    table.search(query_vector)
    .where(filter_clause, prefilter=True)  # Filter before vector search
    .limit(20)
    .to_pandas()
)
```

**Why it matters:** Prefiltering reduces the search space before expensive vector operations.

---

### 2.4 Reranking Strategies (MEDIUM PRIORITY)

**Current samples:** No reranking
**Production uses:** Multiple reranking approaches

```python
# Option 1: Linear Combination Reranker
from lancedb.rerankers import LinearCombinationReranker
reranker = LinearCombinationReranker(weight=0.7)  # 70% vector, 30% FTS

# Option 2: Cross-Encoder Reranker (Cohere)
from lancedb.rerankers import CohereReranker
reranker = CohereReranker(model="rerank-english-v3.0", top_n=10)

# Option 3: AnswerDotAI Reranker (ColBERT-based)
from lancedb.rerankers import AnswerdotaiRerankers
reranker = AnswerdotaiRerankers(column="source_code")

# Apply reranking
results = table.search(query).rerank(reranker).limit(10).to_list()
```

---

### 2.5 Async Batch Embedding (MEDIUM PRIORITY)

**Current samples:** Synchronous single-document embedding
**Production uses:** Async batch processing with rate limiting

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()
BATCH_SIZE = 32  # 32 * ~200 tokens = 6400 < 8191 token limit

async def embed_batch(texts: list[str]) -> list[list[float]]:
    response = await client.embeddings.create(
        input=texts,
        model="text-embedding-3-large"
    )
    return [item.embedding for item in response.data]

async def embed_all(df, batch_size=BATCH_SIZE):
    tasks = []
    for i in range(0, len(df), batch_size):
        batch = df['text'][i:i+batch_size].tolist()
        tasks.append(embed_batch(batch))

    results = await asyncio.gather(*tasks)
    return [emb for batch in results for emb in batch]

# Usage
embeddings = asyncio.run(embed_all(df))
```

---

### 2.6 IVF-PQ Index Configuration (MEDIUM PRIORITY)

**Current samples:** No index creation or basic defaults
**Production uses:** Tuned IVF-PQ parameters

```python
# Wait for minimum rows before indexing
row_count = table.count_rows()
if row_count >= 256:  # Minimum for IVF-PQ
    table.create_index(
        metric="cosine",
        num_partitions=4,      # sqrt(N) is a good starting point
        num_sub_vectors=32,    # Higher = better recall, slower
        index_type="IVF_PQ"
    )

# Search with index parameters
results = (
    table.search(query_vector)
    .nprobes(10)           # More probes = better recall, slower
    .refine_factor(5)      # Re-rank top candidates
    .limit(20)
    .to_list()
)
```

---

### 2.7 Multimodal Search (CLIP) (LOW PRIORITY)

**Current samples:** Text-only
**Production uses:** Image and text embeddings with CLIP

```python
from lancedb.embeddings import EmbeddingFunctionRegistry
from PIL import Image

registry = EmbeddingFunctionRegistry.get_instance()
clip = registry.get("open-clip").create()

class ImageDocument(LanceModel):
    vector: Vector(clip.ndims()) = clip.VectorField()
    image_uri: str = clip.SourceField()

    @property
    def image(self):
        return Image.open(self.image_uri)

# Create table with images
table = db.create_table("images", schema=ImageDocument)
table.add(pd.DataFrame({"image_uri": image_paths}))

# Search by text OR image
text_results = table.search("red dress").limit(10).to_pydantic(ImageDocument)
image_results = table.search(Image.open("query.jpg")).limit(10).to_pydantic(ImageDocument)
```

---

### 2.8 HYDE (Hypothetical Document Embeddings) (ADVANCED)

**Current samples:** Direct query embedding
**Production uses:** LLM-generated hypothetical answers for better retrieval

```python
from openai import OpenAI

client = OpenAI()

def hyde_embed(query: str, table) -> list:
    """Generate hypothetical answer, then embed it for search."""
    # Step 1: Generate hypothetical answer
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Generate a hypothetical code snippet that would answer this query."},
            {"role": "user", "content": query}
        ]
    )
    hypothetical_answer = response.choices[0].message.content

    # Step 2: Search using the hypothetical answer
    results = table.search(hypothetical_answer).limit(10).to_list()
    return results

# Two-stage HYDE for refinement
def hyde_v2(query: str, initial_context: str, table) -> list:
    """Refined search using initial context."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Given this context:\n{initial_context}\n\nGenerate a refined answer."},
            {"role": "user", "content": query}
        ]
    )
    refined_query = response.choices[0].message.content
    return table.search(refined_query).limit(10).to_list()
```

---

## 3. Application Integration Patterns

### 3.1 Flask with Redis Caching

```python
from flask import Flask, session
import redis
from redis import ConnectionPool
import lancedb

app = Flask(__name__)

# Connection pooling
app.redis_pool = ConnectionPool(host='localhost', port=6379, max_connections=10)
app.redis_client = redis.Redis(connection_pool=app.redis_pool)

# LanceDB connection
db = lancedb.connect("./database")
table = db.open_table("documents")

@app.route('/search', methods=['POST'])
def search():
    query = request.json['query']
    user_id = session.get('user_id')

    # Check cache first
    cache_key = f"search:{hash(query)}"
    cached = app.redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Perform search
    results = table.search(query, query_type="hybrid").limit(10).to_list()

    # Cache results (expire in 1 hour)
    app.redis_client.setex(cache_key, 3600, json.dumps(results))

    return results
```

### 3.2 Streamlit with Cached Connection

```python
import streamlit as st
import lancedb

@st.cache_resource
def get_database():
    """Cached database connection."""
    return lancedb.connect("./database")

@st.cache_resource
def get_table(_db, table_name):
    """Cached table reference."""
    return _db.open_table(table_name)

db = get_database()
table = get_table(db, "documents")

# Search interface
query = st.text_input("Search query")
if st.button("Search"):
    results = table.search(query).limit(10).to_pandas()
    st.dataframe(results)
```

### 3.3 FastAPI with Lifespan

```python
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import lancedb

# Global database reference
db = None
table = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, table
    db = lancedb.connect("./database")
    table = db.open_table("documents")
    yield
    # Cleanup if needed

app = FastAPI(lifespan=lifespan)

def get_table():
    return table

@app.get("/search")
async def search(query: str, table=Depends(get_table)):
    results = table.search(query).limit(10).to_list()
    return {"results": results}
```

---

## 4. Schema Design Patterns

### 4.1 Multi-Table Design (Code Search)

```python
# Separate tables for different entity types
class Method(LanceModel):
    code: str = model.SourceField()
    vector: Vector(EMBEDDING_DIM) = model.VectorField()
    file_path: str
    class_name: str
    method_name: str
    docstring: str
    references: str  # JSON array of references

class Class(LanceModel):
    source_code: str = model.SourceField()
    vector: Vector(EMBEDDING_DIM) = model.VectorField()
    file_path: str
    class_name: str
    constructor: str
    methods: str  # JSON array of method names

# Create both tables
method_table = db.create_table("methods", schema=Method, on_bad_vectors='drop')
class_table = db.create_table("classes", schema=Class, on_bad_vectors='drop')
```

### 4.2 Metadata-Rich Schema

```python
class Tweet(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()

    # Filterable metadata
    year: int
    month: int
    likes: int
    retweets: int

    # Boolean flags for filtering
    media_present: int  # 0 or 1
    link_present: int   # 0 or 1

    # JSON metadata for flexibility
    metadata: str  # JSON string with additional fields
```

### 4.3 Dynamic Vector Dimension

```python
def create_document_model(embedding_dim: int):
    """Factory for creating schema with dynamic vector dimension."""
    class Document(LanceModel):
        text: str
        vector: Vector(embedding_dim)
        metadata: str = "{}"
    return Document

# Use with any embedding model
model = registry.get("openai").create(name="text-embedding-3-small")
DocumentSchema = create_document_model(model.ndims())
```

---

## 5. Error Handling Patterns

### 5.1 Graceful Table Creation

```python
def get_or_create_table(db, table_name, schema, data=None):
    """Idempotent table creation."""
    if table_name in db.table_names():
        return db.open_table(table_name)

    try:
        table = db.create_table(table_name, schema=schema, mode="overwrite")
        if data is not None:
            table.add(data)
        return table
    except Exception as e:
        # Cleanup on failure
        if table_name in db.table_names():
            db.drop_table(table_name)
        raise e
```

### 5.2 Bad Vector Handling

```python
# Handle invalid embeddings gracefully
table = db.create_table(
    "documents",
    schema=Document,
    mode="overwrite",
    on_bad_vectors='drop'  # Options: 'drop', 'error', 'fill'
)

# Null value preprocessing
df = df.fillna({
    'text': '',
    'category': 'unknown',
    'score': 0.0
})
```

### 5.3 Token Limit Handling

```python
import tiktoken

def clip_to_token_limit(text: str, max_tokens: int = 8000) -> str:
    """Clip text to fit within embedding model token limit."""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
        return encoding.decode(tokens)
    return text
```

---

## 6. Recommended New Sample Categories

Based on this analysis, we should add the following sample types:

### Task Type 1: Initialization (Keep, but enhance)
- Add: Registry-based embedding model initialization
- Add: Cloud storage connection (S3)
- Add: Connection with index creation

### Task Type 2: Data Operations (Enhance significantly)
- Add: Batch embedding with async processing
- Add: Multi-table schema design
- Add: Bad vector handling
- Add: Token limit preprocessing

### Task Type 3: Search (Major enhancements needed)
- Add: Hybrid search with FTS
- Add: Prefilter-based filtering
- Add: Reranking integration
- Add: HYDE pattern

### Task Type 4: Pipeline (Keep, but make realistic)
- Add: Flask/FastAPI integration
- Add: Redis caching layer
- Add: Session management
- Add: Two-stage retrieval

### Task Type 5: Migration (Keep, enhance)
- Add: Index migration
- Add: Schema evolution with new fields
- Add: Embedding model upgrade

### NEW Task Type 6: Advanced Patterns
- Multimodal search (CLIP)
- Graph + Vector hybrid
- Custom reranker implementation
- Streaming responses

---

## 7. Difficulty Calibration

| Difficulty | Current Samples | Should Be |
|------------|-----------------|-----------|
| Easy | Basic connection | Registry-based init, simple search |
| Medium | N/A | Hybrid search, filtering, batch embedding |
| Hard | Basic pipeline | Reranking, HYDE, caching, multi-table |
| Expert | N/A | Multimodal, custom rerankers, production deployment |

---

## 8. Key Code Snippets for Sample Generation

### Snippet 1: Production-Ready Initialization
```python
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
import lancedb
import os

# Environment-based model selection
def get_embedding_model():
    registry = EmbeddingFunctionRegistry.get_instance()

    if os.getenv("OPENAI_API_KEY"):
        return registry.get("openai").create(
            name="text-embedding-3-large",
            max_retries=3
        )
    elif os.getenv("JINA_API_KEY"):
        return registry.get("jina").create(
            name="jina-embeddings-v3",
            max_retries=3
        )
    else:
        return registry.get("sentence-transformers").create(
            name="BAAI/bge-small-en-v1.5"
        )

model = get_embedding_model()

class Document(LanceModel):
    content: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    category: str = ""
    timestamp: str = ""

db = lancedb.connect("./production_db")
table = db.create_table("documents", schema=Document, mode="overwrite")
```

### Snippet 2: Hybrid Search with Reranking
```python
from lancedb.rerankers import RRFReranker, CohereReranker

def hybrid_search(table, query_text: str, query_embedding: list,
                  filter_clause: str = None, top_k: int = 10,
                  use_reranker: bool = True):
    """Production hybrid search with optional reranking."""

    # Build search query
    search = table.search(query_type="hybrid").vector(query_embedding).text(query_text)

    # Apply filtering
    if filter_clause:
        search = search.where(filter_clause, prefilter=True)

    # Apply reranking
    if use_reranker:
        reranker = RRFReranker()  # Or CohereReranker for better quality
        search = search.rerank(reranker)

    # Execute and return
    results = search.limit(top_k).to_pandas()
    return results
```

### Snippet 3: Async Batch Ingestion
```python
import asyncio
from typing import List, Dict
import pandas as pd

async def ingest_documents(
    table,
    documents: List[Dict],
    batch_size: int = 100
) -> int:
    """Batch ingest documents with progress tracking."""

    total_ingested = 0

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]

        # Add batch to table
        table.add(pd.DataFrame(batch))
        total_ingested += len(batch)

        # Yield control for other async tasks
        await asyncio.sleep(0)

    return total_ingested

# Usage
documents = [{"content": "doc1"}, {"content": "doc2"}, ...]
count = asyncio.run(ingest_documents(table, documents))
```

---

## 9. Files to Reference

Key implementation files from the repositories:

1. **Embedding Registry**: `sankalp1999_code_qa/create_tables.py`
2. **Hybrid Search**: `sankalp1999_semantweet-search/app.py`
3. **Reranking**: `ggozad_haiku.rag/haiku/rag/store/repositories/chunk.py`
4. **Async Embeddings**: `sankalp1999_semantweet-search/openai/async_openai_embedding_two.py`
5. **Multimodal**: `ishandutta0098_multimodal-search/src/schema.py`
6. **Flask Integration**: `sankalp1999_code_qa/app.py`
7. **Streamlit**: `ishandutta0098_multimodal-search/src/app.py`
8. **HYDE Pattern**: `sankalp1999_code_qa/app.py` (openai_hyde function)

---

## 10. Recommendations for SDKBench

### Immediate Actions
1. **Update init samples** to use `EmbeddingFunctionRegistry`
2. **Add hybrid search samples** with FTS index creation
3. **Add filtering samples** with dynamic WHERE clause building
4. **Add reranking samples** with multiple reranker options

### Medium-Term
1. Create async batch embedding samples
2. Add Flask/FastAPI integration samples
3. Add multi-table schema samples
4. Add HYDE retrieval pattern

### Long-Term
1. Multimodal search samples
2. Production deployment patterns
3. Custom reranker implementation
4. Graph + Vector hybrid samples

---

*This document should be used as a reference when generating new LanceDB benchmark samples to ensure they reflect real-world usage patterns.*
