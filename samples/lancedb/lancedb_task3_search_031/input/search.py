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
