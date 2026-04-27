"""
check_supabase_connection.py
Run from: services/fastapi/
    python scripts/check_supabase_connection.py
"""

import asyncio
import sys
from pathlib import Path

# Make sure app imports resolve from services/fastapi/
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load .env from repo root
from dotenv import load_dotenv
env_path = BASE_DIR.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK]  Loaded .env from {env_path}")
else:
    print(f"[WRN] .env not found at {env_path}, using system environment")

from app.core.config import settings

print()
print("=" * 60)
print("  CareRemind -- Supabase Connection Checker")
print("=" * 60)

# 1. Print resolved config values
print()
print("[1] Resolved environment values")
db_url_masked = settings.DATABASE_URL
if "@" in db_url_masked:
    pre, post = db_url_masked.split("@", 1)
    scheme, creds = pre.split("://", 1)
    user = creds.split(":")[0]
    db_url_masked = f"{scheme}://{user}:****@{post}"
print(f"    ENVIRONMENT   : {settings.ENVIRONMENT}")
print(f"    DATABASE_URL  : {db_url_masked}")
print(f"    SUPABASE_URL  : {settings.SUPABASE_URL or '(empty)'}")
print(f"    SUPABASE_KEY  : {'(set)' if settings.SUPABASE_KEY else '(empty)'}")

# 2. Test PostgreSQL connection via asyncpg
print()
print("[2] Testing PostgreSQL connection via asyncpg ...")

async def test_db():
    try:
        import asyncpg
    except ImportError:
        print("    [ERR] asyncpg not installed. Run: pip install asyncpg")
        return False

    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    try:
        conn = await asyncio.wait_for(
            asyncpg.connect(url, ssl="require"),
            timeout=15
        )
        row = await conn.fetchrow("SELECT current_database(), current_user, version()")
        await conn.close()
        print(f"    [OK]  Connected!")
        print(f"          Database : {row['current_database']}")
        print(f"          User     : {row['current_user']}")
        print(f"          PG ver   : {str(row['version'])[:70]}")
        return True
    except asyncio.TimeoutError:
        print("    [ERR] Connection timed out (15s). Check host/firewall.")
        return False
    except Exception as e:
        print(f"    [ERR] Connection failed: {e}")
        return False

db_ok = asyncio.run(test_db())

# 3. Test Supabase SDK
print()
print("[3] Testing Supabase REST API (supabase-py SDK) ...")

def test_supabase_sdk():
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("    [SKP] SUPABASE_URL or SUPABASE_KEY not set -- skipping.")
        return None
    try:
        from supabase import create_client
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        res = client.storage.list_buckets()
        bucket_names = [b.name for b in res] if res else []
        print(f"    [OK]  Supabase SDK connected!")
        print(f"          Buckets  : {bucket_names if bucket_names else '(none yet)'}")
        return True
    except Exception as e:
        print(f"    [ERR] Supabase SDK error: {e}")
        return False

sdk_ok = test_supabase_sdk()

# Summary
print()
print("=" * 60)
print("  Summary")
print("=" * 60)
pg_status  = "[OK]  PASS" if db_ok else "[ERR] FAIL"
sdk_status = "[OK]  PASS" if sdk_ok else ("[SKP] Skipped" if sdk_ok is None else "[ERR] FAIL")
print(f"  PostgreSQL (asyncpg) : {pg_status}")
print(f"  Supabase SDK         : {sdk_status}")
print()
if db_ok:
    print("  Your Supabase DB is reachable. Safe to run Alembic:")
    print()
    print("    alembic upgrade head")
else:
    print("  Fix the PostgreSQL connection before running migrations.")
print()
