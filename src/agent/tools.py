

from langchain_core.tools import tool
from src.config import TOP_K
from src.core import retriever
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














