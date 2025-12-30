from sqlalchemy import text
from db import engine

def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT now();"))
        print("✅ DB connected. Time:", result.fetchone())

if __name__ == "__main__":
    test_connection()
