import re
from sqlalchemy import text
from src.db.history import engine
from langchain_core.tools import tool
from src.config import TOP_K
from src.core import retriever
ALLOWED_TABLES = {'book', 'qa_history'}
@tool
def search_knowledge(query:str) ->str:
    """在数据库课程知识库里检索资料。
       当用户问到 MySQL、数据库、索引、事务、锁、存储引擎、性能优化等
       数据库相关问题时，先用这个工具查资料，再根据查到的内容回答。
       Args:
           query: 要检索的问题，用一句完整的话描述
       """
    results = retriever.search_rerank(query, TOP_K)
    if not results:
        return "知识库没有找到相关资料"
    return '\n\n'.join('【相关度%.3f】%s'%(s,t)for s,t in results)

@tool
def query_database(sql:str) ->str:
    """查询数据库并返回结果。传入一条 SELECT 语句，只能查询不能修改。
        可查询的表：
        - book(id, bookname, author, price, publisher, create_time, update_time)
        - qa_history(id, question, answer, sources, created_at)
    """
    clean = sql.strip().rstrip(';').strip()
    if not clean.upper().startswith('SELECT'):
        return '拒绝执行：只允许SELECT查询语句'
    if ';' in clean:
        return '拒绝执行：不允许多条语句'
    tables = re.findall(r'\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)',clean,re.I)
    bad = [t for t in tables if t.lower() not in ALLOWED_TABLES]
    if bad:
        return '拒绝执行，不允许查询表%s'%','.join(bad)
    if 'LIMIT' not in clean.upper():
        clean = clean+' LIMIT 50'
    try:
        with engine.connect() as conn:
            result = conn.execute(text(clean))
            keys = list(result.keys())
            rows = result.fetchall()
    except Exception as e:
        return 'SQL执行出错：%s'% e
    if not rows:
        return '查询结果为空'
    lines = ['|'.join(keys)]
    for r in rows:
        lines.append('|'.join(str(v) for v in r))
    return  '\n'.join(lines)









