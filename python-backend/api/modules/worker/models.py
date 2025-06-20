from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON, ForeignKey
from datetime import datetime
from .schema import TaskStatus

Base = declarative_base()


class BatchTaskORM(Base):
    __tablename__ = "batch_task"
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, default=datetime.now)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)


class AccountTaskORM(Base):
    __tablename__ = "account_task"
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batch_task.id"))
    username = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    create_time = Column(DateTime, default=datetime.now)
    complete_time = Column(DateTime, nullable=True)
    account_info = Column(JSON, nullable=True)
    execution_modules = Column(JSON, nullable=True)
    browser_type = Column(String, nullable=True)
    thread_id = Column(Integer, nullable=True)
