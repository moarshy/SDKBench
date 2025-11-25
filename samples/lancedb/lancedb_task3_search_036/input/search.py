"""Filtered search with projections."""

# TODO: Import lancedb

def search_with_select(query_vector, k: int = 10):
    """Search with column selection.

    TODO:
        1. Perform vector search
        2. Use .select(["text", "category"]) to limit columns
        3. Use .where() for filtering
        4. Use .metric("cosine") for distance metric
        5. Return results with only selected columns
    """
    pass

def main():
    # TODO: Search with projections
    print("Filtered search complete")

if __name__ == "__main__":
    main()
