"""LanceDB with S3 cloud storage."""

import os
import lancedb

# AWS credentials should be set via environment variables:
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

def get_cloud_database():
    """Connect to LanceDB on S3."""
    bucket = os.environ.get("S3_BUCKET", "my-lancedb-bucket")
    prefix = os.environ.get("S3_PREFIX", "lancedb")
    s3_uri = f"s3://{bucket}/{prefix}"
    return lancedb.connect(s3_uri)

# Initialize cloud database
db = get_cloud_database()

def main():
    tables = db.table_names()
    print(f"Connected to cloud LanceDB")
    print(f"Tables: {tables}")
    print("Cloud database ready")

if __name__ == "__main__":
    main()
