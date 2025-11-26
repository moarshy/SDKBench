# filepath: app.py
"""Multi-tenant LanceDB with tenant isolation."""

from pathlib import Path
import lancedb
from typing import List, Optional

BASE_PATH = "./tenants"

def get_tenant_db(tenant_id: str):
    """Get isolated database for tenant.

    Args:
        tenant_id: Unique tenant identifier

    Returns:
        lancedb.DBConnection: Connection to tenant's isolated database
    
    Raises:
        ValueError: If tenant_id is empty or invalid
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id cannot be empty")
    
    # Sanitize tenant_id to prevent path traversal attacks
    safe_tenant_id = "".join(c for c in tenant_id if c.isalnum() or c in ('-', '_'))
    if not safe_tenant_id:
        raise ValueError("tenant_id must contain alphanumeric characters")
    
    # Build tenant-specific path: {BASE_PATH}/{tenant_id}/db
    tenant_path = Path(BASE_PATH) / safe_tenant_id / "db"
    
    # Create directory if needed
    tenant_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to tenant database
    db = lancedb.connect(str(tenant_path))
    
    return db

def list_tenants() -> List[str]:
    """List all tenant databases.

    Returns:
        List[str]: List of tenant IDs that have databases
    """
    base_path = Path(BASE_PATH)
    
    # Return empty list if base path doesn't exist
    if not base_path.exists():
        return []
    
    # Scan BASE_PATH directory for tenant folders
    tenants = []
    for tenant_dir in base_path.iterdir():
        if tenant_dir.is_dir():
            # Check if it has a db subdirectory (actual database)
            db_path = tenant_dir / "db"
            if db_path.exists():
                tenants.append(tenant_dir.name)
    
    return sorted(tenants)

def create_sample_table(db: lancedb.DBConnection, tenant_id: str) -> None:
    """Create a sample table in the tenant database for verification.
    
    Args:
        db: Database connection
        tenant_id: Tenant identifier for sample data
    """
    import pandas as pd
    
    # Create sample data
    data = pd.DataFrame({
        "id": [1, 2, 3],
        "tenant": [tenant_id] * 3,
        "vector": [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]],
        "text": [f"{tenant_id}_doc1", f"{tenant_id}_doc2", f"{tenant_id}_doc3"]
    })
    
    # Create table
    table = db.create_table("documents", data, mode="overwrite")
    print(f"  Created table 'documents' with {len(data)} records")

def verify_isolation() -> None:
    """Verify that tenant databases are properly isolated."""
    print("\nVerifying tenant isolation:")
    
    # Create databases for two different tenants
    tenant1_db = get_tenant_db("tenant_1")
    tenant2_db = get_tenant_db("tenant_2")
    
    # Create sample tables
    print("  Creating sample data for tenant_1...")
    create_sample_table(tenant1_db, "tenant_1")
    
    print("  Creating sample data for tenant_2...")
    create_sample_table(tenant2_db, "tenant_2")
    
    # Verify isolation by checking table lists
    tenant1_tables = tenant1_db.table_names()
    tenant2_tables = tenant2_db.table_names()
    
    print(f"\n  Tenant 1 tables: {tenant1_tables}")
    print(f"  Tenant 2 tables: {tenant2_tables}")
    
    # Verify data isolation
    tenant1_table = tenant1_db.open_table("documents")
    tenant2_table = tenant2_db.open_table("documents")
    
    tenant1_data = tenant1_table.to_pandas()
    tenant2_data = tenant2_table.to_pandas()
    
    print(f"\n  Tenant 1 has {len(tenant1_data)} records")
    print(f"  Tenant 2 has {len(tenant2_data)} records")
    
    # Verify tenant-specific data
    assert all(tenant1_data['tenant'] == 'tenant_1'), "Tenant 1 data contaminated!"
    assert all(tenant2_data['tenant'] == 'tenant_2'), "Tenant 2 data contaminated!"
    
    print("\n  ✓ Isolation verified: Each tenant has separate data")

def main():
    """Main function to demonstrate multi-tenant system."""
    print("=" * 60)
    print("Multi-tenant LanceDB System")
    print("=" * 60)
    
    try:
        # Create tenant databases
        print("\n1. Creating tenant databases...")
        tenant1_db = get_tenant_db("tenant_1")
        print(f"  ✓ Created database for tenant_1 at: {BASE_PATH}/tenant_1/db")
        
        tenant2_db = get_tenant_db("tenant_2")
        print(f"  ✓ Created database for tenant_2 at: {BASE_PATH}/tenant_2/db")
        
        tenant3_db = get_tenant_db("tenant_3")
        print(f"  ✓ Created database for tenant_3 at: {BASE_PATH}/tenant_3/db")
        
        # List all tenants
        print("\n2. Listing all tenants...")
        tenants = list_tenants()
        print(f"  Found {len(tenants)} tenant(s): {tenants}")
        
        # Verify isolation
        print("\n3. Verifying tenant isolation...")
        verify_isolation()
        
        # Final summary
        print("\n" + "=" * 60)
        print("Multi-tenant system ready ✓")
        print("=" * 60)
        print(f"\nTotal tenants: {len(list_tenants())}")
        print(f"Base path: {Path(BASE_PATH).absolute()}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise

if __name__ == "__main__":
    main()