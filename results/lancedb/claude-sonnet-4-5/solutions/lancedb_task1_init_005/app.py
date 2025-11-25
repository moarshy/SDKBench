# filepath: app.py
"""LanceDB with Sentence Transformers via EmbeddingFunctionRegistry."""

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

# Get registry instance and create sentence-transformers model
registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("sentence-transformers").create(name="all-MiniLM-L6-v2")

# Define Document schema with auto-embedding
class Document(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()

def get_database():
    """Initialize database with sentence transformer embeddings.

    Returns:
        lancedb.DBConnection: Connected database instance
    """
    try:
        # Connect to LanceDB (creates directory if it doesn't exist)
        db = lancedb.connect("./lancedb_data")
        return db
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

def main():
    """Main function to initialize and test the database."""
    try:
        # Initialize database
        db = get_database()
        print(f"✓ Database connected successfully at: {db.uri}")
        
        # Test embedding generation with sample data
        sample_docs = [
            {"text": "LanceDB is a vector database"},
            {"text": "Sentence transformers create embeddings"},
            {"text": "Python is a programming language"}
        ]
        
        # Create or recreate table with schema
        table_name = "documents"
        
        # Drop table if it exists (for clean initialization)
        if table_name in db.table_names():
            db.drop_table(table_name)
            print(f"✓ Dropped existing table: {table_name}")
        
        # Create table with Document schema
        table = db.create_table(table_name, schema=Document)
        print(f"✓ Created table: {table_name}")
        
        # Add sample documents (embeddings will be generated automatically)
        table.add(sample_docs)
        print(f"✓ Added {len(sample_docs)} documents with auto-generated embeddings")
        
        # Verify data was inserted
        count = table.count_rows()
        print(f"✓ Table contains {count} rows")
        
        # Test a simple search
        query_text = "database technology"
        results = table.search(query_text).limit(2).to_pandas()
        print(f"\n✓ Search results for '{query_text}':")
        print(results[['text']].to_string(index=False))
        
        print("\n✓ Sentence transformer pipeline ready")
        
    except Exception as e:
        print(f"✗ Error in main: {e}")
        raise

if __name__ == "__main__":
    main()