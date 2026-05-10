import os
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func

DB_URL = os.getenv('DB_URL','postgresql+psycopg2://app:app@localhost:5432/arxiv')
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'

    job_id = Column(String, primary_key=True)
    chat_id = Column(String, nullable=False)
    arxiv_id = Column(String, nullable=False)

    status = Column(String, default='queued')

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

def init_db():
    Base.metadata.create_all(bind=engine)
    print('[DB] Initialized')


def create_job(job_id, chat_id, arxiv_id):
    db = SessionLocal()
    try:
        job = Job(
            job_id=job_id,
            chat_id=str(chat_id),
            arxiv_id=arxiv_id,
            status='processing'
        )
        db.add(job)
        db.commit()
    finally:
        db.close()


def update_job(job_id, **kwargs):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return
        for k, v in kwargs.items():
            setattr(job, k, v)
        db.commit()
    finally:
        db.close()


def get_job(job_id):
    db = SessionLocal()
    try:
        return db.query(Job).filter(Job.job_id == job_id).first()
    finally:
        db.close()


def get_all_jobs(limit=10):
    db = SessionLocal()
    try:
        return (
            db.query(Job)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()