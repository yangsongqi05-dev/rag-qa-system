from sqlalchemy.orm import declarative_base
from sqlalchemy import Column,Integer,Text,DateTime,func
Base = declarative_base()
class QaRecord(Base):
    __tablename__ = 'qa_history'
    id = Column(Integer,primary_key=True,autoincrement=True)
    question = Column(Text,nullable=False)
    answer = Column(Text)
    sources=Column(Text)
    created_at = Column(DateTime,default=func.now())




















