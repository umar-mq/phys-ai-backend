from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Ensure the URL is compatible with SQLAlchemy (postgres:// -> postgresql://)
db_url = settings.DATABASE_URL
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url) if db_url else None

def init_db():
    """Creates tables if they don't exist."""
    if engine:
        SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for DB session."""
    if not engine:
        raise RuntimeError("DATABASE_URL is not set.")
    with Session(engine) as session:
        yield session