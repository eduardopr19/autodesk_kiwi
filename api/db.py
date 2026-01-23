from contextlib import contextmanager
from sqlmodel import SQLModel, create_engine, Session
from config import get_settings

settings = get_settings()
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.debug
)

def init_db() -> None:
    """Crée toutes les tables"""
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    """Context manager pour sessions DB"""
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()