# filepath: data_ops.py
"""Full data validation pipeline."""

from typing import Optional, List, Dict, Any
from pydantic import field_validator, ValidationError
import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np


# Define schema with validators
class Document(LanceModel):
    text: str
    vector: Vector(384)
    category: str

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("text cannot be empty")
        return v.strip()

    @field_validator("category")
    @classmethod
    def valid_category(cls, v):
        allowed = ["tech", "science", "business"]
        if v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v


def validate_and_insert(table, documents: List[dict]) -> Dict[str, Any]:
    """Validate documents before insertion.

    Args:
        table: LanceDB table to insert into
        documents: List of document dictionaries to validate and insert

    Returns:
        Dictionary containing:
            - valid_count: Number of successfully validated documents
            - invalid_count: Number of failed validations
            - errors: List of validation errors with document indices
    """
    valid_documents = []
    errors = []

    # Validate each document against schema
    for idx, doc in enumerate(documents):
        try:
            # Validate document using Pydantic model
            validated_doc = Document(**doc)
            valid_documents.append(validated_doc)
        except ValidationError as e:
            # Collect validation errors with document index
            error_details = {
                "document_index": idx,
                "document": doc,
                "errors": []
            }
            for error in e.errors():
                error_details["errors"].append({
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"]
                })
            errors.append(error_details)
        except Exception as e:
            # Handle unexpected errors
            errors.append({
                "document_index": idx,
                "document": doc,
                "errors": [{
                    "field": "unknown",
                    "message": str(e),
                    "type": "unexpected_error"
                }]
            })

    # Insert valid documents if any exist
    inserted_count = 0
    if valid_documents:
        try:
            table.add([doc.dict() for doc in valid_documents])
            inserted_count = len(valid_documents)
            print(f"✓ Successfully inserted {inserted_count} valid documents")
        except Exception as e:
            print(f"✗ Error inserting documents: {e}")
            # Add insertion error to errors list
            errors.append({
                "document_index": "bulk_insert",
                "document": None,
                "errors": [{
                    "field": "insertion",
                    "message": f"Failed to insert valid documents: {str(e)}",
                    "type": "insertion_error"
                }]
            })

    return {
        "valid_count": inserted_count,
        "invalid_count": len(errors),
        "errors": errors
    }


def main():
    """Main function to demonstrate data validation pipeline."""
    
    # Connect to LanceDB
    db = lancedb.connect("./validation_demo")
    
    # Create table with schema
    try:
        # Drop table if it exists for clean demo
        try:
            db.drop_table("documents")
        except:
            pass
        
        # Create new table with schema
        table = db.create_table(
            "documents",
            schema=Document,
            mode="create"
        )
        print("✓ Created table with schema")
    except Exception as e:
        print(f"✗ Error creating table: {e}")
        return

    # Create documents with some invalid data for testing
    documents = [
        {
            # Valid document
            "text": "Machine learning advances in 2024",
            "vector": np.random.rand(384).tolist(),
            "category": "tech"
        },
        {
            # Invalid: empty text
            "text": "   ",
            "vector": np.random.rand(384).tolist(),
            "category": "science"
        },
        {
            # Valid document
            "text": "Quantum computing breakthrough",
            "vector": np.random.rand(384).tolist(),
            "category": "science"
        },
        {
            # Invalid: wrong category
            "text": "Stock market analysis",
            "vector": np.random.rand(384).tolist(),
            "category": "finance"
        },
        {
            # Invalid: missing vector
            "text": "AI ethics discussion",
            "category": "tech"
        },
        {
            # Invalid: wrong vector dimension
            "text": "Blockchain technology",
            "vector": np.random.rand(128).tolist(),  # Wrong dimension
            "category": "tech"
        },
        {
            # Valid document
            "text": "Business strategy for startups",
            "vector": np.random.rand(384).tolist(),
            "category": "business"
        },
        {
            # Invalid: empty text and wrong category
            "text": "",
            "vector": np.random.rand(384).tolist(),
            "category": "invalid"
        }
    ]

    print(f"\n{'='*60}")
    print(f"Validating {len(documents)} documents...")
    print(f"{'='*60}\n")

    # Validate and insert documents
    results = validate_and_insert(table, documents)

    # Report results
    print(f"\n{'='*60}")
    print("VALIDATION RESULTS")
    print(f"{'='*60}")
    print(f"✓ Valid documents inserted: {results['valid_count']}")
    print(f"✗ Invalid documents rejected: {results['invalid_count']}")
    
    if results['errors']:
        print(f"\n{'='*60}")
        print("VALIDATION ERRORS")
        print(f"{'='*60}")
        for error_info in results['errors']:
            doc_idx = error_info['document_index']
            print(f"\nDocument #{doc_idx}:")
            if error_info['document']:
                print(f"  Text: {error_info['document'].get('text', 'N/A')[:50]}...")
                print(f"  Category: {error_info['document'].get('category', 'N/A')}")
            print("  Errors:")
            for err in error_info['errors']:
                print(f"    - {err['field']}: {err['message']}")

    # Verify inserted data
    print(f"\n{'='*60}")
    print("VERIFICATION")
    print(f"{'='*60}")
    try:
        count = table.count_rows()
        print(f"Total rows in table: {count}")
        
        if count > 0:
            # Show sample of inserted data
            sample = table.to_pandas().head(3)
            print(f"\nSample of inserted documents:")
            for idx, row in sample.iterrows():
                print(f"  {idx + 1}. {row['text'][:50]}... (category: {row['category']})")
    except Exception as e:
        print(f"✗ Error verifying data: {e}")

    print(f"\n{'='*60}")
    print("Validation complete")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()