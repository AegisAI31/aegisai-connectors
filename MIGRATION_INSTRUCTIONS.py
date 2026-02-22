"""
Simplified migration script - Run SQL directly in pgAdmin
"""

print("""
=== KAN-14 Migration Instructions ===

1. Open pgAdmin 4
2. Connect to your PostgreSQL server
3. Select the 'AegisAI' database
4. Open Query Tool (Tools > Query Tool)
5. Open the file: migrations/001_kan14_reports_audit.sql
6. Click Execute (F5)

The migration will create:
- trust_reports table
- audit_trails table  
- deletion_logs table
- All ENUMs and indexes

Alternative: Copy the SQL from migrations/001_kan14_reports_audit.sql
and paste it directly into pgAdmin Query Tool.
""")
