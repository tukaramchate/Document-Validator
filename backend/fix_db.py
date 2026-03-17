import psycopg

conn = psycopg.connect("postgresql://postgres:1206@localhost:5432/document_validator")
try:
    conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT TRUE")
    conn.commit()
    print("Database updated: Added is_approved to users")
except Exception as e:
    print(f"Error updating database: {e}")
finally:
    conn.close()
