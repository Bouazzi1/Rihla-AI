"""Script temporaire pour créer la base rihla_ai."""
import asyncio
import asyncpg
import sys

async def create_db():
    try:
        conn = await asyncio.wait_for(
            asyncpg.connect(
                user='postgres',
                password='postgres',
                host='localhost',
                port=5432,
                database='postgres',
            ),
            timeout=5,
        )
        try:
            await conn.execute('CREATE DATABASE rihla_ai')
            print('✅ Database rihla_ai created!')
        except asyncpg.DuplicateDatabaseError:
            print('ℹ️ Database rihla_ai already exists!')
        finally:
            await conn.close()
    except asyncio.TimeoutError:
        print('❌ Connection timeout — check PostgreSQL credentials')
        sys.exit(1)
    except Exception as e:
        print(f'❌ Error: {e}')
        sys.exit(1)

asyncio.run(create_db())
