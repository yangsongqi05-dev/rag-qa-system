import json
from sqlalchemy import create_engine

from sqlalchemy.orm import Session
from src.config import DB_URL
from src.db.models import Base,QaRecord
engine = create_engine(DB_URL,echo=False)
Base.metadata.create_all(engine)
def save_qa(question,answer,sources):
    """存一条问答记录"""
    with Session(engine) as s:
        s.add(QaRecord(question=question,answer=answer,sources=sources))
        s.commit()
def recent(limit=20):
    with Session(engine) as s:
        rows = s.query(QaRecord).order_by(QaRecord.id.desc()).limit(limit).all()
        return [
            {'id':r.id,'question':r.question,'answer':r.answer,
             'sources':r.sources,'created_at':str(r.created_at)} for r in rows
        ]


















