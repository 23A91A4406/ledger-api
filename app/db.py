from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy import event
import os

# ---------- DATABASE URL ----------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin123@db:5432/ledger_db"  # <-- change db -> localhost
)

# ---------- ENGINE ----------

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# ---------- SESSION ----------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ---------- BASE ----------

Base = declarative_base()

# ---------- ENFORCE FOREIGN KEYS (Postgres-safe) ----------

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # This hook exists for compatibility; no-op for PostgreSQL
    pass


# ---------- DEPENDENCY ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
