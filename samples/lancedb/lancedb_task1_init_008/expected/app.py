"""Multi-tenant LanceDB setup."""

import os
import lancedb
from pathlib import Path

BASE_PATH = "./tenants"

def get_tenant_db(tenant_id: str):
    """Get database for specific tenant."""
    tenant_path = f"{BASE_PATH}/{tenant_id}/db"
    Path(tenant_path).parent.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(tenant_path)

def create_tenant(tenant_id: str):
    """Create new tenant database."""
    db = get_tenant_db(tenant_id)
    # Initialize with default table
    data = [{"text": "welcome", "vector": [0.0] * 384}]
    db.create_table("documents", data, mode="overwrite")
    return db

def main():
    """Multi-tenant main."""
    # Example: create tenant
    tenant_db = create_tenant("tenant_001")
    print(f"Tenant database ready with {len(tenant_db.table_names())} tables")
    print("Multi-tenant system ready")

if __name__ == "__main__":
    main()
