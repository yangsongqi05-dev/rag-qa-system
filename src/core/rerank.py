import requests
from src.config import RERANK_MODEL,RERANK_URL,get_header
def rerank(question,candidates,top_k=3):
    if not candidates:
        return []
    data = {
        'model':RERANK_MODEL,
        'query':question,
        'documents':candidates,
        'top_n': min(top_k,len(candidates)),
    }
    resp = requests.post(RERANK_URL,json=data,headers=get_header())
    if resp.status_code != 200:
        raise RuntimeError(f'重排失败：{resp.status_code}{resp.text}')
    results = resp.json()['results']
    results.sort(key=lambda x:x['relevance_score'],reverse=True)
    return [(x['relevance_score'],candidates[x['index']]) for x in results]




































