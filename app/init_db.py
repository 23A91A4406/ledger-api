from app.db import engine, Base
import app.models  # IMPORTANT: ensures models are registered

def init_db():
    print("📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")

if __name__ == "__main__":
    init_db()
