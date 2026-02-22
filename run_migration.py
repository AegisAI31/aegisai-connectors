"""
Migration script to apply KAN-14 Reports & Audit schema
Run this to create the tables in the AegisAI database
"""
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    # Parse DATABASE_URL
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:Jatinder%4012@localhost:5432/AegisAI")
    db_url = db_url.replace("postgresql+psycopg://", "")
    
    # Extract connection details
    auth, host_db = db_url.split("@")
    user, password = auth.split(":")
    host_port, database = host_db.split("/")
    host = host_port.split(":")[0]
    port = host_port.split(":")[1] if ":" in host_port else "5432"
    
    # Decode password
    password = password.replace("%40", "@")
    
    print(f"Connecting to database: {database} on {host}:{port}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read migration file
        with open("migrations/001_kan14_reports_audit.sql", "r") as f:
            migration_sql = f.read()
        
        print("Executing migration...")
        cursor.execute(migration_sql)
        
        print("✓ Migration completed successfully!")
        print("✓ Created tables: trust_reports, audit_trails, deletion_logs")
        print("✓ Created enums: report_status, report_type, action_type")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
