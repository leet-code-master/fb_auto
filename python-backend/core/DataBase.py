from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

SQLITE_DB_URL = "sqlite:///./tasks.db"
engine = create_engine(SQLITE_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_all_tables():
    # 关键：导入所有定义了Base的模块，注册所有表
    from api.modules.worker import models
    Base.metadata.create_all(bind=engine)