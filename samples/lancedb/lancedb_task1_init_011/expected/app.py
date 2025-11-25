"""Multi-tenant LanceDB with tenant isolation."""

from pathlib import Path
import lancedb

BASE_PATH = "./tenants"

def get_tenant_db(tenant_id: str):
    """Get isolated database for tenant."""
    tenant_path = Path(BASE_PATH) / tenant_id / "db"
    tenant_path.parent.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(str(tenant_path))

def list_tenants():
    """List all tenant databases."""
    base = Path(BASE_PATH)
    if not base.exists():
        return []
    return [d.name for d in base.iterdir() if d.is_dir()]

def main():
    # Create tenant databases
    tenant_a = get_tenant_db("tenant_a")
    tenant_b = get_tenant_db("tenant_b")

    # Verify isolation
    print(f"Tenant A tables: {tenant_a.table_names()}")
    print(f"Tenant B tables: {tenant_b.table_names()}")
    print(f"All tenants: {list_tenants()}")
    print("Multi-tenant system ready")

if __name__ == "__main__":
    main()
