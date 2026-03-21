import psycopg2

conn = psycopg2.connect(
    host='seekingspgfld.postgres.database.azure.com',
    user='ssadmin',
    password='72430814Stl.',
    port=5432,
    dbname='postgres',
    sslmode='require'
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("SELECT datname FROM pg_database WHERE datname = 'missouriconstruction'")
row = cur.fetchone()
if row:
    print("DATABASE ALREADY EXISTS: missouriconstruction")
else:
    print("NOT FOUND — creating database: missouriconstruction")
    cur.execute("CREATE DATABASE missouriconstruction")
    print("DATABASE CREATED SUCCESSFULLY.")

# List all databases on server
cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname")
print("\nAll databases on seekingspgfld server:")
for r in cur.fetchall():
    print(f"  - {r[0]}")

cur.close()
conn.close()
