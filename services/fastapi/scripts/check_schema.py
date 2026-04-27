"""Check if migration 001/002 columns already exist"""
import asyncio
import asyncpg

DB_URL = "postgresql://postgres.denpygmjfloijyinzanx:CareRemind2024SecureDB@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"

async def check():
    conn = await asyncpg.connect(DB_URL, ssl="require")
    
    # Check 001: phone_hash in patients
    r = await conn.fetchrow(
        "SELECT column_name FROM information_schema.columns WHERE table_name='patients' AND column_name='phone_hash'"
    )
    print(f"001 - patients.phone_hash exists: {bool(r)}")

    # Check 002: street in tenants
    r2 = await conn.fetchrow(
        "SELECT column_name FROM information_schema.columns WHERE table_name='tenants' AND column_name='street'"
    )
    print(f"002 - tenants.street exists: {bool(r2)}")

    # Check 003: clinic_locations table exists
    r3 = await conn.fetchrow(
        "SELECT table_name FROM information_schema.tables WHERE table_name='clinic_locations' AND table_schema='public'"
    )
    print(f"003 - clinic_locations table exists: {bool(r3)}")

    await conn.close()

asyncio.run(check())
