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
        print(f"✓ Connected to LanceDB at: ./lancedb_data")
        
        # Test embedding generation with sample data
        sample_docs = [
            {"text": "LanceDB is a vector database"},
            {"text": "Sentence transformers create embeddings"},
            {"text": "Python is a programming language"}
        ]
        
        # Create or recreate the table with the Document schema
        table_name = "documents"
        
        # Check if table exists and drop it for fresh start
        if table_name in db.table_names():
            db.drop_table(table_name)
            print(f"✓ Dropped existing table: {table_name}")
        
        # Create table with schema
        table = db.create_table(table_name, schema=Document)
        print(f"✓ Created table: {table_name}")
        
        # Add sample documents (embeddings will be generated automatically)
        table.add(sample_docs)
        print(f"✓ Added {len(sample_docs)} documents with auto-generated embeddings")
        
        # Verify the data
        results = table.to_pandas()
        print(f"✓ Table contains {len(results)} rows")
        print(f"✓ Vector dimension: {model.ndims()}")
        
        # Test a simple search
        query_text = "database technology"
        search_results = table.search(query_text).limit(2).to_pandas()
        print(f"\n✓ Search test successful - found {len(search_results)} results for: '{query_text}'")
        print("\nTop result:")
        print(f"  Text: {search_results.iloc[0]['text']}")
        print(f"  Distance: {search_results.iloc[0]['_distance']:.4f}")
        
        print("\nSentence transformer pipeline ready")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()