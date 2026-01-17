# db/database_connection.py
import time
from sqlalchemy import create_engine, inspect, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from typing import Generator
from settings import get_settings, setup_logging

settings = get_settings()
logger = setup_logging("database", "database.log")

# Create engine with logging
engine = create_engine(
    settings.database_url,
    echo=False,  # We'll use custom logging
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20
)

# create session
session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

#inspector
inspector = inspect(engine)

# Event listeners for query logging
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug(f"Start Query: {statement}")
    logger.debug(f"Parameters: {parameters}")

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    logger.debug(f"Query Complete in {total:.3f}s")
    
    if total > 1.0:  # Warn on slow queries
        logger.warning(f"SLOW QUERY ({total:.3f}s): {statement[:100]}...")
        
def get_db() -> Generator[Session, None, None]:
    """Get a database session with logging"""
    db = session()
    logger.debug("Database session created")
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")