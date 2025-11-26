```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
boto3>=1.28.0
```

```python
# filepath: app.py
"""LanceDB with S3 cloud storage."""

import os
import lancedb

# Configure AWS credentials via environment variables
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

def get_cloud_database():
    """Connect to LanceDB on S3.
    
    Returns:
        lancedb.DBConnection: Connection to LanceDB on S3
        
    Raises:
        ValueError: If required environment variables are not set
        Exception: If connection to S3 fails
    """
    # Verify AWS credentials are configured
    required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        )
    
    # Get S3 configuration from environment
    bucket = os.getenv('S3_BUCKET', 'my-lancedb-bucket')
    path = os.getenv('S3_PATH', 'lancedb')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    # Build S3 URI
    s3_uri = f"s3://{bucket}/{path}"
    
    try:
        # Connect to LanceDB with S3 path
        # LanceDB will use boto3 to access S3 with credentials from environment
        db = lancedb.connect(
            s3_uri,
            storage_options={
                "region": region,
                "aws_access_key_id": os.getenv('AWS_ACCESS_KEY_ID'),
                "aws_secret_access_key": os.getenv('AWS_SECRET_ACCESS_KEY'),
            }
        )
        
        print(f"Successfully connected to LanceDB at {s3_uri}")
        return db
        
    except Exception as e:
        raise Exception(f"Failed to connect to LanceDB on S3: {str(e)}")

def main():
    """Initialize and verify cloud database connection."""
    try:
        # Initialize cloud database
        db = get_cloud_database()
        
        # Verify connection by listing tables
        tables = db.table_names()
        print(f"Connected successfully. Found {len(tables)} table(s): {tables}")
        
        print("Cloud database ready")
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nTo use S3 storage, set the following environment variables:")
        print("  export AWS_ACCESS_KEY_ID='your-access-key'")
        print("  export AWS_SECRET_ACCESS_KEY='your-secret-key'")
        print("  export AWS_REGION='us-east-1'  # optional, defaults to us-east-1")
        print("  export S3_BUCKET='your-bucket'  # optional, defaults to my-lancedb-bucket")
        print("  export S3_PATH='lancedb'  # optional, defaults to lancedb")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```