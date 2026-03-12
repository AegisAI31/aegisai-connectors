import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, dbname="AegisAI",
    user="postgres", password="Jatinder@12"
)
conn.set_isolation_level(0)  # AUTOCOMMIT
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS request_latency (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID,
        endpoint VARCHAR(100) NOT NULL,
        latency_ms FLOAT NOT NULL,
        status_code INTEGER NOT NULL DEFAULT 200,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_rl_user_created ON request_latency(user_id, created_at DESC)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_rl_created ON request_latency(created_at DESC)")

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
print("Tables:", [r[0] for r in cur.fetchall()])

cur.close()
conn.close()
print("OK")
