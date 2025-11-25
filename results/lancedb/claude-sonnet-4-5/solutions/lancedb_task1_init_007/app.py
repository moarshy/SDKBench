# filepath: app.py
"""LanceDB with S3 cloud storage."""

import os
import lancedb

# Configure AWS credentials via environment variables
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
# These should be set in your environment before running the script

def get_cloud_database():
    """Connect to LanceDB on S3.
    
    Returns:
        lancedb.DBConnection: Connection to LanceDB on S3
        
    Raises:
        ValueError: If required environment variables are not set
        Exception: If connection fails
    """
    # Verify AWS credentials are configured
    required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION"
        )
    
    # Build S3 URI: s3://bucket/path
    # You can customize these values or make them environment variables
    bucket_name = os.getenv('S3_BUCKET', 'my-lancedb-bucket')
    path = os.getenv('S3_PATH', 'lancedb')
    s3_uri = f"s3://{bucket_name}/{path}"
    
    try:
        # Connect to LanceDB with S3 path
        # LanceDB will use the AWS credentials from environment variables
        db = lancedb.connect(s3_uri)
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
        
        # Additional verification: check if we can create a simple table
        # This is optional but helps ensure write permissions work
        test_table_name = "_connection_test"
        if test_table_name not in tables:
            import pandas as pd
            test_data = pd.DataFrame({
                'id': [1],
                'text': ['connection test']
            })
            db.create_table(test_table_name, test_data, mode='overwrite')
            print(f"Created test table '{test_table_name}' successfully")
        
        print("Cloud database ready")
        return db
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nTo use S3 storage, set these environment variables:")
        print("  export AWS_ACCESS_KEY_ID='your-access-key'")
        print("  export AWS_SECRET_ACCESS_KEY='your-secret-key'")
        print("  export AWS_REGION='us-east-1'")
        print("  export S3_BUCKET='your-bucket-name'  # optional")
        print("  export S3_PATH='lancedb'  # optional")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    main()